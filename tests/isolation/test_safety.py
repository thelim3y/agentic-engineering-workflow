"""Safe regression tests: no attack suite, external network or model invocation."""
import contextlib
import io
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import runner


class NetworkJudgeTests(unittest.TestCase):
    def judge(self, status, curl_rc=0, phase="judge_attack"):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            if status is not None:
                (root / "http_code.txt").write_text(str(status))
                (root / "curl_rc.txt").write_text(str(curl_rc))
            return subprocess.run(
                ["sh", str(runner.FIXTURES / "15-net-egress.sh"), phase],
                env={"PATH": "/usr/bin:/bin", "ISO_WS": directory},
                text=True, capture_output=True, timeout=5,
            ).stdout.strip()

    def test_any_authenticated_destination_response_proves_egress(self):
        for status in (200, 301, 403, 404, 500):
            with self.subTest(status=status):
                self.assertEqual(self.judge(status), "ATTACK_SUCCEEDED")
                self.assertEqual(self.judge(status, phase="judge_positive"), "POSITIVE_OK")

    def test_proxy_denial_is_not_destination_response(self):
        self.assertEqual(self.judge("000", curl_rc=56), "ATTACK_BLOCKED")

    def test_response_with_transfer_error_is_not_claimed_blocked(self):
        for status in (200, 403):
            self.assertEqual(self.judge(status, curl_rc=56), "INDETERMINATE")

    def test_missing_or_malformed_network_observations_are_not_blocked(self):
        for status, rc in ((None, 0), ("garbage", 0), ("garbage", 7), (0, 0), (200, "garbage")):
            with self.subTest(status=status, rc=rc):
                self.assertEqual(self.judge(status, rc), "INDETERMINATE")

    def test_curl_startup_failure_is_not_network_prevention(self):
        self.assertEqual(self.judge(0, 127), "INDETERMINATE")


class SafetyLauncherTests(unittest.TestCase):
    def test_existing_log_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bwrap.log"
            path.write_text("historical evidence")
            with self.assertRaises(FileExistsError):
                runner.Log(path)
            self.assertEqual(path.read_text(), "historical evidence")

    def test_inherited_credentials_are_not_forwarded(self):
        with patch.dict(os.environ, {"REAL_SECRET": "synthetic-sentinel", "SSH_AUTH_SOCK": "/fake/socket"}):
            clean = runner.child_environment()
        self.assertNotIn("REAL_SECRET", clean)
        self.assertNotIn("SSH_AUTH_SOCK", clean)
        self.assertNotIn("HOME", clean)

    def test_outer_sandbox_is_allowlisted_not_a_root_bind(self):
        with tempfile.TemporaryDirectory() as output:
            cmd = runner.sandbox_command("bwrap", Path(output), [])
        self.assertIn("--clearenv", cmd)
        self.assertIn("--unshare-pid", cmd)
        mounts = [tuple(cmd[i+1:i+3]) for i, value in enumerate(cmd) if value in ("--ro-bind", "--bind")]
        self.assertNotIn(("/", "/"), mounts)
        self.assertFalse(any(source == str(Path.home()) for source, _ in mounts))
        self.assertIn((str(runner.HERE), "/suite"), mounts)

    def test_unavailable_outer_sandbox_does_not_start_suite(self):
        with patch.object(runner.shutil, "which", return_value=None), \
             patch.object(runner, "run_suite") as suite, \
             patch("sys.argv", ["runner.py", "--host", "bwrap"]), \
             contextlib.redirect_stderr(io.StringIO()):
            self.assertNotEqual(runner.main(), 0)
        suite.assert_not_called()

    def test_native_build_inputs_are_read_only(self):
        with patch.object(Path, "exists", return_value=True):
            cmd = runner.sandbox_command("bwrap", Path("/tmp/results"), [])
        read_only = [tuple(cmd[i+1:i+3]) for i, value in enumerate(cmd) if value == "--ro-bind"]
        writable = [tuple(cmd[i+1:i+3]) for i, value in enumerate(cmd) if value == "--bind"]
        for path in ("/usr/include", "/usr/libexec"):
            self.assertIn((path, path), read_only)
        self.assertEqual(writable, [("/tmp/results", "/results")])


if __name__ == "__main__":
    unittest.main()
