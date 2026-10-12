"""Single-host POSIX file audit. See docs/audit-v1.md for the trust boundary."""

from contextlib import contextmanager
import errno
import fcntl
import hashlib
import json
import os
from pathlib import Path
import stat
import time
from uuid import uuid4

from .events_v1 import AuditErrorV1, EventV1, ReceiptV1, VerificationV1, canonical_json


_ZERO = "0" * 64
_FLAGS = os.O_CLOEXEC | os.O_NOFOLLOW


def _fail(code, message):
    raise AuditErrorV1(code, message)


def _integrity():
    _fail(
        "integrity_error",
        "Audit history or accepted head is inconsistent; preserve storage for inspection.",
    )


def _digest(data):
    return hashlib.sha256(data).hexdigest()


def _write_all(fd, data):
    remaining = memoryview(data)
    while remaining:
        count = os.write(fd, remaining)
        if count == 0:
            raise OSError(errno.EIO, "No write progress")
        remaining = remaining[count:]


def _io_error(error, context):
    code = {
        errno.ENOENT: "storage_missing",
        errno.EACCES: "permission_denied",
        errno.EPERM: "permission_denied",
        errno.ELOOP: "unsafe_storage",
        errno.EEXIST: "already_exists",
    }.get(error.errno, "io_error")
    return AuditErrorV1(
        code,
        "Audit storage operation failed; inspect phase and errno before choosing retry, abort or degraded continuation.",
        acceptance="unknown" if context.get("writing") else "not_attempted",
        phase=context["phase"],
        errno=error.errno,
        pending_event=context.get("event"),
    )


class FileAuditV1:
    """Trusted callers only. OS isolation must deny agents this directory and process.

    Opening never creates or repairs storage. Creation is explicit. All operations
    lock and verify; only a byte-identical pending append can complete a torn write.
    """

    def __init__(self, path, *, workspace_roots, secret_values=()):
        try:
            if isinstance(workspace_roots, (str, bytes, os.PathLike)) or isinstance(
                secret_values, (str, bytes)
            ):
                raise ValueError
            self.path = Path(os.path.abspath(self._path_text(path)))
            self.workspaces = tuple(
                Path(self._path_text(root)).resolve() for root in workspace_roots
            )
            self.secret_values = tuple(secret_values)
        except (ValueError, TypeError, RuntimeError, OSError):
            raise AuditErrorV1(
                "invalid_configuration", "Invalid storage, workspace or secret configuration."
            ) from None
        if not self.workspaces or any(type(s) is not str or not s for s in self.secret_values):
            _fail(
                "invalid_configuration", "Declare agent workspace roots and nonempty secret values."
            )
        for workspace in self.workspaces:
            if self.path.is_relative_to(workspace) or workspace.is_relative_to(self.path):
                _fail("unsafe_storage", "Audit storage and agent workspaces must be separate.")

    @staticmethod
    def _path_text(path):
        value = os.fspath(path)
        if type(value) is not str or not value or "\0" in value:
            raise ValueError
        return value

    def _check_location(self):
        # No symlink component, including one above the store. Non-sticky writable
        # ancestors would allow another OS user to replace the directory.
        try:
            resolved = self.path.resolve()
        except (ValueError, RuntimeError):
            raise AuditErrorV1(
                "unsafe_storage", "Audit storage path cannot be resolved safely."
            ) from None
        if resolved != self.path:
            _fail("unsafe_storage", "Audit storage cannot use symlink paths.")
        # A user namespace may map the host's root owner to an overflow UID.
        trusted_owners = {os.geteuid(), Path("/").stat().st_uid}
        for parent in self.path.parents:
            info = parent.stat()
            if info.st_uid not in trusted_owners or (
                info.st_mode & 0o022 and not info.st_mode & stat.S_ISVTX
            ):
                _fail("unsafe_storage", "Audit storage requires trusted parent directories.")

    @staticmethod
    def _check_owner(fd, *, directory=False):
        info = os.fstat(fd)
        expected = stat.S_ISDIR if directory else stat.S_ISREG
        if (
            not expected(info.st_mode)
            or info.st_uid != os.geteuid()
            or stat.S_IMODE(info.st_mode) != (0o700 if directory else 0o600)
            or (not directory and info.st_nlink != 1)
        ):
            _fail(
                "unsafe_storage",
                "Audit storage requires private owned directories and unlinked regular files.",
            )

    @classmethod
    def create_v1(cls, path, *, workspace_roots, secret_values=()):
        provider = cls(path, workspace_roots=workspace_roots, secret_values=secret_values)
        context = {"phase": "create"}
        try:
            provider._check_location()
            os.mkdir(provider.path, 0o700)
            with provider._directory() as directory:
                for name in ("lock", "events.jsonl"):
                    fd = os.open(
                        name, _FLAGS | os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600, dir_fd=directory
                    )
                    try:
                        os.fsync(fd)
                    finally:
                        os.close(fd)
                provider._publish_head(
                    directory,
                    {
                        "schema_version": 1,
                        "count": 0,
                        "byte_count": 0,
                        "head": _ZERO,
                        "run_ids": [],
                        "pending": None,
                    },
                )
            parent = os.open(provider.path.parent, _FLAGS | os.O_RDONLY | os.O_DIRECTORY)
            try:
                os.fsync(parent)
            finally:
                os.close(parent)
        except OSError as error:
            raise _io_error(error, context) from None
        return provider

    @contextmanager
    def _directory(self):
        self._check_location()
        fd = os.open(self.path, _FLAGS | os.O_RDONLY | os.O_DIRECTORY)
        try:
            self._check_owner(fd, directory=True)
            yield fd
        finally:
            os.close(fd)

    @contextmanager
    def _file(self, directory, name, flags=os.O_RDONLY):
        fd = os.open(name, _FLAGS | flags | os.O_NONBLOCK, dir_fd=directory)
        try:
            self._check_owner(fd)
            yield fd
        finally:
            os.close(fd)

    @contextmanager
    def _session(self, context):
        try:
            with self._directory() as directory, self._file(directory, "lock") as lock:
                deadline = time.monotonic() + 5
                while True:
                    try:
                        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                        break
                    except BlockingIOError:
                        if time.monotonic() >= deadline:
                            _fail("busy", "Audit writer is busy; retry the same event later.")
                        time.sleep(0.01)
                try:
                    yield directory
                finally:
                    fcntl.flock(lock, fcntl.LOCK_UN)
        except OSError as error:
            raise _io_error(error, context) from None

    def _read_file(self, directory, name):
        with self._file(directory, name) as fd, os.fdopen(os.dup(fd), "rb") as stream:
            return stream.read()

    def _publish_head(self, directory, head):
        name = ".head-" + uuid4().hex
        fd = os.open(name, _FLAGS | os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600, dir_fd=directory)
        try:
            _write_all(fd, canonical_json(head) + b"\n")
            os.fsync(fd)
        finally:
            os.close(fd)
            # Failed or killed writes may leave temporary heads. They are never
            # authoritative; no automatic repair or selection by modification time.
        os.replace(name, "head.json", src_dir_fd=directory, dst_dir_fd=directory)
        os.fsync(directory)

    def _snapshot(self, directory):
        try:
            head = json.loads(self._read_file(directory, "head.json"))
            if type(head) is not dict:
                _integrity()
            if type(head.get("schema_version")) is not int or head["schema_version"] != 1:
                _fail("unsupported_version", "Only file audit format v1 is supported.")
            if set(head) != {"schema_version", "count", "byte_count", "head", "run_ids", "pending"}:
                _integrity()
            if any(type(head[k]) is not int or head[k] < 0 for k in ("count", "byte_count")):
                _integrity()
            data = self._read_file(directory, "events.jsonl")
            if len(data) < head["byte_count"]:
                _integrity()
            accepted, tail = data[: head["byte_count"]], data[head["byte_count"] :]
            events, receipts, seen, runs = [], [], set(), set()
            previous = _ZERO
            lines = accepted.splitlines(keepends=True)
            for sequence, line in enumerate(lines, 1):
                row = json.loads(line)
                if type(row) is not dict or set(row) != {"sequence", "previous", "event", "digest"}:
                    _integrity()
                if (
                    type(row["sequence"]) is not int
                    or row["sequence"] != sequence
                    or row["previous"] != previous
                ):
                    _integrity()
                digest = row.pop("digest")
                if digest != _digest(canonical_json(row)):
                    _integrity()
                row["digest"] = digest
                if canonical_json(row) + b"\n" != line:
                    _integrity()
                item = EventV1(row["event"])
                record_id, run_id = row["event"]["record_id"], row["event"]["run_id"]
                if record_id in seen:
                    _integrity()
                seen.add(record_id)
                runs.add(run_id)
                events.append(item)
                receipts.append(ReceiptV1(sequence, record_id, run_id, digest))
                previous = digest
            if (
                head["count"] != len(events)
                or head["head"] != previous
                or head["run_ids"] != sorted(runs)
            ):
                _integrity()
            pending = head["pending"]
            if pending is None:
                if tail:
                    _integrity()
            else:
                if (
                    type(pending) is not dict
                    or set(pending) != {"line_sha256", "size"}
                    or type(pending["size"]) is not int
                    or not 0 < pending["size"] <= 70000
                    or type(pending["line_sha256"]) is not str
                    or len(pending["line_sha256"]) != 64
                    or len(tail) > pending["size"]
                ):
                    _integrity()
                if len(tail) == pending["size"] and _digest(tail) != pending["line_sha256"]:
                    _integrity()
            return head, tuple(events), tuple(receipts), tail
        except (ValueError, TypeError, KeyError, UnicodeError, RecursionError):
            _integrity()
        except AuditErrorV1 as error:
            if error.code in {"invalid_event", "secret_rejected"}:
                _integrity()
            raise

    def append_v1(self, event):
        if not isinstance(event, EventV1):
            _fail("invalid_event", "append_v1 requires an EventV1.")
        event.reject_secrets(self.secret_values)
        context = {"phase": "verify", "event": event}
        with self._session(context) as directory:
            head, events, receipts, tail = self._snapshot(directory)
            record = event.to_dict()
            for existing, receipt in zip(events, receipts):
                if receipt.record_id == record["record_id"]:
                    if existing != event:
                        _fail(
                            "identity_conflict",
                            "Event identity already has different accepted content.",
                        )
                    # Reconfirm durability even after an earlier ambiguous fsync.
                    context.update(phase="confirm_duplicate", writing=True)
                    for name in ("events.jsonl", "head.json"):
                        with self._file(directory, name) as fd:
                            os.fsync(fd)
                    os.fsync(directory)
                    return receipt
            row = {"sequence": head["count"] + 1, "previous": head["head"], "event": record}
            digest = _digest(canonical_json(row))
            row["digest"] = digest
            line = canonical_json(row) + b"\n"
            pending = {"line_sha256": _digest(line), "size": len(line)}
            if head["pending"] is not None:
                if head["pending"] != pending:
                    _fail(
                        "pending_conflict",
                        "Retry the exact pending event before appending another event.",
                    )
                if not line.startswith(tail):
                    _integrity()
            context.update(phase="publish_intent", writing=True)
            if head["pending"] is None:
                self._publish_head(directory, dict(head, pending=pending))
            else:
                # A previous rename may be visible even when its directory fsync
                # failed. Make that intent durable before any recovery write.
                with self._file(directory, "head.json") as fd:
                    os.fsync(fd)
                os.fsync(directory)
            context["phase"] = "write_event"
            with self._file(directory, "events.jsonl", os.O_WRONLY | os.O_APPEND) as fd:
                _write_all(fd, line[len(tail) :])
                os.fsync(fd)
            context["phase"] = "accept_event"
            self._publish_head(
                directory,
                {
                    "schema_version": 1,
                    "count": row["sequence"],
                    "byte_count": head["byte_count"] + len(line),
                    "head": digest,
                    "run_ids": sorted(set(head["run_ids"]) | {record["run_id"]}),
                    "pending": None,
                },
            )
            return ReceiptV1(row["sequence"], record["record_id"], record["run_id"], digest)

    def _accepted(self):
        with self._session({"phase": "verify"}) as directory:
            head, events, _, _ = self._snapshot(directory)
            if head["pending"] is not None:
                raise AuditErrorV1(
                    "interrupted_append",
                    "An unaccepted append is pending; retry its exact event.",
                    acceptance="unknown",
                    phase="verify",
                )
            return head, events

    def read_v1(self):
        """Return a fully verified ordered snapshot, never an unchecked prefix."""
        return self._accepted()[1]

    def verify_v1(self):
        head, _ = self._accepted()
        return VerificationV1(head["count"], head["head"], tuple(head["run_ids"]))
