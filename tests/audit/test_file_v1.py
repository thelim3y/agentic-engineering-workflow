import concurrent.futures
import errno
import fcntl
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from uuid import UUID

from aew.audit.file_v1 import FileAuditV1
from aew.audit.v1 import AuditErrorV1
from test_v1 import event


def append_worker(path, workspace, number):
    provider = FileAuditV1(path, workspace_roots=[workspace])
    return provider.append_v1(event(str(UUID(int=number + 100)))).sequence


class FileTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.workspace = self.root / "workspace"
        self.workspace.mkdir()
        self.path = self.root / "audit"
        self.provider = FileAuditV1.create_v1(self.path, workspace_roots=[self.workspace])

    def reopen(self, **kwargs):
        return FileAuditV1(self.path, workspace_roots=[self.workspace], **kwargs)

    def append_three(self):
        for number in range(1, 4):
            self.provider.append_v1(event(str(UUID(int=number))))

    def assert_code(self, code, operation):
        with self.assertRaises(AuditErrorV1) as caught:
            operation()
        self.assertEqual(caught.exception.code, code)
        return caught.exception

    def test_durable_order_and_run_inventory_after_reopen(self):
        first = event()
        second = event(
            str(UUID(int=2)), run_id=str(UUID(int=20)), recorded_at="2025-01-01T00:00:00Z"
        )
        a = self.provider.append_v1(first)
        b = self.provider.append_v1(second)
        self.assertEqual((a.sequence, b.sequence), (1, 2))
        self.assertEqual(self.reopen().read_v1(), (first, second))
        verified = self.reopen().verify_v1()
        self.assertEqual(verified.count, 2)
        self.assertEqual(verified.head, b.digest)
        self.assertEqual(set(verified.run_ids), {a.run_id, b.run_id})

    def test_idempotent_retry_and_conflicting_identity(self):
        original = event()
        receipt = self.provider.append_v1(original)
        self.provider.append_v1(event(str(UUID(int=2))))
        self.assertEqual(self.reopen().append_v1(original), receipt)
        self.assert_code(
            "identity_conflict", lambda: self.provider.append_v1(event(details={"changed": True}))
        )
        self.assertEqual(self.provider.verify_v1().count, 2)

    def test_mutations_and_deletions_detected_by_independent_head(self):
        self.append_three()
        journal = self.path / "events.jsonl"
        original = journal.read_bytes()
        lines = original.splitlines(keepends=True)
        mutations = {
            "modification": original.replace(b"Started", b"Altered"),
            "middle deletion": lines[0] + lines[2],
            "valid suffix deletion": b"".join(lines[:2]),
            "partial truncation": original[:-10],
            "insertion": lines[0] + lines[0] + b"".join(lines[1:]),
            "duplication": original + lines[-1],
            "reordering": lines[1] + lines[0] + lines[2],
            "whole inventory deletion": b"",
        }
        for name, altered in mutations.items():
            with self.subTest(name=name):
                journal.write_bytes(altered)
                self.assert_code("integrity_error", self.reopen().verify_v1)
                self.assert_code("integrity_error", self.reopen().read_v1)
        journal.write_bytes(original)
        self.assertEqual(self.reopen().verify_v1().count, 3)

    def test_missing_journal_head_or_store_is_never_initialized_by_open(self):
        self.append_three()
        for name in ("events.jsonl", "head.json", "lock"):
            target = self.path / name
            original = target.read_bytes()
            target.unlink()
            self.assert_code("storage_missing", self.reopen().verify_v1)
            target.write_bytes(original)
            target.chmod(0o600)
        missing = self.root / "missing"
        self.assert_code(
            "storage_missing",
            lambda: FileAuditV1(missing, workspace_roots=[self.workspace]).verify_v1(),
        )
        self.assertFalse(missing.exists())

    def test_inventory_tampering_and_unsupported_storage_version(self):
        self.append_three()
        head = self.path / "head.json"
        original = json.loads(head.read_bytes())
        changed = dict(original, run_ids=[])
        head.write_text(json.dumps(changed))
        self.assert_code("integrity_error", self.reopen().verify_v1)
        head.write_text(json.dumps(dict(original, schema_version=2)))
        self.assert_code("unsupported_version", self.reopen().verify_v1)

    def test_rejects_storage_in_workspace_and_insecure_files(self):
        self.assert_code(
            "unsafe_storage",
            lambda: FileAuditV1.create_v1(
                self.workspace / "audit", workspace_roots=[self.workspace]
            ),
        )
        self.path.chmod(0o777)
        self.assert_code("unsafe_storage", self.provider.verify_v1)
        self.path.chmod(0o700)
        journal = self.path / "events.jsonl"
        journal.chmod(0o666)
        self.assert_code("unsafe_storage", self.provider.verify_v1)
        journal.chmod(0o600)
        target = self.root / "target"
        target.write_bytes(b"do not touch")
        journal.unlink()
        journal.symlink_to(target)
        self.assert_code("unsafe_storage", lambda: self.provider.append_v1(event()))
        self.assertEqual(target.read_bytes(), b"do not touch")

    def test_known_secret_values_rejected_before_any_write(self):
        before = {p.name: p.read_bytes() for p in self.path.iterdir()}
        provider = self.reopen(secret_values=["synthetic-sensitive"])
        self.assert_code(
            "secret_rejected",
            lambda: provider.append_v1(
                event(details={"message": "has synthetic-sensitive inside"})
            ),
        )
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.path.iterdir()})

    def test_concurrent_processes_serialize_without_lost_events(self):
        with concurrent.futures.ProcessPoolExecutor(max_workers=4) as pool:
            results = list(
                pool.map(append_worker, [self.path] * 16, [self.workspace] * 16, range(16))
            )
        self.assertEqual(sorted(results), list(range(1, 17)))
        self.assertEqual(len({e.to_dict()["record_id"] for e in self.provider.read_v1()}), 16)

    def test_concurrent_identical_appends_return_one_receipt(self):
        with concurrent.futures.ProcessPoolExecutor(max_workers=4) as pool:
            results = list(pool.map(append_worker, [self.path] * 8, [self.workspace] * 8, [1] * 8))
        self.assertEqual(results, [1] * 8)
        self.assertEqual(self.provider.verify_v1().count, 1)

    def test_io_failure_preserves_pending_event_and_unknown_acceptance(self):
        original = event()
        with patch(
            "aew.audit.file_v1.os.fsync", side_effect=OSError(errno.ENOSPC, "sensitive OS path")
        ):
            failure = self.assert_code("io_error", lambda: self.provider.append_v1(original))
        self.assertEqual(failure.errno, errno.ENOSPC)
        self.assertEqual(failure.acceptance, "unknown")
        self.assertEqual(failure.pending_event, original)
        self.assertIsNotNone(failure.phase)
        self.assertNotIn("sensitive", str(failure))
        self.assertEqual(self.reopen().append_v1(original).sequence, 1)

    def test_process_death_during_journal_write_retries_only_exact_event(self):
        self.provider.append_v1(event(str(UUID(int=2))))
        script = """
import os, sys
from aew.audit.file_v1 import FileAuditV1
from aew.audit.v1 import EventV1
import json
provider = FileAuditV1(sys.argv[1], workspace_roots=[sys.argv[2]])
inode = os.stat(sys.argv[1] + '/events.jsonl').st_ino
write = os.write
def interrupted(fd, data):
    if os.fstat(fd).st_ino == inode:
        write(fd, data[:len(data)//2])
        os._exit(91)
    return write(fd, data)
os.write = interrupted
provider.append_v1(EventV1(json.loads(sys.argv[3])))
"""
        result = subprocess.run(
            [
                sys.executable,
                "-B",
                "-c",
                script,
                str(self.path),
                str(self.workspace),
                event().canonical.decode(),
            ],
            check=False,
        )
        self.assertEqual(result.returncode, 91)
        self.assert_code("interrupted_append", self.reopen().verify_v1)
        self.assert_code(
            "pending_conflict", lambda: self.reopen().append_v1(event(details={"different": True}))
        )
        self.assertEqual(self.reopen().append_v1(event()).sequence, 2)
        self.assertEqual(self.reopen().verify_v1().count, 2)

    def test_short_writes_are_completed(self):
        write = os.write
        with patch("aew.audit.file_v1.os.write", side_effect=lambda fd, data: write(fd, data[:7])):
            self.provider.append_v1(event())
        self.assertEqual(self.reopen().read_v1(), (event(),))

    def test_every_flush_failure_has_safe_exact_retry(self):
        for failure_at in range(1, 6):
            with self.subTest(failure_at=failure_at):
                path = self.root / f"flush-{failure_at}"
                provider = FileAuditV1.create_v1(path, workspace_roots=[self.workspace])
                real_fsync = os.fsync
                calls = 0

                def fail_one(fd):
                    nonlocal calls
                    calls += 1
                    if calls == failure_at:
                        raise OSError(errno.EIO, "injected")
                    real_fsync(fd)

                with patch("aew.audit.file_v1.os.fsync", side_effect=fail_one):
                    failure = self.assert_code("io_error", lambda: provider.append_v1(event()))
                self.assertEqual(failure.acceptance, "unknown")
                reopened = FileAuditV1(path, workspace_roots=[self.workspace])
                self.assertEqual(reopened.append_v1(event()).sequence, 1)
                self.assertEqual(reopened.read_v1(), (event(),))

    def test_pending_retry_flushes_intent_before_touching_journal(self):
        # Simulate a rename that became visible but whose directory flush failed.
        real_fsync = os.fsync
        calls = 0

        def fail_second(fd):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError(errno.EIO, "injected")
            real_fsync(fd)

        with patch("aew.audit.file_v1.os.fsync", side_effect=fail_second):
            self.assert_code("io_error", lambda: self.provider.append_v1(event()))
        with patch(
            "aew.audit.file_v1.os.fsync", side_effect=OSError(errno.EIO, "still unavailable")
        ):
            self.assert_code("io_error", lambda: self.reopen().append_v1(event()))
        self.assertEqual((self.path / "events.jsonl").read_bytes(), b"")

    def test_lock_contention_returns_typed_busy_without_mutation(self):
        with (self.path / "lock").open("rb") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            with patch("aew.audit.file_v1.time.monotonic", side_effect=[0, 6]):
                self.assert_code("busy", lambda: self.provider.append_v1(event()))
        self.assertEqual(self.provider.verify_v1().count, 0)

    def test_readers_never_accept_partial_commit_and_corrupt_pending_is_rejected(self):
        real_replace = os.replace
        calls = 0

        def fail_final(*args, **kwargs):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError(errno.EIO, "injected")
            real_replace(*args, **kwargs)

        with patch("aew.audit.file_v1.os.replace", side_effect=fail_final):
            self.assert_code("io_error", lambda: self.provider.append_v1(event()))
        self.assert_code("interrupted_append", self.reopen().read_v1)
        journal = self.path / "events.jsonl"
        journal.write_bytes(journal.read_bytes().replace(b"Started", b"Altered"))
        self.assert_code("integrity_error", lambda: self.reopen().append_v1(event()))

    def test_joint_rollback_limit_is_demonstrated(self):
        self.provider.append_v1(event())
        saved = {name: (self.path / name).read_bytes() for name in ("events.jsonl", "head.json")}
        self.provider.append_v1(event(str(UUID(int=2))))
        (self.path / "head.json").write_bytes(saved["head.json"])
        self.assert_code("integrity_error", self.reopen().verify_v1)
        (self.path / "events.jsonl").write_bytes(saved["events.jsonl"])
        # This limitation is part of the contract: no external witness exists.
        self.assertEqual(self.reopen().verify_v1().count, 1)

    def test_invalid_configuration_never_escapes_typed_errors(self):
        for path, workspaces, secrets in (
            (None, [self.workspace], ()),
            ("bad\0path", [self.workspace], ()),
            (self.path, None, ()),
            (self.path, str(self.workspace), ()),
            (self.path, [None], ()),
            (self.path, [self.workspace], None),
            (self.path, [self.workspace], "synthetic-sensitive"),
        ):
            with self.subTest(path=path, workspaces=workspaces):
                self.assert_code(
                    "invalid_configuration",
                    lambda: FileAuditV1(path, workspace_roots=workspaces, secret_values=secrets),
                )


if __name__ == "__main__":
    unittest.main()
