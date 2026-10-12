"""Small language-neutral v1 audit events, receipts and typed failures."""

import json
import math
import re
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


class AuditErrorV1(Exception):
    """Safe diagnostics; callers decide whether to retry, abort or degrade audit.

    `acceptance` is not_attempted or unknown, never a claim that work must stop.
    `pending_event` retains a sanitized event for retry after an append IO failure.
    Errors never interpolate submitted values, paths or raw OS error messages.
    """

    def __init__(
        self,
        code,
        message,
        *,
        acceptance="not_attempted",
        phase=None,
        errno=None,
        pending_event=None
    ):
        super().__init__(message)
        self.code = code
        self.acceptance = acceptance
        self.phase = phase
        self.errno = errno
        self.pending_event = pending_event


def canonical_json(value):
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    ).encode("utf-8")


_SECRET_KEYS = set(
    "password passwd secret secrets token accesstoken refreshtoken apikey authorization "
    "credential credentials privatekey clientsecret cookie setcookie sessionid".split()
)
_SECRET_VALUE = re.compile(
    r"(?i)\bbearer\s+\S+|-----BEGIN (?:[A-Z ]*PRIVATE KEY|OPENSSH PRIVATE KEY)-----"
    r"|\b(?:gh[pousr]_[A-Za-z0-9_]{10,}|github_pat_[A-Za-z0-9_]+|sk-[A-Za-z0-9_-]{16,})"
)
_SECRET_SUFFIXES = ("password", "secret", "token", "apikey", "privatekey")
_EVENT_FIELDS = set(
    "schema_version record_id record_type run_id task_ref recorded_at provenance details".split()
)
_RECORD_TYPE = re.compile(r"[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)+")
_TIMESTAMP = re.compile(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d{1,6})?Z")


def _invalid():
    raise AuditErrorV1("invalid_event", "Invalid v1 envelope or JSON details.")


def _secret():
    raise AuditErrorV1("secret_rejected", "Secret-bearing content rejected before persistence.")


def _reject_secret(value, *, key, secrets):
    if key:
        normalized = re.sub(r"[^a-z0-9]", "", value.lower())
        if normalized in _SECRET_KEYS or normalized.endswith(_SECRET_SUFFIXES):
            _secret()
    if _SECRET_VALUE.search(value) or any(secret in value for secret in secrets):
        _secret()


def _walk_json(value, visit_string, depth=0):
    if depth > 16:
        _invalid()
    if type(value) is dict:
        for key, item in value.items():
            if type(key) is not str:
                _invalid()
            visit_string(key, key=True)
            _walk_json(key, visit_string, depth + 1)
            _walk_json(item, visit_string, depth + 1)
    elif type(value) is list:
        for item in value:
            _walk_json(item, visit_string, depth + 1)
    elif type(value) is str:
        visit_string(value, key=False)
    elif value is None or type(value) is bool:
        pass
    elif type(value) is int:
        if abs(value) > 2**53 - 1:
            _invalid()
    elif type(value) is float:
        if not math.isfinite(value):
            _invalid()
    else:
        _invalid()


def _valid_uuid(value):
    try:
        return type(value) is str and str(UUID(value)) == value
    except (ValueError, TypeError, AttributeError):
        return False


def _valid_timestamp(value):
    if type(value) is not str or not _TIMESTAMP.fullmatch(value):
        return False
    try:
        datetime.fromisoformat(value)
        return True
    except ValueError:
        return False


def _valid_text_map(value, fields):
    return (
        type(value) is dict
        and set(value) == fields
        and all(type(item) is str and item.strip() and len(item) <= 256 for item in value.values())
    )


def _encode(record):
    try:
        encoded = canonical_json(record)
    except (ValueError, UnicodeError):
        _invalid()
    if len(encoded) > 65536:
        _invalid()
    return encoded


def _validate_record(record):
    if type(record) is not dict:
        _invalid()
    if type(record.get("schema_version")) is not int or record["schema_version"] != 1:
        raise AuditErrorV1("unsupported_version", "Only audit envelope v1 is supported.")
    if set(record) != _EVENT_FIELDS:
        _invalid()
    _walk_json(record, lambda value, key: _reject_secret(value, key=key, secrets=()))
    if not all(_valid_uuid(record[field]) for field in ("record_id", "run_id")):
        _invalid()
    if not _valid_timestamp(record["recorded_at"]):
        _invalid()
    name = record["record_type"]
    if type(name) is not str or len(name) > 128 or not _RECORD_TYPE.fullmatch(name):
        _invalid()
    task, provenance = record["task_ref"], record["provenance"]
    if not _valid_text_map(task, {"provider", "project", "id"}):
        _invalid()
    if not _valid_text_map(provenance, {"kind", "source"}):
        _invalid()
    if provenance["kind"] not in {"controller", "adapter", "agent", "operator"}:
        _invalid()
    if type(record["details"]) is not dict:
        _invalid()


class EventV1:
    """Immutable canonical snapshot; dictionary access always returns a copy."""

    __slots__ = ("_canonical",)

    def __init__(self, record):
        _validate_record(record)
        object.__setattr__(self, "_canonical", _encode(record))

    def __setattr__(self, name, value):
        raise AttributeError("EventV1 is immutable")

    @property
    def canonical(self):
        return self._canonical

    def to_dict(self):
        return json.loads(self._canonical)

    def reject_secrets(self, secrets):
        _walk_json(
            self.to_dict(), lambda value, key: _reject_secret(value, key=key, secrets=secrets)
        )

    def __eq__(self, other):
        return isinstance(other, EventV1) and self.canonical == other.canonical


@dataclass(frozen=True)
class ReceiptV1:
    sequence: int
    record_id: str
    run_id: str
    digest: str


@dataclass(frozen=True)
class VerificationV1:
    count: int
    head: str
    run_ids: tuple[str, ...]
