"""Bounded OS-isolation proof, not commissioning of any agent runner."""

import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from aew.audit.file_v1 import FileAuditV1
from test_events_v1 import event


_ATTACK = """
import os, pathlib, subprocess, sys
path = pathlib.Path(sys.argv[1])
action = sys.argv[2]
try:
    if action == 'truncate':
        path.write_bytes(b'changed')
    elif action == 'unlink':
        path.unlink()
    elif action == 'replace':
        pathlib.Path('replacement').write_bytes(b'changed')
        os.replace('replacement', path)
    elif action == 'symlink':
        pathlib.Path('link').symlink_to(path)
        pathlib.Path('link').write_bytes(b'changed')
    elif action == 'child':
        result = subprocess.run(['/bin/sh', '-c', 'echo changed > "$1"', 'sh', str(path)], capture_output=True)
        sys.exit(0 if result.returncode == 0 else 13)
    elif action == 'proc':
        pathlib.Path('/proc/' + sys.argv[3] + '/root' + str(path)).write_bytes(b'changed')
except (PermissionError, FileNotFoundError):
    sys.exit(13)
"""


class BoundaryTests(unittest.TestCase):
    def test_isolated_workspace_cannot_mutate_accepted_history(self):
        self.assertIsNotNone(
            shutil.which("bwrap"), "Install bubblewrap to run the required boundary proof"
        )
        with tempfile.TemporaryDirectory() as root:
            root = Path(root)
            store, work = root / "audit", root / "work"
            work.mkdir()
            provider = FileAuditV1.create_v1(store, workspace_roots=[work])
            provider.append_v1(event())
            original = {p.name: p.read_bytes() for p in store.iterdir()}
            sandbox = [
                "bwrap",
                "--unshare-all",
                "--new-session",
                "--die-with-parent",
                "--cap-drop",
                "ALL",
                "--clearenv",
                "--ro-bind",
                "/usr",
                "/usr",
                "--symlink",
                "usr/bin",
                "/bin",
                "--symlink",
                "usr/lib",
                "/lib",
                "--symlink",
                "usr/lib64",
                "/lib64",
                "--proc",
                "/proc",
                "--dev",
                "/dev",
                "--tmpfs",
                "/tmp",
                "--bind",
                str(work),
                "/work",
                "--chdir",
                "/work",
            ]
            for action in ("truncate", "unlink", "replace", "symlink", "child", "proc"):
                with self.subTest(action=action):
                    control = root / "control"
                    control.write_bytes(b"accepted")
                    command = [sys.executable, "-I", "-B", "-c", _ATTACK]
                    # Prove each attack actually mutates a reachable control.
                    disabled = subprocess.run(
                        command + [str(control), action, str(os.getpid())],
                        cwd=work,
                        capture_output=True,
                    )
                    self.assertEqual(disabled.returncode, 0, disabled.stderr.decode())
                    self.assertTrue(not control.exists() or control.read_bytes() != b"accepted")
                    (work / "link").unlink(missing_ok=True)
                    enabled = subprocess.run(
                        sandbox + command + [str(store / "events.jsonl"), action, str(os.getpid())],
                        capture_output=True,
                    )
                    self.assertEqual(enabled.returncode, 13, enabled.stderr.decode())
                    (work / "link").unlink(missing_ok=True)
            allowed = subprocess.run(
                sandbox
                + [sys.executable, "-I", "-B", "-c", "open('/work/allowed', 'w').write('ok')"],
                capture_output=True,
            )
            self.assertEqual(allowed.returncode, 0, allowed.stderr.decode())
            self.assertEqual((work / "allowed").read_text(), "ok")
            self.assertEqual(original, {p.name: p.read_bytes() for p in store.iterdir()})
            self.assertEqual(provider.read_v1(), (event(),))


if __name__ == "__main__":
    unittest.main()
