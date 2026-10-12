import json
import unittest

from aew.audit.v1 import AuditErrorV1, EventV1


def event(record_id="00000000-0000-4000-8000-000000000001", **changes):
    record = {
        "schema_version": 1,
        "record_id": record_id,
        "record_type": "observation.recorded",
        "run_id": "00000000-0000-4000-8000-000000000010",
        "task_ref": {"provider": "local", "project": "example", "id": "task-1"},
        "recorded_at": "2026-10-12T09:00:00Z",
        "provenance": {"kind": "operator", "source": "audit-cli"},
        "details": {"name": "example.started", "message": "Started", "attempt": 1},
    }
    record.update(changes)
    return EventV1(record)


class EventTests(unittest.TestCase):
    def test_round_trip_preserves_unknown_names_and_json_details(self):
        original = event(record_type="future.extension", details={"ok": True, "x": [None, 1.5]})
        self.assertEqual(EventV1(json.loads(original.canonical)), original)

    def test_input_and_output_mutations_cannot_change_event(self):
        details = {"nested": [1]}
        original = event(details=details)
        details["nested"].append(2)
        output = original.to_dict()
        output["details"]["nested"].append(3)
        self.assertEqual(original.to_dict()["details"], {"nested": [1]})

    def test_unknown_versions_are_typed(self):
        for version in (2, "1", True, None):
            with self.subTest(version=version), self.assertRaises(AuditErrorV1) as caught:
                event(schema_version=version)
            self.assertEqual(caught.exception.code, "unsupported_version")

    def test_invalid_envelopes_and_non_json_details(self):
        for change in (
            {"record_id": "unstable"},
            {"recorded_at": "yesterday"},
            {"recorded_at": "2026-10-12T09:00:00"},
            {"record_type": "unnamespaced"},
            {"details": {"x": float("nan")}},
            {"details": {"x": float("inf")}},
            {"details": {"x": object()}},
            {"details": {1: "non-string key"}},
            {"details": {"x": 2**53}},
            {"details": {"x": "\ud800"}},
            {"provenance": {"kind": "unknown", "source": "x"}},
            {"extra": 1},
        ):
            with self.subTest(change=repr(change)), self.assertRaises(AuditErrorV1) as caught:
                event(**change)
            self.assertEqual(caught.exception.code, "invalid_event")

    def test_secrets_rejected_without_echoing_values(self):
        for details in (
            {"nested": [{"api_key": "synthetic-sensitive"}]},
            {"Authorization": "synthetic-sensitive"},
            {"message": "Bearer synthetic-sensitive"},
            {"message": "-----BEGIN PRIVATE KEY----- synthetic-sensitive"},
        ):
            with self.subTest(details=details), self.assertRaises(AuditErrorV1) as caught:
                event(details=details)
            self.assertEqual(caught.exception.code, "secret_rejected")
            self.assertNotIn("synthetic-sensitive", str(caught.exception))

    def test_cycles_depth_and_size_are_bounded(self):
        cycle = {}
        cycle["x"] = cycle
        deep = {}
        for _ in range(30):
            deep = {"x": deep}
        for details in (cycle, deep, {"message": "x" * 65536}):
            with self.assertRaises(AuditErrorV1) as caught:
                event(details=details)
            self.assertEqual(caught.exception.code, "invalid_event")


if __name__ == "__main__":
    unittest.main()
