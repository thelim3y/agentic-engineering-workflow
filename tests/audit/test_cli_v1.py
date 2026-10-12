import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class CliTests(unittest.TestCase):
    def test_observation_command_produces_persists_and_reads_event(self):
        with tempfile.TemporaryDirectory() as root:
            command = [
                sys.executable,
                "-B",
                "-m",
                "aew.audit",
                "v1",
                "--store",
                root + "/audit",
                "--workspace",
                root + "/work",
            ]

            def run(*args):
                return subprocess.run(
                    command + list(args), text=True, capture_output=True, check=False
                )

            self.assertEqual(run("init").returncode, 0)
            observe = [
                "observe",
                "--record-id",
                "00000000-0000-4000-8000-000000000001",
                "--run-id",
                "00000000-0000-4000-8000-000000000010",
                "--recorded-at",
                "2026-10-12T09:00:00Z",
                "--project",
                "sample",
                "--task",
                "task-1",
                "--name",
                "sample.started",
                "--message",
                "Started",
            ]
            result = run(*observe)
            self.assertEqual(result.returncode, 0, result.stderr)
            receipt = json.loads(result.stdout)
            self.assertEqual(receipt["sequence"], 1)
            self.assertEqual(json.loads(run(*observe).stdout), receipt)
            records = json.loads(run("read").stdout)
            self.assertEqual(records[0]["record_type"], "observation.recorded")
            self.assertEqual(records[0]["details"]["name"], "sample.started")
            self.assertEqual(json.loads(run("verify").stdout)["count"], 1)
            failed = run(*observe[:-1], "Bearer synthetic-sensitive")
            self.assertEqual(failed.returncode, 1)
            self.assertEqual(json.loads(failed.stderr)["code"], "secret_rejected")
            self.assertNotIn("synthetic-sensitive", failed.stderr)
            Path(root + "/audit/events.jsonl").unlink()
            failure = run(*observe)
            self.assertEqual(failure.returncode, 1)
            self.assertEqual(
                json.loads(failure.stderr)["choices"], ["retry", "abort", "audit-degraded"]
            )

    def test_unknown_api_version_is_typed(self):
        result = subprocess.run(
            [sys.executable, "-B", "-m", "aew.audit", "v2"], text=True, capture_output=True
        )
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stderr)["code"], "unsupported_version")

    def test_symlink_loop_returns_safe_typed_error(self):
        with tempfile.TemporaryDirectory() as root:
            loop = Path(root) / "synthetic-sensitive-loop"
            loop.symlink_to(loop)
            for store, workspace in ((root + "/audit", str(loop)), (str(loop), root + "/work")):
                result = subprocess.run(
                    [
                        sys.executable,
                        "-B",
                        "-m",
                        "aew.audit",
                        "v1",
                        "--store",
                        store,
                        "--workspace",
                        workspace,
                        "verify",
                    ],
                    text=True,
                    capture_output=True,
                )
                self.assertEqual(result.returncode, 1)
                self.assertIn(
                    json.loads(result.stderr)["code"], ("invalid_configuration", "unsafe_storage")
                )
                self.assertNotIn("synthetic-sensitive", result.stderr)


if __name__ == "__main__":
    unittest.main()
