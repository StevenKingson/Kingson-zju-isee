"""Collect the portable executable, sources and bundled license notices."""
import importlib.metadata as metadata
import shutil
import sys
from pathlib import Path


def package(folder: Path):
    here = Path(__file__).resolve().parent
    sources = folder / "源码"
    sources.mkdir(parents=True, exist_ok=True)
    for source in here.iterdir():
        if source.is_file() and source.suffix in (".py", ".md", ".txt", ".ps1"):
            shutil.copy2(source, sources / source.name)
    shutil.copy2(here / "README.md", folder / "使用说明.md")
    notices = folder / "第三方许可证"
    notices.mkdir(exist_ok=True)
    packages = ("numpy", "cryptography", "cffi", "pycparser", "soundfile", "lameenc", "mutagen", "pyinstaller", "psutil", "charset-normalizer")
    inventory = []
    for name in packages:
        try:
            dist = metadata.distribution(name)
        except metadata.PackageNotFoundError:
            continue
        inventory.append(f"{name}=={dist.version}")
        for file in dist.files or ():
            if any(word in file.name.lower() for word in ("license", "copying", "notice", "author")):
                source = Path(dist.locate_file(file))
                if source.is_file():
                    target = notices / name / str(file).replace("..", "_")
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source, target)
    python_license = Path(sys.base_prefix) / "LICENSE.txt"
    if python_license.exists():
        shutil.copy2(python_license, notices / "Python-LICENSE.txt")
    for name in ("tcl8.6", "tk8.6"):
        license_file = Path(sys.base_prefix) / "tcl" / name / "license.terms"
        if license_file.exists():
            shutil.copy2(license_file, notices / (name + "-license.terms"))
    (notices / "组件版本.txt").write_text("\n".join(inventory) + "\n", encoding="utf-8")
    (notices / "源码获取说明.md").write_text("""# 第三方源码与版权

本程序自有源码附于“源码”目录。第三方组件的版权、许可证和源码获取位置如下；完整版本见组件版本.txt，许可证正文在对应子文件夹。

- CPython 3.11.9 / Tcl / Tk: https://www.python.org/downloads/release/python-3119/ 、https://www.tcl.tk/software/tcltk/8.6.html
- NumPy: https://github.com/numpy/numpy/tree/v2.3.3 （wheel 内的 OpenBLAS 等组件见 NumPy 附带许可证）
- cryptography: https://github.com/pyca/cryptography/tree/50.0.2 （含其 wheel 附带的 OpenSSL / Rust 组件许可）
- CFFI: https://github.com/python-cffi/cffi
- pycparser: https://github.com/eliben/pycparser
- python-soundfile: https://github.com/bastibe/python-soundfile/tree/0.14.0
- libsndfile 及其音频依赖: https://github.com/libsndfile/libsndfile （更多来源、版权见 soundfile 的 license_notes.md 和 LICENSE 文件）
- lameenc: https://github.com/chrisstaite/lameenc/tree/v1.9.0 （LGPL-3.0-or-later）
- LAME 3.100: https://sourceforge.net/projects/lame/files/lame/3.100/ （LGPL）
- Mutagen: https://github.com/quodlibet/mutagen/tree/release-1.48.1 （GPL-2.0-or-later）
- PyInstaller: https://github.com/pyinstaller/pyinstaller/tree/v6.22.3 （其 bootloader 分发例外见许可证）

源码目录含 requirements.txt 与构建命令，可修改源码并替换或重建相关库后重新打包。建议转发时保留整个分发压缩包中的源码、说明和许可证。
""", encoding="utf-8")
    return folder


if __name__ == "__main__":
    package(Path(sys.argv[1]))
