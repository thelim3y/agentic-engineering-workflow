"""A trusted local entry point that produces an audited observation."""

import argparse
from dataclasses import asdict
import json
import sys

from .file_v1 import FileAuditV1
from .v1 import AuditErrorV1, EventV1


class _Parser(argparse.ArgumentParser):
    def error(self, message):
        # argparse's default includes submitted values, which may contain secrets.
        raise AuditErrorV1("invalid_configuration", "Invalid command arguments; consult --help.")


def main():
    try:
        if len(sys.argv) < 2 or sys.argv[1] != "v1":
            raise AuditErrorV1("unsupported_version", "Use the explicit audit API version v1.")
        parser = _Parser(description=__doc__)
        parser.add_argument("--store", required=True)
        parser.add_argument("--workspace", required=True, action="append")
        commands = parser.add_subparsers(dest="command", required=True)
        for name in ("init", "read", "verify"):
            commands.add_parser(name)
        observe = commands.add_parser("observe")
        for name in ("record-id", "run-id", "recorded-at", "project", "task", "name", "message"):
            observe.add_argument("--" + name, required=True)
        args = parser.parse_args(sys.argv[2:])
        if args.command == "init":
            FileAuditV1.create_v1(args.store, workspace_roots=args.workspace)
            result = {"schema_version": 1, "created": True}
        else:
            provider = FileAuditV1(args.store, workspace_roots=args.workspace)
            if args.command == "observe":
                event = EventV1(
                    {
                        "schema_version": 1,
                        "record_id": args.record_id,
                        "run_id": args.run_id,
                        "recorded_at": args.recorded_at,
                        "task_ref": {"provider": "local", "project": args.project, "id": args.task},
                        "provenance": {"kind": "operator", "source": "audit-cli"},
                        "record_type": "observation.recorded",
                        "details": {"name": args.name, "message": args.message},
                    }
                )
                result = asdict(provider.append_v1(event))
            elif args.command == "read":
                result = [event.to_dict() for event in provider.read_v1()]
            else:
                result = asdict(provider.verify_v1())
        print(json.dumps(result, sort_keys=True))
        return 0
    except AuditErrorV1 as error:
        print(
            json.dumps(
                {
                    "schema_version": 1,
                    "code": error.code,
                    "message": str(error),
                    "acceptance": error.acceptance,
                    "phase": error.phase,
                    "errno": error.errno,
                    "choices": ["retry", "abort", "audit-degraded"],
                }
            ),
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
