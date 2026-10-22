"""Exercise upload behavior with real disposable local Git repositories."""
import importlib.util
import io
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("website_upload", ROOT / "scripts/upload-github.py")
uploader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(uploader)
GIT = shutil.which("git")


class UploadIntegrationTests(unittest.TestCase):
    def setUp(self):
        output = (ROOT / "output").resolve()
        output.mkdir(exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(prefix="upload-test-", dir=output)
        self.base = Path(self.temporary.name).resolve()
        # Validate the cleanup target before registering recursive cleanup.
        assert self.base.is_relative_to(output) and self.base != output
        self.addCleanup(self.temporary.cleanup)
        self.remote = self.base / "remote.git"
        self.work = self.base / "website"
        self.git(self.base, "init", "--bare", "--initial-branch=main", str(self.remote))
        self.git(self.base, "init", "--initial-branch=main", str(self.work))
        self.identity(self.work)
        (self.work / ".gitignore").write_text("site/\noutput/\n", encoding="utf-8")
        (self.work / "old.md").write_text("Original note\n", encoding="utf-8")
        self.git(self.work, "add", ".")
        self.git(self.work, "commit", "-m", "Initial content")
        self.git(self.work, "remote", "add", "origin", str(self.remote))
        self.git(self.work, "push", "-u", "origin", "main")
        self.publisher = uploader.Publisher(self.work,
            uploader.Reporter(io.StringIO(), quiet=True), expected_remote=str(self.remote))

    def git(self, cwd, *arguments, check=True):
        return subprocess.run([GIT, *arguments], cwd=cwd, check=check,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8", errors="replace")

    def identity(self, path):
        self.git(path, "config", "user.name", "Upload integration test")
        self.git(path, "config", "user.email", "test@example.invalid")

    def remote_head(self):
        return self.git(self.base, "--git-dir", str(self.remote), "rev-parse", "main").stdout.strip()

    def local_head(self):
        return self.git(self.work, "rev-parse", "HEAD").stdout.strip()

    def test_uploads_additions_and_deletions_but_respects_gitignore(self):
        self.publisher.verify_repository()
        (self.work / "new.md").write_text("新的课程心得\n", encoding="utf-8")
        (self.work / "old.md").unlink()
        (self.work / "site").mkdir()
        (self.work / "site/index.html").write_text("Generated file", encoding="utf-8")
        self.assertTrue(self.publisher.publish_changes())
        files = self.git(self.base, "--git-dir", str(self.remote), "ls-tree", "-r", "--name-only", "main").stdout.splitlines()
        self.assertIn("new.md", files)
        self.assertNotIn("old.md", files)
        self.assertNotIn("site/index.html", files)
        self.assertEqual(self.local_head(), self.remote_head())

    def test_retry_pushes_existing_commit_after_rejected_push(self):
        hook = self.remote / "hooks/pre-receive"
        hook.write_bytes(b"#!/bin/sh\nexit 1\n")
        hook.chmod(0o755)
        original = self.local_head()
        (self.work / "new.md").write_text("A new note", encoding="utf-8")
        with self.assertRaises(uploader.UploadError):
            self.publisher.publish_changes()
        saved_commit = self.local_head()
        self.assertNotEqual(original, saved_commit)
        self.assertEqual(original, self.remote_head())
        hook.unlink()
        self.assertTrue(self.publisher.publish_changes())
        self.assertEqual(saved_commit, self.local_head())
        self.assertEqual(saved_commit, self.remote_head())

    def test_remote_updates_stop_before_staging_and_preserve_local_edits(self):
        other = self.base / "other"
        self.git(self.base, "clone", str(self.remote), str(other))
        self.identity(other)
        (other / "remote-note.md").write_text("Edited on another computer", encoding="utf-8")
        self.git(other, "add", ".")
        self.git(other, "commit", "-m", "Remote change")
        self.git(other, "push", "origin", "main")
        old_head = self.local_head()
        (self.work / "my-note.md").write_text("My unfinished work", encoding="utf-8")
        with self.assertRaisesRegex(uploader.UploadError, "本机尚未包含"):
            self.publisher.publish_changes()
        self.assertEqual(old_head, self.local_head())
        self.assertEqual("My unfinished work", (self.work / "my-note.md").read_text(encoding="utf-8"))
        self.assertEqual("", self.git(self.work, "diff", "--cached", "--name-only").stdout)

    def test_no_changes_does_not_create_empty_commit(self):
        head = self.local_head()
        self.assertFalse(self.publisher.publish_changes())
        self.assertEqual(head, self.local_head())

    def test_wrong_remote_and_wrong_branch_are_rejected(self):
        self.git(self.work, "remote", "set-url", "origin", "https://example.invalid/other.git")
        with self.assertRaisesRegex(uploader.UploadError, "推送地址"):
            self.publisher.verify_repository()
        self.git(self.work, "remote", "set-url", "origin", str(self.remote))
        self.git(self.work, "switch", "-c", "draft")
        with self.assertRaisesRegex(uploader.UploadError, "当前分支"):
            self.publisher.verify_repository()


if __name__ == "__main__":
    unittest.main(verbosity=2)
