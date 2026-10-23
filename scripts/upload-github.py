"""Check, commit and upload this website. No force push or automatic merge."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
import os
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
REMOTE = "https://github.com/StevenKingson/Kingson-zju-isee.git"
WEBSITE = "https://stevenkingson.github.io/Kingson-zju-isee/"
ACTIONS = "https://github.com/StevenKingson/Kingson-zju-isee/actions"
CHINA_TIME = timezone(timedelta(hours=8))


class UploadError(Exception):
    pass


class Reporter:
    def __init__(self, stream, quiet=False):
        self.stream = stream
        self.quiet = quiet

    def say(self, message=""):
        if not self.quiet:
            print(message, flush=True)
        self.stream.write(message + "\n")
        self.stream.flush()


def canonical_remote(value):
    value = value.rstrip("/")
    if value.startswith("git@github.com:"):
        value = "https://github.com/" + value.split(":", 1)[1]
    if "://" not in value:
        return Path(value).resolve().as_posix().casefold()
    return value.removesuffix(".git").casefold()


class Publisher:
    def __init__(self, root, reporter, expected_remote=REMOTE):
        self.root = Path(root).resolve()
        self.reporter = reporter
        self.expected_remote = expected_remote
        self.git = shutil.which("git")
        if not self.git:
            raise UploadError("没有找到 Git。请按操作指南中的“没有 Git”步骤安装后重试。")
        self.env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUTF8="1", NO_MKDOCS_2_WARNING="1")

    def capture(self, arguments, allowed=(0,)):
        result = subprocess.run([self.git, *arguments], cwd=self.root, env=self.env,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8", errors="replace")
        if result.returncode not in allowed:
            self.reporter.say(result.stderr.strip())
            raise UploadError("Git 检查失败。请查看上方错误，或把本次日志发给我。")
        return result

    def run(self, description, arguments):
        self.reporter.say("  · " + description)
        with subprocess.Popen([str(a) for a in arguments], cwd=self.root, env=self.env,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
            encoding="utf-8", errors="replace") as process:
            for line in process.stdout:
                self.reporter.say(line.rstrip())
            code = process.wait()
        if code:
            raise UploadError(f"“{description}”未完成（退出码 {code}）。请查看上方具体原因。")

    def verify_repository(self):
        top = self.capture(["rev-parse", "--show-toplevel"]).stdout.strip()
        if Path(top).resolve() != self.root:
            raise UploadError("请把上传程序放在网站项目根目录，与 mkdocs.yml 放在一起。")
        branch = self.capture(["branch", "--show-current"]).stdout.strip()
        if branch != "main":
            raise UploadError(f"当前分支是 {branch or '游离状态'}，需要在 main 分支上传。请先完成当前分支的工作。")
        remote = self.capture(["remote", "get-url", "--push", "origin"]).stdout.strip()
        if canonical_remote(remote) != canonical_remote(self.expected_remote):
            raise UploadError("origin 的推送地址与本网站仓库不符，已停止。请先核对仓库地址。")
        for marker in ("MERGE_HEAD", "CHERRY_PICK_HEAD", "REVERT_HEAD", "rebase-merge", "rebase-apply"):
            path = Path(self.capture(["rev-parse", "--git-path", marker]).stdout.strip())
            if not path.is_absolute():
                path = self.root / path
            if path.exists():
                raise UploadError("Git 中有尚未完成的合并或变基，请先处理完再上传。")
        for field in ("user.name", "user.email"):
            if not self.capture(["config", "--get", field], allowed=(0, 1)).stdout.strip():
                raise UploadError("Git 尚未配置提交姓名或邮箱，请按操作指南设置提交身份。")
        result = self.capture(["ls-files", "--cached", "--others", "--exclude-standard", "-z"])
        for name in set(result.stdout.split("\0")) - {""}:
            path = self.root / name
            if path.is_file() and path.stat().st_size > 100 * 1024 * 1024:
                raise UploadError(f"单个文件超过 GitHub 普通上传限制（100 MiB）：{name}。请先压缩或拆分此文件。")

    def prepare_environment(self):
        python = self.root / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        if not python.exists():
            self.run("创建网站专用 Python 环境", [sys.executable, "-m", "venv", ".venv"])
        self.run("检查并补齐网站依赖", [python, "-m", "pip", "install", "--quiet", "--disable-pip-version-check", "-r", "requirements.txt"])
        return python

    def build(self, python):
        self.env["SITE_URL"] = WEBSITE
        self.run("更新画集目录", [python, "scripts/update-gallery.py"])
        self.run("更新 BGM 曲库", [python, "scripts/update-music.py"])
        self.run("更新追番目录", [python, "scripts/update-watchlist.py"])
        self.run("生成可双击阅读的操作指南", [python, "scripts/build-guide.py"])
        self.run("检查并构建网站", [python, "-m", "mkdocs", "build", "--strict"])

    def publish_changes(self):
        # Fetch first: stop before staging or committing if GitHub has new work.
        self.run("检查 GitHub 上是否有其他更新", [self.git, "fetch", "origin", "main"])
        ancestor = self.capture(["merge-base", "--is-ancestor", "origin/main", "HEAD"], allowed=(0, 1))
        if ancestor.returncode:
            raise UploadError("GitHub 上有本机尚未包含的提交，已停止。请先同步这些更新；程序不会覆盖远程内容。")
        self.run("保存本次新增、修改和删除", [self.git, "add", "--all", "--", "."])
        changes = self.capture(["diff", "--cached", "--quiet"], allowed=(0, 1))
        if changes.returncode:
            stamp = datetime.now(CHINA_TIME).strftime("%Y-%m-%d %H:%M:%S")
            self.run("创建本机版本记录", [self.git, "commit", "--quiet", "-m", "更新网站内容 " + stamp])
        else:
            self.reporter.say("没有新的文件改动，继续检查是否有上次尚未上传的提交。")
        ahead = int(self.capture(["rev-list", "--count", "origin/main..HEAD"]).stdout.strip())
        if not ahead:
            self.reporter.say("本机内容与 GitHub 一致，无需重复上传。")
            return False
        self.run(f"上传 {ahead} 个提交到 GitHub", [self.git, "push", "origin", "main"])
        return True


@contextmanager
def upload_lock(path):
    with path.open("a+b") as stream:
        stream.seek(0, 2)
        if stream.tell() == 0:
            stream.write(b"0")
            stream.flush()
        stream.seek(0)
        try:
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            raise UploadError("另一个上传窗口正在运行，请等待它结束后再试。") from None
        # Closing the handle releases the lock, even after a failed upload.
        yield


def main():
    parser = argparse.ArgumentParser(description="检查并上传 KING桑的个人网站")
    parser.add_argument("--check-only", action="store_true", help="只更新目录并构建检查，不提交或推送")
    args = parser.parse_args()
    output = ROOT / "output"
    output.mkdir(exist_ok=True)
    stamp = datetime.now(CHINA_TIME).strftime("%Y%m%d-%H%M%S-%f")
    log_path = output / f"upload-{stamp}.log"
    with log_path.open("w", encoding="utf-8") as stream:
        reporter = Reporter(stream)
        try:
            with upload_lock(output / "upload.lock"):
                reporter.say("KING桑の放课后茶会 · 一键上传")
                reporter.say("[1/4] 检查项目、仓库和文件大小")
                publisher = Publisher(ROOT, reporter)
                publisher.verify_repository()
                reporter.say("[2/4] 检查网站运行环境")
                python = publisher.prepare_environment()
                reporter.say("[3/4] 更新素材目录并检查网站")
                publisher.build(python)
                if args.check_only:
                    reporter.say("检查通过。本次没有提交或推送；画集、曲库和指南的生成文件已刷新。")
                    return 0
                reporter.say("[4/4] 保存版本并上传")
                uploaded = publisher.publish_changes()
                if uploaded:
                    reporter.say("上传成功！网站更新还需要等待 GitHub Actions 完成，通常需要几分钟。")
                reporter.say("部署进度：" + ACTIONS)
                reporter.say("网站地址：" + WEBSITE)
                return 0
        except (UploadError, OSError) as error:
            reporter.say("\n未完成：" + str(error))
            reporter.say("已有文件和本机提交均保留。修正问题后可以重新双击上传，未上传的提交会继续推送。")
            reporter.say("本次日志：" + str(log_path))
            return 1
        except KeyboardInterrupt:
            reporter.say("\n操作已取消，已有文件和提交仍然保留。")
            return 130


if __name__ == "__main__":
    sys.exit(main())
