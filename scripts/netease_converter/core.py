"""Offline NCM audio recovery and timed lyric conversion. No network access."""
from __future__ import annotations

import base64
import hashlib
import io
import json
import os
import re
import shutil
import tempfile
import threading
from dataclasses import dataclass
from contextlib import contextmanager
from pathlib import Path
from typing import Callable

import lameenc
import numpy as np
import soundfile as sf
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from mutagen.flac import FLAC, Picture
from mutagen.id3 import APIC, ID3, TALB, TIT2, TPE1


class Cancelled(Exception):
    pass


class AudioRegion(io.RawIOBase):
    """Expose audio without a leading ID3 tag to libsndfile's MP3 decoder.

    Large embedded covers otherwise inflate libsndfile's estimated duration.
    This view avoids loading an entire music file into memory.
    """
    def __init__(self, file, start, end):
        self.file, self.start, self.end = file, start, end
        self.seek(0)

    def readable(self):
        return True

    def seekable(self):
        return True

    def tell(self):
        return self.file.tell() - self.start

    def seek(self, offset, whence=0):
        position = offset if whence == 0 else self.tell() + offset if whence == 1 else self.end - self.start + offset
        if position < 0:
            raise ValueError("音频 seek 越界")
        self.file.seek(self.start + position)
        return position

    def read(self, size=-1):
        available = max(0, self.end - self.file.tell())
        return self.file.read(available if size < 0 else min(size, available))

    def readinto(self, buffer):
        data = self.read(len(buffer))
        buffer[:len(data)] = data
        return len(data)


@contextmanager
def open_audio(path: Path):
    with path.open("rb") as raw:
        header = raw.read(42)
        start, end = 0, path.stat().st_size
        is_mp3 = header.startswith(b"ID3") or (len(header) > 1 and header[0] == 255 and header[1] & 224 == 224)
        if header.startswith(b"ID3"):
            start = 10 + sum((header[6 + i] & 127) << (7 * (3 - i)) for i in range(4))
            if header[3] == 4 and header[5] & 16:
                start += 10
        if is_mp3 and end >= 128:
            raw.seek(-128, 2)
            if raw.read(3) == b"TAG":
                end -= 128
        with sf.SoundFile(AudioRegion(raw, start, end)) as audio:
            yield audio


def check_cancel(event: threading.Event):
    if event.is_set():
        raise Cancelled("已取消")


def aes_decode(data: bytes, key: bytes) -> bytes:
    if not data or len(data) % 16:
        raise ValueError("NCM 密钥或元数据长度无效")
    decryptor = Cipher(algorithms.AES(key), modes.ECB()).decryptor()
    plain = decryptor.update(data) + decryptor.finalize()
    pad = plain[-1]
    if not 1 <= pad <= 16 or plain[-pad:] != bytes([pad]) * pad:
        raise ValueError("不支持的 NCM 加密版本或文件损坏")
    return plain[:-pad]


def recover_ncm(source: Path, destination: Path, cancel: threading.Event):
    """Recover embedded audio; return metadata, cover bytes, detected extension."""
    with source.open("rb") as stream:
        def take(count):
            if count < 0 or count > 32 * 1024 * 1024:
                raise ValueError("NCM 头部长度异常")
            data = stream.read(count)
            if len(data) != count:
                raise ValueError("NCM 文件不完整")
            return data

        def number():
            return int.from_bytes(take(4), "little")

        if take(8) != b"CTENFDAM":
            raise ValueError("不是支持的 NCM 文件（文件头不匹配）")
        take(2)
        encrypted_key = bytes(value ^ 0x64 for value in take(number()))
        key_data = aes_decode(encrypted_key, bytes.fromhex("687a4852416d736f356b496e62617857"))
        if not key_data.startswith(b"neteasecloudmusic") or len(key_data) <= 17:
            raise ValueError("不支持的 NCM 密钥结构")
        key = key_data[17:]
        box = list(range(256))
        previous = 0
        for i in range(256):
            previous = (previous + box[i] + key[i % len(key)]) & 255
            box[i], box[previous] = box[previous], box[i]
        pattern = bytes(box[(box[j] + box[(box[j] + j) & 255]) & 255]
                        for j in list(range(1, 256)) + [0])
        metadata = {}
        encrypted_meta = take(number())
        if encrypted_meta:
            try:
                text = bytes(value ^ 0x63 for value in encrypted_meta)
                raw = aes_decode(base64.b64decode(text[22:]),
                                 bytes.fromhex("2331346c6a6b5f215c5d2630553c2728"))
                metadata = json.loads(raw.split(b":", 1)[1])
                if not isinstance(metadata, dict):
                    metadata = {}
            except (ValueError, IndexError, UnicodeError):
                # Audio recovery is independent of optional album information.
                metadata = {}
        take(5)
        cover_capacity, cover_length = number(), number()
        if cover_length > cover_capacity:
            raise ValueError("NCM 封面区长度无效")
        cover = take(cover_length)
        take(cover_capacity - cover_length)
        extension = None
        with destination.open("wb") as out:
            offset = 0
            while data := stream.read(1024 * 1024):
                check_cancel(cancel)
                # Chunk size is a multiple of the 256-byte NCM keystream.
                view = np.frombuffer(data, dtype=np.uint8)
                mask = np.frombuffer(pattern, dtype=np.uint8)
                decoded = np.bitwise_xor(view, np.resize(mask, len(view))).tobytes()
                if offset == 0:
                    if decoded.startswith(b"fLaC"):
                        extension = "flac"
                    elif decoded.startswith(b"ID3") or (len(decoded) > 1 and
                            decoded[0] == 255 and decoded[1] & 224 == 224):
                        extension = "mp3"
                    else:
                        raise ValueError("解密后音频头不受支持，可能是新版加密格式")
                out.write(decoded)
                offset += len(data)
        if not extension:
            raise ValueError("NCM 中没有音频数据")
        return metadata, cover, extension


def verify_audio(path: Path, cancel: threading.Event):
    """Decode every frame and verify FLAC PCM MD5 when available."""
    with path.open("rb") as stream:
        header = stream.read(42)
    is_flac = header.startswith(b"fLaC")
    bits = ((int.from_bytes(header[18:26], "big") >> 36) & 31) + 1 if is_flac else 16
    checksum = hashlib.md5()
    frames = 0
    with open_audio(path) as audio:
        rate, channels = audio.samplerate, audio.channels
        for block in audio.blocks(blocksize=65536, dtype="int32", always_2d=True):
            check_cancel(cancel)
            frames += len(block)
            if is_flac:
                if bits not in (8, 16, 24, 32):
                    raise ValueError(f"暂不支持 {bits}bit FLAC 校验")
                packed = np.ascontiguousarray(block.astype("<i4")).view(np.uint8).reshape(-1, 4)
                checksum.update(packed[:, 4 - bits // 8:].tobytes())
    if frames == 0:
        raise ValueError("音频为空")
    if is_flac and any(header[26:42]) and checksum.digest() != header[26:42]:
        raise ValueError("FLAC 音频 MD5 校验失败，文件可能损坏")
    return {"duration": frames / rate, "sample_rate": rate, "channels": channels,
            "bits": bits, "flac_md5": is_flac and any(header[26:42])}


def write_tags(path: Path, kind: str, metadata: dict, cover: bytes):
    if kind == "wav":
        return
    title = str(metadata.get("musicName", ""))
    album = str(metadata.get("album", ""))
    artists = [str(item[0]) for item in metadata.get("artist", []) if isinstance(item, list) and item]
    if kind == "flac":
        audio = FLAC(path)
        if title:
            audio["title"] = title
        if album:
            audio["album"] = album
        if artists:
            audio["artist"] = artists
        if cover and not audio.pictures:
            picture = Picture()
            picture.type, picture.mime, picture.data = 3, ("image/png" if cover.startswith(b"\x89PNG") else "image/jpeg"), cover
            audio.add_picture(picture)
        audio.save()
    else:
        try:
            tags = ID3(path)
        except Exception:
            tags = ID3()
        if title:
            tags.add(TIT2(encoding=3, text=title))
        if album:
            tags.add(TALB(encoding=3, text=album))
        if artists:
            tags.add(TPE1(encoding=3, text=artists))
        if cover and not tags.getall("APIC"):
            tags.add(APIC(encoding=3, mime="image/png" if cover.startswith(b"\x89PNG") else "image/jpeg", type=3, data=cover))
        tags.save(path, v2_version=3)


def publish(temp: Path, target: Path):
    """Atomic, no-overwrite publication on NTFS and other hard-link filesystems."""
    try:
        os.link(temp, target)
    except FileExistsError:
        raise
    except OSError:
        # Fallback for USB/network drives without hard links.
        created = False
        try:
            with target.open("xb") as out, temp.open("rb") as src:
                created = True
                shutil.copyfileobj(src, out)
        except Exception:
            if created:
                target.unlink(missing_ok=True)
            raise


def convert_audio(source: Path, target: Path, kind: str, bitrate: int,
                  cancel: threading.Event, progress: Callable[[float], None] = lambda _: None):
    if target.exists():
        return "跳过：目标文件已存在"
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".ncm-work-", dir=target.parent) as work:
        work = Path(work)
        metadata, cover = {}, b""
        recovered = source
        input_kind = source.suffix.lower().lstrip(".")
        if input_kind == "ncm":
            recovered = work / "recovered.audio"
            metadata, cover, input_kind = recover_ncm(source, recovered, cancel)
        original = verify_audio(recovered, cancel)
        result = work / ("result." + kind)
        if input_kind == kind:
            shutil.copyfile(recovered, result)
        elif kind == "mp3":
            encoder = lameenc.Encoder()
            encoder.set_bit_rate(bitrate)
            encoder.set_in_sample_rate(original["sample_rate"])
            encoder.set_out_sample_rate(48000 if original["sample_rate"] % 48000 == 0 else 44100)
            encoder.set_channels(original["channels"])
            encoder.set_quality(2)
            with open_audio(recovered) as audio, result.open("wb") as out:
                done = 0
                for block in audio.blocks(blocksize=65536, dtype="int16", always_2d=True):
                    check_cancel(cancel)
                    out.write(encoder.encode(block.tobytes()))
                    done += len(block)
                    progress(done / len(audio))
                out.write(encoder.flush())
        else:
            subtype = "PCM_24" if original["bits"] > 16 else "PCM_16"
            # Avoid integer overflow/quantization when writing decoded samples.
            with open_audio(recovered) as audio, sf.SoundFile(
                result, "w", samplerate=audio.samplerate, channels=audio.channels,
                subtype=subtype, format=kind.upper()
            ) as out:
                done = 0
                for block in audio.blocks(blocksize=65536, dtype="int32", always_2d=True):
                    check_cancel(cancel)
                    out.write(block)
                    done += len(block)
                    progress(done / len(audio))
        write_tags(result, kind, metadata, cover)
        validated = verify_audio(result, cancel)
        if abs(validated["duration"] - original["duration"]) > 1.0:
            raise ValueError("输出音频时长校验失败")
        check_cancel(cancel)
        publish(result, target)
        seconds = int(original["duration"])
        note = "；原 MP3 直接恢复，未重编码" if input_kind == kind == "mp3" else ""
        return f"完成：{kind.upper()} · {seconds // 60}:{seconds % 60:02d} · 已完整解码校验{note}"


STAMP = re.compile(r"\[(\d+):(\d{1,2})(?:[.:](\d{1,3}))?\]")
YRC = re.compile(r"^\[(\d+),(\d+)\](.*)$")


def decode_text(data: bytes):
    if data.startswith((b"\xff\xfe", b"\xfe\xff")):
        return data.decode("utf-16")
    for encoding in ("utf-8-sig", "gb18030"):
        try:
            text = data.decode(encoding)
            if "\x00" not in text:
                return text
        except UnicodeError:
            pass
    raise ValueError("歌词不是可识别的文本，可能已加密；需要对应格式样本才能支持")


def parse_lyrics(text: str):
    text = text.strip()
    if not text:
        raise ValueError("歌词文件为空")
    if text.startswith("{"):
        try:
            obj = json.loads(text)
        except json.JSONDecodeError:
            obj = None  # NetEase metadata JSON lines followed by LRC.
        if isinstance(obj, dict):
            sections = []
            for name in ("lrc", "tlyric", "romalrc", "yrc"):
                value = obj.get(name)
                if isinstance(value, dict):
                    value = value.get("lyric", "")
                if isinstance(value, str) and value:
                    sections.append(value)
            if not sections and isinstance(obj.get("lyric"), str):
                sections.append(obj["lyric"])
            if not sections:
                raise ValueError("JSON 中未找到 lrc / tlyric / romalrc / yrc 歌词")
            text = "\n".join(sections)
    entries, plain, headers = [], [], []
    offset_match = re.search(r"\[offset:([+-]?\d+)\]", text, re.I)
    offset = int(offset_match[1]) if offset_match else 0
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("{"):
            try:
                item = json.loads(line)
                content = "".join(str(part.get("tx", "")) for part in item.get("c", []))
                if content:
                    entries.append((max(0, int(item.get("t", 0)) + offset), None, content))
                continue
            except (ValueError, TypeError, AttributeError):
                raise ValueError("无法识别的 JSON 歌词行")
        if match := YRC.match(line):
            content = re.sub(r"\(\d+,\d+(?:,\d+)?\)", "", match[3]).strip()
            if content:
                entries.append((max(0, int(match[1]) + offset), int(match[2]), content))
            continue
        stamps = list(STAMP.finditer(line))
        if stamps:
            content = STAMP.sub("", line).strip()
            for match in stamps:
                milliseconds = int((match[3] or "0").ljust(3, "0"))
                start = (int(match[1]) * 60 + int(match[2])) * 1000 + milliseconds + offset
                entries.append((max(0, start), None, content))
        elif re.match(r"\[(ar|ti|al|by|re|ve):.*\]$", line, re.I):
            headers.append(line)
        elif not re.match(r"\[(offset|length):.*\]$", line, re.I):
            plain.append(line)
    # Stable ordering retains original/translated lines sharing a timestamp.
    entries = list(dict.fromkeys(sorted(entries, key=lambda x: x[0])))
    if not entries and not plain:
        raise ValueError("未找到歌词正文")
    if entries and plain:
        raise ValueError("文件混合了无法定位时间的正文；请先整理为标准 LRC 或 TXT")
    return entries, plain, list(dict.fromkeys(headers))


def render_lyrics(text: str, kind: str):
    entries, plain, headers = parse_lyrics(text)
    if kind == "txt":
        return "\n".join(plain or [entry[2] for entry in entries if entry[2]]) + "\n"
    if not entries:
        raise ValueError("没有时间轴，无法导出 LRC/SRT；请选择 TXT")
    if kind == "lrc":
        lines = headers[:]
        for start, _, content in entries:
            minutes, rest = divmod(start, 60000)
            lines.append(f"[{minutes:02d}:{rest // 1000:02d}.{rest % 1000:03d}]{content}")
        return "\n".join(lines) + "\n"
    if kind != "srt":
        raise ValueError("不支持的歌词输出格式")
    groups = {}
    for start, length, content in entries:
        if content:
            groups.setdefault(start, []).append((length, content))
    starts = sorted(groups)
    def stamp(ms):
        hours, rest = divmod(ms, 3600000)
        minutes, rest = divmod(rest, 60000)
        return f"{hours:02d}:{minutes:02d}:{rest // 1000:02d},{rest % 1000:03d}"
    blocks = []
    for i, start in enumerate(starts):
        lengths = [length for length, _ in groups[start] if length is not None]
        end = start + max(lengths) if lengths else (starts[i + 1] if i + 1 < len(starts) else start + 5000)
        if i + 1 < len(starts):
            end = min(end, starts[i + 1])
        content = "\n".join(item[1] for item in groups[start])
        blocks.append(f"{i + 1}\n{stamp(start)} --> {stamp(max(start + 1, end))}\n{content}")
    return "\n\n".join(blocks) + "\n"


@dataclass
class Options:
    source: Path
    output: Path
    audio: str = "mp3"
    bitrate: int = 320
    lyrics: tuple[str, ...] = ("lrc",)
    recursive: bool = True
    include_audio: bool = False
    audio_enabled: bool = True

    def __post_init__(self):
        self.source = self.source.expanduser().resolve()
        self.output = self.output.expanduser().resolve()


def scan(options: Options):
    source, output = options.source.resolve(), options.output.resolve()
    if not source.is_dir():
        raise ValueError("请选择有效的读取文件夹")
    if source == output:
        raise ValueError("保存文件夹应与读取文件夹不同，建议使用“已转换”子文件夹")
    if options.audio not in ("mp3", "flac", "wav") or options.bitrate not in (128, 192, 256, 320):
        raise ValueError("不支持的音频参数")
    if any(item not in ("lrc", "srt", "txt") for item in options.lyrics):
        raise ValueError("不支持的歌词参数")
    files = source.rglob("*") if options.recursive else source.iterdir()
    tasks = []
    for file in files:
        if not file.is_file() or output in file.resolve().parents:
            continue
        ext = file.suffix.lower()
        if options.audio_enabled and (ext == ".ncm" or (options.include_audio and ext in (".mp3", ".flac", ".wav"))):
            tasks.append(("audio", file))
        elif options.lyrics and (ext in (".lrc", ".yrc", ".lyric") or file.name.lower().endswith(".lyric.json")):
            tasks.append(("lyrics", file))
    return sorted(tasks, key=lambda item: str(item[1]).casefold())


def run_batch(options: Options, cancel: threading.Event, notify=lambda *args: None):
    tasks = scan(options)
    if not tasks:
        raise ValueError("没有找到可处理的 NCM 或歌词文件；普通音频需勾选相应选项")
    options.output.mkdir(parents=True, exist_ok=True)
    report = []
    for index, (task, file) in enumerate(tasks):
        if cancel.is_set():
            break
        relative = file.relative_to(options.source)
        notify("start", index, len(tasks), str(relative))
        try:
            if task == "audio":
                target = (options.output / relative).with_suffix("." + options.audio)
                message = convert_audio(file, target, options.audio, options.bitrate, cancel,
                                        lambda value: notify("progress", index, len(tasks), value))
                records = [(target, message)]
            else:
                text = decode_text(file.read_bytes())
                records = []
                for kind in options.lyrics:
                    check_cancel(cancel)
                    name = relative.name[:-11] if relative.name.lower().endswith(".lyric.json") else relative.stem
                    target = options.output / relative.parent / (name + "." + kind)
                    if target.exists():
                        records.append((target, "跳过：目标文件已存在"))
                        continue
                    result = render_lyrics(text, kind)
                    target.parent.mkdir(parents=True, exist_ok=True)
                    fd, temp_name = tempfile.mkstemp(prefix=".lyrics-", dir=target.parent)
                    temp = Path(temp_name)
                    try:
                        with os.fdopen(fd, "w", encoding="utf-8-sig" if kind == "srt" else "utf-8", newline="\n") as out:
                            out.write(result)
                        publish(temp, target)
                    finally:
                        temp.unlink(missing_ok=True)
                    records.append((target, f"完成：{kind.upper()} 歌词"))
            for target, message in records:
                status = "skipped" if message.startswith("跳过") else "success"
                report.append({"input": str(file), "output": str(target), "status": status, "message": message})
                notify("result", index, len(tasks), report[-1])
        except Cancelled:
            break
        except Exception as error:
            report.append({"input": str(file), "status": "error", "message": str(error)})
            notify("result", index, len(tasks), report[-1])
        notify("progress", index, len(tasks), 1.0)
    return {"cancelled": cancel.is_set(), "tasks": len(tasks), "results": report}
