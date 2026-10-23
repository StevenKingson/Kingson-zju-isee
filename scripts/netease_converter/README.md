# 云音乐本地转换工具

独立的 Windows 桌面程序，离线批量恢复本地 `.ncm` 音频并整理时间轴歌词。无需登录，不请求网络，不修改原文件。支持 Windows 10/11 x64；其他系统和 ARM64 原生运行未验证。

## 使用

双击 `云音乐本地转换工具.exe`。选择读取、保存文件夹，选择 MP3 / FLAC / WAV，可同时勾选 LRC / SRT / TXT 歌词，然后点击“扫描文件”或“开始批量转换”。保存位置默认是读取目录下的“已转换”文件夹。支持子文件夹，保留相对目录；已存在的目标文件自动跳过，单个文件失败不影响后续任务。

原 NCM 包含什么编码，就先恢复为什么编码。输出格式相同时直接保留音频数据；原 MP3 导出 MP3 不重新压缩，码率设置仅影响重新编码的 MP3。FLAC / WAV 不会提升原始 MP3 的音质。新编码 MP3 可选 128 / 192 / 256 / 320kbps，采样率为 44.1kHz 或 48kHz。FLAC / WAV 保持输入采样率，写入 16bit 或 24bit PCM。FLAC / MP3 写入可用的标题、歌手、专辑和内嵌封面，WAV 主要保存音频。

## 歌词

- 推荐 **LRC**：UTF-8、保留时间轴，适合网页或音乐播放器。
- **SRT**：UTF-8 BOM 字幕，适合视频编辑；同时间戳的原文和译文合并为双语字幕。普通 LRC 最后一行默认显示 5 秒。
- **TXT**：UTF-8 纯文本，删除时间标记。
- 输入支持 `.lrc`、`.yrc`、`.lyric` 和 `.lyric.json`。JSON 支持网易云歌词接口常见的 `lrc` / `tlyric` / `romalrc` / `yrc` 字段。
- 网易云 LRC 开头的 JSON 作者信息会转成普通时间轴文本。YRC 的逐字时间信息在导出 LRC / SRT 时降为逐行时间轴。无时间轴文本只能导出 TXT。
- **当前样本的 LRC 没有加密**。程序不声称支持未知加密歌词、KRC / QRC、UC 缓存或新版未知 NCM；这些会报告失败，需要真实样本才能适配。
- NCM 通常不内含歌词。程序只处理已有的本地歌词，不从网络获取缺失歌词，也不会凭空生成翻译。

每批会在输出目录生成 JSON 转换记录。支持中途取消，临时音频会清理；已经完成的文件保留。音频会全程解码校验，带 PCM MD5 的 FLAC 还会核对 MD5。大文件校验和 MP3 编码需要一定时间。

## 源码运行与打包

需要 Python 3.11 x64，包含 Tkinter。

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python app.py
.\.venv\Scripts\python -m unittest -v test_core.py
.\.venv\Scripts\python -m PyInstaller --noconfirm --clean --onefile --windowed --name 云音乐本地转换工具 --collect-all _soundfile_data --exclude-module matplotlib --exclude-module scipy --exclude-module pandas --exclude-module PIL --exclude-module pytest --exclude-module IPython app.py
```

`dist/云音乐本地转换工具.exe` 为单文件版，其他电脑不需安装 Python 或 FFmpeg。单文件程序启动时会把依赖解压到系统临时目录，首次启动可能需要数秒。

命令行批量用法（EXE 也支持）：

```powershell
python app.py --input "D:\音乐" --output "D:\导出" --audio mp3 --bitrate 320 --lyrics lrc srt txt --recursive
```

`--no-audio` 仅处理歌词，`--lyrics` 后留空则不处理歌词；`--include-audio` 同时转换已有 MP3 / FLAC / WAV。窗口版 EXE 不显示控制台输出，可查看保存目录里的转换记录。

## 第三方组件

NCM 容器处理参考 [taurusxin/ncmdump](https://github.com/taurusxin/ncmdump) 的公开格式实现。运行时使用 Python、Tk/Tcl、NumPy、cryptography、CFFI、libsndfile / python-soundfile、LAME / lameenc、Mutagen，打包器为 PyInstaller。分发包附有第三方许可证和源码获取说明；二进制程序没有数字签名。
