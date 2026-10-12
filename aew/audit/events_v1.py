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


_SECRET_KEYS = {
    "password",
    "passwd",
    "secret",
    "secrets",
    "token",
    "accesstoken",
    "refreshtoken",
    "apikey",
    "authorization",
    "credential",
    "credentials",
    "privatekey",
    "clientsecret",
    "cookie",
    "setcookie",
    "sessionid",
}
_SECRET_VALUE = re.compile(
    r"(?i)\bbearer\s+\S+|-----BEGIN (?:[A-Z ]*PRIVATE KEY|OPENSSH PRIVATE KEY)-----"
    r"|\b(?:gh[pousr]_[A-Za-z0-9_]{10,}|github_pat_[A-Za-z0-9_]+|sk-[A-Za-z0-9_-]{16,})"
)


def _invalid():
    raise AuditErrorV1("invalid_event", "Invalid v1 envelope or JSON details.")


def _walk(value, depth=0, secrets=()):
    if depth > 16:
        _invalid()
    if type(value) is dict:
        for key, item in value.items():
            if type(key) is not str:
                _invalid()
            normalized = re.sub(r"[^a-z0-9]", "", key.lower())
            if normalized in _SECRET_KEYS or normalized.endswith(
                ("password", "secret", "token", "apikey", "privatekey")
            ):
                raise AuditErrorV1(
                    "secret_rejected", "Secret-bearing content rejected before persistence."
                )
            _walk(key, depth + 1, secrets)
            _walk(item, depth + 1, secrets)
    elif type(value) is list:
        for item in value:
            _walk(item, depth + 1, secrets)
    elif type(value) is str:
        if _SECRET_VALUE.search(value) or any(secret in value for secret in secrets):
            raise AuditErrorV1(
                "secret_rejected", "Secret-bearing content rejected before persistence."
            )
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


class EventV1:
    """Immutable canonical snapshot; dictionary access always returns a copy."""

    __slots__ = ("_canonical",)

    def __init__(self, record):
        if type(record) is not dict:
            _invalid()
        if type(record.get("schema_version")) is not int or record["schema_version"] != 1:
            raise AuditErrorV1("unsupported_version", "Only audit envelope v1 is supported.")
        if set(record) != {
            "schema_version",
            "record_id",
            "record_type",
            "run_id",
            "task_ref",
            "recorded_at",
            "provenance",
            "details",
        }:
            _invalid()
        _walk(record)
        for field in ("record_id", "run_id"):
            try:
                if str(UUID(record[field])) != record[field]:
                    _invalid()
            except (ValueError, TypeError, AttributeError):
                _invalid()
        timestamp = record["recorded_at"]
        if type(timestamp) is not str or not re.fullmatch(
            r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d{1,6})?Z", timestamp
        ):
            _invalid()
        try:
            datetime.fromisoformat(timestamp)
        except ValueError:
            _invalid()
        name = record["record_type"]
        if (
            type(name) is not str
            or len(name) > 128
            or not re.fullmatch(r"[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)+", name)
        ):
            _invalid()
        task = record["task_ref"]
        provenance = record["provenance"]
        if type(task) is not dict or set(task) != {"provider", "project", "id"}:
            _invalid()
        if type(provenance) is not dict or set(provenance) != {"kind", "source"}:
            _invalid()
        for value in (*task.values(), *provenance.values()):
            if type(value) is not str or not value.strip() or len(value) > 256:
                _invalid()
        if provenance["kind"] not in {"controller", "adapter", "agent", "operator"}:
            _invalid()
        if type(record["details"]) is not dict:
            _invalid()
        try:
            encoded = canonical_json(record)
        except (ValueError, UnicodeError):
            _invalid()
        if len(encoded) > 65536:
            _invalid()
        object.__setattr__(self, "_canonical", encoded)

    def __setattr__(self, name, value):
        raise AttributeError("EventV1 is immutable")

    @property
    def canonical(self):
        return self._canonical

    def to_dict(self):
        return json.loads(self._canonical)

    def reject_secrets(self, secrets):
        _walk(self.to_dict(), secrets=secrets)

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
