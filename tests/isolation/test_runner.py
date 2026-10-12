"""Trusted runner regressions; never execute attack fixtures or real adapters.

Run with: python3 -B -m unittest discover -s tests/isolation -p 'test_*.py'
"""
import contextlib
import importlib.util
import io
import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock


SPEC = importlib.util.spec_from_file_location("isolation_runner", Path(__file__).with_name("runner.py"))
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)


def phase(verdict, **changes):
    result = {
        "rc": 0, "verdict": verdict, "judge_rc": 0, "started": True,
        "timed_out": False, "drain_complete": True, "cancelled": False,
        "survivors": [], "descendants_verified": True, "unsupported": False,
        "output_truncated": False, "output_prefix": "",
    }
    result.update(changes)
    return result


class ProtectedSnapshotTests(unittest.TestCase):
    def test_snapshot_changes_with_content_and_metadata(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            item = root / "input.txt"
            item.write_text("first")
            initial = runner.tree_digest(root)
            item.write_text("second")
            content_changed = runner.tree_digest(root)
            item.chmod(0o400)
            metadata_changed = runner.tree_digest(root)
        self.assertNotEqual(initial, content_changed)
        self.assertNotEqual(content_changed, metadata_changed)

    def test_unreadable_input_fails_snapshot(self):
        with tempfile.TemporaryDirectory() as directory:
            item = Path(directory) / "input.txt"
            item.write_text("protected")
            real_open = os.open

            def deny_target(path, flags, *args, **kwargs):
                if os.fspath(path) == os.fspath(item):
                    raise PermissionError("synthetic unreadable input")
                return real_open(path, flags, *args, **kwargs)

            with mock.patch.object(runner.os, "open", side_effect=deny_target):
                with self.assertRaisesRegex(RuntimeError, "cannot snapshot"):
                    runner.tree_digest(Path(directory))

    @unittest.skipUnless(hasattr(os, "mkfifo"), "requires POSIX fifo support")
    def test_unsupported_input_type_fails_snapshot(self):
        with tempfile.TemporaryDirectory() as directory:
            os.mkfifo(Path(directory) / "unexpected.fifo")
            with self.assertRaisesRegex(RuntimeError, "unsupported input type"):
                runner.tree_digest(Path(directory))

    def test_input_changing_between_passes_fails_snapshot(self):
        with mock.patch.object(runner, "_tree_manifest", side_effect=[b"first", b"second"]):
            with self.assertRaisesRegex(RuntimeError, "changed while being snapshotted"):
                runner.tree_digest(Path("unused"))


class FixtureVerdictTests(unittest.TestCase):
    def run_fixture(self, phases, name="01-direct-file-tool"):
        subject = runner.Runner.__new__(runner.Runner)
        subject.host = "fake"
        subject.rows = []
        subject.log = mock.Mock()
        subject.cleanup = mock.Mock()
        subject.run_phase = mock.Mock(side_effect=phases)
        with mock.patch.object(runner, "Env"):
            return subject.run_fixture(Path(name + ".sh"))

    def attack(self, enabled=None, disabled=None, positive=None, name="01-direct-file-tool"):
        return self.run_fixture([
            disabled if disabled is not None else phase("ATTACK_SUCCEEDED"),
            enabled if enabled is not None else phase("ATTACK_BLOCKED"),
            positive if positive is not None else phase("POSITIVE_OK"),
        ], name)

    def assertNotPassing(self, row):
        self.assertNotIn(row["verdict"], {"blocked", "held"}, row)

    def test_exact_blocked_verdict_and_valid_controls_pass(self):
        self.assertEqual(self.attack()["verdict"], "blocked")

    def test_snapshot_or_phase_exception_is_untested(self):
        subject = runner.Runner.__new__(runner.Runner)
        subject.host = "fake"
        subject.rows = []
        subject.log = mock.Mock()
        subject.cleanup = mock.Mock()
        subject.run_phase = mock.Mock(side_effect=RuntimeError("snapshot failed"))
        with mock.patch.object(runner, "Env"):
            row = subject.run_fixture(Path("01-direct-edit.sh"))
        self.assertEqual(row["verdict"], "untested")

    def test_denied_attack_may_exit_nonzero_after_starting(self):
        self.assertEqual(self.attack(enabled=phase("ATTACK_BLOCKED", rc=1))["verdict"], "blocked")

    def test_missing_or_unknown_enabled_judge_never_passes(self):
        for verdict in ("NO_VERDICT", "", "something unexpected"):
            with self.subTest(verdict=verdict):
                self.assertNotPassing(self.attack(enabled=phase(verdict)))

    def test_nonzero_judge_exit_never_passes_any_control(self):
        for label, verdict in (("disabled", "ATTACK_SUCCEEDED"), ("enabled", "ATTACK_BLOCKED"), ("positive", "POSITIVE_OK")):
            with self.subTest(control=label):
                self.assertNotPassing(self.attack(**{label: phase(verdict, judge_rc=2)}))

    def test_startup_failure_is_not_successful_prevention(self):
        for fields in ({"rc": 127, "started": False}, {"rc": 127}, {"rc": 126}, {"started": False}):
            with self.subTest(fields=fields):
                self.assertNotPassing(self.attack(enabled=phase("ATTACK_BLOCKED", **fields)))

    def test_missing_phase_evidence_never_defaults_to_success(self):
        for key in ("judge_rc", "started", "drain_complete", "output_truncated",
                    "descendants_verified", "timed_out"):
            with self.subTest(field=key):
                enabled = phase("ATTACK_BLOCKED")
                del enabled[key]
                self.assertNotPassing(self.attack(enabled=enabled))

    def test_timeout_or_incomplete_drain_never_passes(self):
        for fields in ({"timed_out": True}, {"drain_complete": False},
                       {"output_truncated": True}):
            with self.subTest(fields=fields):
                self.assertNotPassing(self.attack(enabled=phase("ATTACK_BLOCKED", **fields)))

    def test_surviving_or_unverified_descendants_never_pass(self):
        for fields in ({"survivors": [12345]}, {"descendants_verified": False}):
            with self.subTest(fields=fields):
                self.assertNotPassing(self.attack(enabled=phase("ATTACK_BLOCKED", **fields)))

    def test_cancellation_requires_cancellation_to_have_occurred(self):
        self.assertNotPassing(self.attack(
            disabled=phase("ATTACK_SUCCEEDED", cancelled=True, rc=-9),
            enabled=phase("ATTACK_BLOCKED", cancelled=False), name="16-cancellation"))

    def test_confirmed_cancellation_with_no_survivors_passes(self):
        self.assertEqual(self.attack(
            disabled=phase("ATTACK_SUCCEEDED", cancelled=True, rc=-9),
            enabled=phase("ATTACK_BLOCKED", cancelled=True, rc=-9),
            name="16-cancellation")["verdict"], "blocked")

    def test_unsupported_config_requires_an_exact_successful_judge(self):
        for verdict, judge_rc in (("NO_VERDICT", 0), ("CONTRACT_HELD", 2), ("CONTRACT_VIOLATED", 0)):
            with self.subTest(verdict=verdict, judge_rc=judge_rc):
                result = phase(verdict, rc=64, unsupported=True, started=False, judge_rc=judge_rc)
                self.assertNotPassing(self.run_fixture([result] * 4, "20-unsupported-config"))

    def test_valid_unsupported_config_rejection_passes(self):
        result = phase("CONTRACT_HELD", rc=64, unsupported=True, started=False)
        self.assertEqual(self.run_fixture([result] * 4, "20-unsupported-config")["verdict"], "held")

    def test_failure_propagation_rejects_untrusted_judge(self):
        results = [phase("NO_VERDICT", rc=23), phase("NO_VERDICT", rc=23), phase("NO_VERDICT")]
        self.assertNotPassing(self.run_fixture(results, "21-failure-propagation"))

    def test_failure_propagation_rejects_failed_judge(self):
        results = [phase("EXIT_CODE_IS_JUDGED_BY_RUNNER", rc=rc, judge_rc=2) for rc in (23, 23, 0)]
        self.assertNotPassing(self.run_fixture(results, "21-failure-propagation"))

    def test_expected_failure_exit_codes_and_valid_judges_pass(self):
        results = [phase("EXIT_CODE_IS_JUDGED_BY_RUNNER", rc=rc) for rc in (23, 23, 0)]
        self.assertEqual(self.run_fixture(results, "21-failure-propagation")["verdict"], "held")


class CliExitTests(unittest.TestCase):
    def invoke(self, verdicts, filters=()):
        # All file writes are confined to a fresh trusted temp directory.
        # No Runner constructor, Env constructor, adapter or fixture is run.
        with tempfile.TemporaryDirectory(prefix="isolation-unit-") as directory:
            root = Path(directory)
            fixtures = root / "fixtures"
            fixtures.mkdir()
            (root / "results").mkdir()
            for index in range(len(verdicts)):
                (fixtures / f"{index:02d}-fake.sh").touch()
            subject = mock.Mock()
            subject.info = {}
            subject.rows = []
            verdict_iterator = iter(verdicts)

            def record(fixture):
                row = {"fixture": fixture.stem, "verdict": next(verdict_iterator)}
                subject.rows.append(row)
                return row

            subject.run_fixture.side_effect = record
            arguments = SimpleNamespace(host="fake", fixture=list(filters), results_dir=root / "results")
            with mock.patch.object(runner, "HERE", root), mock.patch.object(runner, "FIXTURES", fixtures), \
                    mock.patch.object(runner, "Runner", return_value=subject), \
                    contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                try:
                    code = runner.run_suite(arguments)
                except SystemExit as exc:
                    code = exc.code
            return 0 if code is None else code

    def test_all_passing_rows_exit_zero(self):
        self.assertEqual(self.invoke(["blocked", "held"]), 0)

    def test_any_nonpassing_row_exits_nonzero(self):
        for verdict in ("allowed", "untested", "unsupported", "invalid-fixture", "too-strict", "violated"):
            with self.subTest(verdict=verdict):
                self.assertNotEqual(self.invoke(["blocked", verdict]), 0)

    def test_no_matching_fixtures_exits_nonzero(self):
        self.assertNotEqual(self.invoke(["blocked"], filters=["does-not-exist"]), 0)

    def test_empty_suite_exits_nonzero(self):
        self.assertNotEqual(self.invoke([]), 0)


if __name__ == "__main__":
    unittest.main()
