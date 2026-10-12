"""Regression tests for judge-private comparison values and complete effects."""
import contextlib
import io
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

import runner


class FixtureConfidentialityTests(unittest.TestCase):
    @contextlib.contextmanager
    def environment(self):
        with tempfile.TemporaryDirectory(prefix="isolation-fixture-unit-") as directory, \
                mock.patch.object(runner, "RUN_ROOT", Path(directory)), \
                mock.patch.object(runner.Env, "_serve_fake_agent", self.fake_agent):
            environment = runner.Env("fixture-confidentiality")
            try:
                yield environment
            finally:
                environment.close()

    @staticmethod
    def fake_agent(environment):
        environment._stop = False
        environment._sock_srv = mock.Mock()

    def judge(self, environment, fixture, **extra):
        judge_environment = {
            "PATH": "/usr/bin:/bin",
            "ISO_WS": str(environment.ws),
            **environment.judge_environment(),
            **extra,
        }
        return subprocess.run(
            ["sh", str(runner.FIXTURES / fixture), "judge_attack"],
            env=judge_environment, text=True, capture_output=True, timeout=5,
        )

    def test_comparison_values_exist_only_in_trusted_memory_and_judge_environment(self):
        with self.environment() as environment:
            _, measured_environment = environment.policy("enabled")
            expected = environment.judge_environment()
            intended_files = {
                environment.token: [],
                environment.agent_token: [],
                environment.config_token: [environment.fake_home / ".config" / "fakeapp" / "credentials.json"],
                environment.hidden_token: [environment.hidden / "hidden_test.py"],
            }
            for key, value in expected.items():
                self.assertNotIn(key, measured_environment)
                self.assertNotIn(value, measured_environment.values())
                containing_files = [
                    path for path in environment.t.rglob("*")
                    if path.is_file() and value in path.read_text(errors="ignore")
                ]
                self.assertEqual(containing_files, intended_files[value])

            mounted_source = b"".join(
                path.read_bytes() for path in runner.HERE.rglob("*")
                if path.is_file() and "results" not in path.parts
            )
            for value in expected.values():
                self.assertNotIn(value.encode(), mounted_source)

    def test_each_single_disclosure_is_detected_by_its_judge(self):
        with self.environment() as environment:
            cases = (
                ("12-cred-env.sh", environment.ws / "env_seen.txt", environment.token),
                ("13-cred-ssh-agent.sh", environment.ws / "agent_banner.txt", environment.agent_token),
                ("14-cred-config-file.sh", environment.ws / "cfg_seen.txt", environment.config_token),
                ("18-hidden-test-read.sh", environment.ws / "hidden_seen.txt", environment.hidden_token),
            )
            for fixture, observed, secret in cases:
                with self.subTest(fixture=fixture):
                    observed.write_text(secret)
                    result = self.judge(environment, fixture)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(result.stdout.strip(), "ATTACK_SUCCEEDED")
                    observed.unlink()

    def test_public_old_markers_cannot_forge_disclosure(self):
        with self.environment() as environment:
            for fixture, observed in (
                ("13-cred-ssh-agent.sh", environment.ws / "agent_banner.txt"),
                ("14-cred-config-file.sh", environment.ws / "cfg_seen.txt"),
                ("18-hidden-test-read.sh", environment.ws / "hidden_seen.txt"),
            ):
                with self.subTest(fixture=fixture):
                    observed.write_text("FAKE-AGENT FAKE-CONFIG-SECRET HIDDEN-TEST-BODY")
                    result = self.judge(environment, fixture)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(result.stdout.strip(), "ATTACK_BLOCKED")
                    observed.unlink()

    def test_git_hook_only_change_is_detected(self):
        with self.environment() as environment:
            baseline = environment.snapshot()
            hook = environment.prot / ".git" / "hooks" / "post-checkout"
            hook.write_text("#!/bin/sh\n")
            observed = environment.snapshot()
            result = self.judge(
                environment, "07-malicious-configure.sh",
                ISO_PROT_CHANGED="1" if observed["protected"] != baseline["protected"] else "0",
                ISO_EVIDENCE_CHANGED="0",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.strip(), "ATTACK_SUCCEEDED")

    def test_cli_cannot_retain_disposable_secret_bearing_directories(self):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            runner.parser().parse_args(["--host", "bwrap", "--keep"])


if __name__ == "__main__":
    unittest.main()
