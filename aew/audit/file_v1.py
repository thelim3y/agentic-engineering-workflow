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
_HEAD_FIELDS = set("schema_version count byte_count head run_ids pending".split())
_ROW_FIELDS = set("sequence previous event digest".split())


def _fail(code, message):
    raise AuditErrorV1(code, message)


def _integrity():
    _fail(
        "integrity_error",
        "Audit history or accepted head is inconsistent; preserve storage for inspection.",
    )


def _require_integrity(condition):
    if not condition:
        _integrity()


def _digest(data):
    return hashlib.sha256(data).hexdigest()


def _write_all(fd, data):
    remaining = memoryview(data)
    while remaining:
        count = os.write(fd, remaining)
        if count == 0:
            raise OSError(errno.EIO, "No write progress")
        remaining = remaining[count:]


@contextmanager
def _close_fd(fd):
    try:
        yield fd
    finally:
        os.close(fd)


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
        # Reject symlink components and replaceable non-sticky ancestors.
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
                    with _close_fd(fd):
                        os.fsync(fd)
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
            with _close_fd(
                os.open(provider.path.parent, _FLAGS | os.O_RDONLY | os.O_DIRECTORY)
            ) as parent:
                os.fsync(parent)
        except OSError as error:
            raise _io_error(error, context) from None
        return provider

    @contextmanager
    def _directory(self):
        self._check_location()
        with _close_fd(os.open(self.path, _FLAGS | os.O_RDONLY | os.O_DIRECTORY)) as fd:
            self._check_owner(fd, directory=True)
            yield fd

    @contextmanager
    def _file(self, directory, name, flags=os.O_RDONLY):
        with _close_fd(os.open(name, _FLAGS | flags | os.O_NONBLOCK, dir_fd=directory)) as fd:
            self._check_owner(fd)
            yield fd

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

    def _fsync_file(self, directory, name, flags=os.O_RDONLY):
        with self._file(directory, name, flags) as fd:
            os.fsync(fd)

    def _publish_head(self, directory, head):
        name = ".head-" + uuid4().hex
        flags = _FLAGS | os.O_WRONLY | os.O_CREAT | os.O_EXCL
        with _close_fd(os.open(name, flags, 0o600, dir_fd=directory)) as fd:
            _write_all(fd, canonical_json(head) + b"\n")
            os.fsync(fd)
        # Failed writes may leave temporary heads. They are never authoritative.
        os.replace(name, "head.json", src_dir_fd=directory, dst_dir_fd=directory)
        os.fsync(directory)

    def _read_head(self, directory):
        head = json.loads(self._read_file(directory, "head.json"))
        _require_integrity(type(head) is dict)
        if type(head.get("schema_version")) is not int or head["schema_version"] != 1:
            _fail("unsupported_version", "Only file audit format v1 is supported.")
        _require_integrity(set(head) == _HEAD_FIELDS)
        _require_integrity(
            all(type(head[name]) is int and head[name] >= 0 for name in ("count", "byte_count"))
        )
        return head

    @staticmethod
    def _decode_row(line, sequence, previous):
        row = json.loads(line)
        _require_integrity(type(row) is dict and set(row) == _ROW_FIELDS)
        _require_integrity(type(row["sequence"]) is int and row["sequence"] == sequence)
        _require_integrity(row["previous"] == previous)
        digest = row.pop("digest")
        _require_integrity(digest == _digest(canonical_json(row)))
        row["digest"] = digest
        _require_integrity(canonical_json(row) + b"\n" == line)
        event = EventV1(row["event"])
        return event, ReceiptV1(sequence, row["event"]["record_id"], row["event"]["run_id"], digest)

    def _read_records(self, accepted):
        events, receipts, record_ids, run_ids = [], [], set(), set()
        previous = _ZERO
        for sequence, line in enumerate(accepted.splitlines(keepends=True), 1):
            event, receipt = self._decode_row(line, sequence, previous)
            _require_integrity(receipt.record_id not in record_ids)
            record_ids.add(receipt.record_id)
            run_ids.add(receipt.run_id)
            events.append(event)
            receipts.append(receipt)
            previous = receipt.digest
        return tuple(events), tuple(receipts), previous, sorted(run_ids)

    @staticmethod
    def _verify_head(head, events, digest, run_ids):
        _require_integrity(
            head["count"] == len(events) and head["head"] == digest and head["run_ids"] == run_ids
        )

    @staticmethod
    def _verify_pending(pending, tail):
        if pending is None:
            _require_integrity(not tail)
            return
        _require_integrity(
            type(pending) is dict
            and set(pending) == {"line_sha256", "size"}
            and type(pending["size"]) is int
            and 0 < pending["size"] <= 70000
            and type(pending["line_sha256"]) is str
            and len(pending["line_sha256"]) == 64
            and len(tail) <= pending["size"]
        )
        _require_integrity(len(tail) != pending["size"] or _digest(tail) == pending["line_sha256"])

    def _snapshot(self, directory):
        try:
            head = self._read_head(directory)
            journal = self._read_file(directory, "events.jsonl")
            _require_integrity(len(journal) >= head["byte_count"])
            accepted, tail = journal[: head["byte_count"]], journal[head["byte_count"] :]
            events, receipts, digest, run_ids = self._read_records(accepted)
            self._verify_head(head, events, digest, run_ids)
            self._verify_pending(head["pending"], tail)
            return head, events, receipts, tail
        except (ValueError, TypeError, KeyError, UnicodeError, RecursionError):
            _integrity()
        except AuditErrorV1 as error:
            if error.code in {"invalid_event", "secret_rejected"}:
                _integrity()
            raise

    @staticmethod
    def _matching_receipt(record_id, event, events, receipts):
        for existing, receipt in zip(events, receipts):
            if receipt.record_id != record_id:
                continue
            if existing != event:
                _fail("identity_conflict", "Event identity already has different accepted content.")
            return receipt
        return None

    def _confirm_receipt(self, directory, context):
        context.update(phase="confirm_duplicate", writing=True)
        for name in ("events.jsonl", "head.json"):
            self._fsync_file(directory, name)
        os.fsync(directory)

    @staticmethod
    def _encode_append(head, record):
        row = {"sequence": head["count"] + 1, "previous": head["head"], "event": record}
        digest = _digest(canonical_json(row))
        row["digest"] = digest
        line = canonical_json(row) + b"\n"
        pending = {"line_sha256": _digest(line), "size": len(line)}
        receipt = ReceiptV1(row["sequence"], record["record_id"], record["run_id"], digest)
        return line, pending, receipt

    @staticmethod
    def _validate_retry(head, pending, line, tail):
        if head["pending"] is not None:
            if head["pending"] != pending:
                _fail(
                    "pending_conflict",
                    "Retry the exact pending event before appending another event.",
                )
            if not line.startswith(tail):
                _integrity()

    def _publish_intent(self, directory, context, head, pending):
        context.update(phase="publish_intent", writing=True)
        if head["pending"] is None:
            self._publish_head(directory, dict(head, pending=pending))
            return
        # The previous rename may be visible despite a failed directory fsync.
        self._fsync_file(directory, "head.json")
        os.fsync(directory)

    def _write_event(self, directory, context, line, tail):
        context["phase"] = "write_event"
        with self._file(directory, "events.jsonl", os.O_WRONLY | os.O_APPEND) as fd:
            _write_all(fd, line[len(tail) :])
            os.fsync(fd)

    def _accept_event(self, directory, context, head, record, line, receipt):
        context["phase"] = "accept_event"
        self._publish_head(
            directory,
            {
                "schema_version": 1,
                "count": receipt.sequence,
                "byte_count": head["byte_count"] + len(line),
                "head": receipt.digest,
                "run_ids": sorted(set(head["run_ids"]) | {record["run_id"]}),
                "pending": None,
            },
        )

    def append_v1(self, event):
        if not isinstance(event, EventV1):
            _fail("invalid_event", "append_v1 requires an EventV1.")
        event.reject_secrets(self.secret_values)
        context = {"phase": "verify", "event": event}
        with self._session(context) as directory:
            head, events, receipts, tail = self._snapshot(directory)
            record = event.to_dict()
            receipt = self._matching_receipt(record["record_id"], event, events, receipts)
            if receipt:
                self._confirm_receipt(directory, context)
                return receipt
            line, pending, receipt = self._encode_append(head, record)
            self._validate_retry(head, pending, line, tail)
            self._publish_intent(directory, context, head, pending)
            self._write_event(directory, context, line, tail)
            self._accept_event(directory, context, head, record, line, receipt)
            return receipt

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
