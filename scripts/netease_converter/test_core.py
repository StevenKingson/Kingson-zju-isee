import tempfile
import threading
import unittest
from pathlib import Path

import numpy as np
import soundfile as sf

from core import (Cancelled, Options, convert_audio, decode_text, parse_lyrics,
                  recover_ncm, render_lyrics, run_batch, scan, verify_audio)
from core import write_tags


class LyricsTests(unittest.TestCase):
    def test_netease_metadata_and_japanese(self):
        text = '{"t":0,"c":[{"tx":"作词: "},{"tx":"Vaundy"}]}\n[00:21.41]変わりゆく景色\n'
        self.assertEqual(render_lyrics(text, "lrc"), "[00:00.000]作词: Vaundy\n[00:21.410]変わりゆく景色\n")

    def test_multitimestamp_offset_and_translation(self):
        text = '[offset:-100]\n[00:01.20][00:03.456]原文\n[00:01.20]译文\n'
        entries, _, _ = parse_lyrics(text)
        self.assertEqual([entry[0] for entry in entries], [1100, 1100, 3356])
        srt = render_lyrics(text, "srt")
        self.assertIn("00:00:01,100 --> 00:00:03,356\n原文\n译文", srt)

    def test_yrc(self):
        yrc = '[2000,1200](2000,500,0)你好(2500,700,0)世界'
        self.assertEqual(render_lyrics(yrc, "lrc"), '[00:02.000]你好世界\n')
        self.assertIn('00:00:02,000 --> 00:00:03,200', render_lyrics(yrc, "srt"))

    def test_json_translated_sections(self):
        import json
        text = json.dumps({"lrc": {"lyric": "[00:01]hello"}, "tlyric": {"lyric": "[00:01]你好"}})
        self.assertEqual(render_lyrics(text, "txt"), "hello\n你好\n")

    def test_untimed_text_cannot_invent_timestamps(self):
        self.assertEqual(render_lyrics("hello", "txt"), "hello\n")
        with self.assertRaises(ValueError):
            render_lyrics("hello", "lrc")

    def test_text_encodings_and_binary_rejection(self):
        self.assertEqual(decode_text("歌词".encode("utf-16")), "歌词")
        self.assertEqual(decode_text("歌词".encode("gb18030")), "歌词")
        with self.assertRaises(ValueError):
            decode_text(b"\x00\x00encrypted")


class BatchTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_recursive_preserves_structure_excludes_output_and_does_not_overwrite(self):
        source = self.root / "输入"
        source.mkdir()
        nested = source / "日本語"
        nested.mkdir()
        (nested / "song.lrc").write_text("[00:01.25]歌詞", encoding="utf-8")
        output = source / "已转换"
        options = Options(source, output, lyrics=("lrc", "srt", "txt"))
        result = run_batch(options, threading.Event())
        self.assertEqual(len(result["results"]), 3)
        self.assertEqual(len(scan(options)), 1)
        self.assertTrue((output / "日本語/song.srt").exists())
        result = run_batch(options, threading.Event())
        self.assertTrue(all(row["status"] == "skipped" for row in result["results"]))

    def test_corrupt_ncm_fails_and_next_file_continues(self):
        source = self.root / "source"
        source.mkdir()
        (source / "bad.ncm").write_bytes(b"bad ncm!")
        (source / "good.lrc").write_text("[00:01]hello", encoding="utf-8")
        result = run_batch(Options(source, self.root / "output"), threading.Event())
        self.assertEqual([row["status"] for row in result["results"]], ["error", "success"])
        self.assertFalse(list((self.root / "output").glob(".ncm-work-*")))

    def test_cancel_does_not_publish_partial_audio(self):
        source = self.root / "input.wav"
        sf.write(source, np.zeros((96000, 2)), 48000)
        target = self.root / "output.mp3"
        cancel = threading.Event()
        cancel.set()
        with self.assertRaises(Cancelled):
            convert_audio(source, target, "mp3", 320, cancel)
        self.assertFalse(target.exists())

    def test_all_audio_formats_and_no_overwrite(self):
        source = self.root / "tone.flac"
        samples = 0.2 * np.sin(np.arange(48000) * 2 * np.pi * 440 / 48000)
        sf.write(source, np.column_stack([samples, samples]), 48000, subtype="PCM_24")
        event = threading.Event()
        for kind in ("flac", "wav", "mp3"):
            target = self.root / "转换" / ("tone." + kind)
            convert_audio(source, target, kind, 320, event)
            info = verify_audio(target, event)
            self.assertLess(abs(info["duration"] - 1), 0.1)
            digest = target.read_bytes()
            self.assertTrue(convert_audio(source, target, kind, 320, event).startswith("跳过"))
            self.assertEqual(target.read_bytes(), digest)

    def test_mp3_large_embedded_cover_does_not_extend_audio(self):
        source = self.root / "tone.wav"
        sf.write(source, np.zeros((48000, 2)), 48000)
        event = threading.Event()
        mp3 = self.root / "cover.mp3"
        convert_audio(source, mp3, "mp3", 320, event)
        write_tags(mp3, "mp3", {"musicName": "日本語"}, b"\xff\xd8" + b"x" * 800000)
        self.assertLess(abs(verify_audio(mp3, event)["duration"] - 1), 0.1)
        wave = self.root / "after-cover.wav"
        convert_audio(mp3, wave, "wav", 320, event)
        self.assertLess(abs(verify_audio(wave, event)["duration"] - 1), 0.1)


if __name__ == "__main__":
    unittest.main()
