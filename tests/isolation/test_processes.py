"""Benign process-supervision tests, isolated from the unittest process.

Every scenario uses its own Python process. Descendants only sleep briefly;
the scenario always asks the helper to clean up, and the outer test bounds it.
"""
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import textwrap
import unittest


MODULE_DIRECTORY = str(Path(__file__).resolve().parent)


class ProcessSupervisionTests(unittest.TestCase):
    def scenario(self, body):
        with tempfile.TemporaryDirectory(prefix="isolation-process-unit-") as directory:
            script = "\n".join([
                "import json, os, pathlib, subprocess, sys, time",
                f"sys.path.insert(0, {MODULE_DIRECTORY!r})",
                "import processes",
                "processes.enable_subreaper()",
                f"root = pathlib.Path({directory!r})",
                "try:",
                textwrap.indent(textwrap.dedent(body).strip(), "    "),
                "finally:",
                "    processes.terminate_descendants(timeout=2)",
            ])
            child = subprocess.Popen(
                [sys.executable, "-B", "-c", script], cwd=directory,
                env={"PATH": os.defpath, "PYTHONUNBUFFERED": "1"},
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                start_new_session=True,
            )
            try:
                stdout, stderr = child.communicate(timeout=12)
            finally:
                if child.poll() is None:
                    os.killpg(child.pid, signal.SIGKILL)
                    child.communicate(timeout=3)
            self.assertEqual(child.returncode, 0, stderr)
            return json.loads(stdout)

    def test_normal_completion_has_no_survivors(self):
        result = self.scenario("""
            result = processes.run_command(
                [sys.executable, '-c', "print('completed')"],
                env={'PATH': os.defpath}, cwd=root, timeout=2)
            result['remaining'] = list(processes.descendants())
            print(json.dumps(result))
        """)
        self.assertEqual(result["rc"], 0)
        self.assertIn("completed", result["output"])
        self.assertFalse(result["cancelled"])
        self.assertFalse(result["timed_out"])
        self.assertTrue(result["drain_complete"])
        self.assertTrue(result["descendants_verified"])
        self.assertEqual(result["survivors"], [])
        self.assertEqual(result["remaining"], [])

    def test_output_is_bounded_and_truncation_is_explicit(self):
        result = self.scenario("""
            size = processes.MAX_OUTPUT_BYTES + 4096
            result = processes.run_command(
                [sys.executable, '-c', f'import os; os.write(1, b"x" * {size})'],
                env={'PATH': os.defpath}, cwd=root, timeout=2)
            result['remaining'] = list(processes.descendants())
            print(json.dumps(result))
        """)
        self.assertEqual(len(result["output"].encode()), 1024 * 1024)
        self.assertEqual(result["output_bytes_retained"], 1024 * 1024)
        self.assertEqual(result["output_bytes_total"], 1024 * 1024 + 4096)
        self.assertTrue(result["output_truncated"])
        self.assertTrue(result["drain_complete"])
        self.assertEqual(result["remaining"], [])

    def test_child_cannot_seek_or_truncate_accepted_output(self):
        program = textwrap.dedent("""
            import os
            os.write(1, b"EARLIER_FAILURE\\n")
            for action in (lambda: os.lseek(1, 0, 0), lambda: os.ftruncate(1, 0)):
                try:
                    action()
                except OSError:
                    pass
                else:
                    os.write(1, b"SEEKABLE_BYPASS\\n")
            os.write(1, b"LATER_OUTPUT\\n")
        """)
        result = self.scenario(f"""
            program = {program!r}
            result = processes.run_command(
                [sys.executable, '-c', program], env={{'PATH': os.defpath}},
                cwd=root, timeout=2)
            print(json.dumps(result))
        """)
        self.assertEqual(result["rc"], 0)
        self.assertEqual(result["output"], "EARLIER_FAILURE\nLATER_OUTPUT\n")
        self.assertFalse(result["output_truncated"])
        self.assertTrue(result["drain_complete"])

    def test_duplicated_descriptor_and_fragmented_writes_append(self):
        program = textwrap.dedent("""
            import os, subprocess, sys
            duplicate = os.dup(1)
            os.write(1, b"parent:")
            child = "import os, sys; fd=int(sys.argv[1]); [os.write(fd, bytes([value])) for value in b'child']"
            subprocess.run([sys.executable, "-c", child, str(duplicate)],
                           pass_fds=(duplicate,), check=True)
            os.write(duplicate, b":done\\n")
        """)
        result = self.scenario(f"""
            program = {program!r}
            result = processes.run_command(
                [sys.executable, '-c', program], env={{'PATH': os.defpath}},
                cwd=root, timeout=2)
            print(json.dumps(result))
        """)
        self.assertEqual(result["rc"], 0)
        self.assertEqual(result["output"], "parent:child:done\n")
        self.assertFalse(result["output_truncated"])
        self.assertTrue(result["drain_complete"])

    def test_invalid_encoding_is_retained_and_reported(self):
        program = r"import os; os.write(1, b'valid\xfftail')"
        result = self.scenario(f"""
            result = processes.run_command(
                [sys.executable, '-c', {program!r}],
                env={{'PATH': os.defpath}}, cwd=root, timeout=2)
            print(json.dumps(result))
        """)
        self.assertEqual(result["output"], "valid\ufffdtail")
        self.assertEqual(result["output_bytes_total"], 10)
        self.assertTrue(result["output_decode_replaced"])
        self.assertTrue(result["drain_complete"])

    def test_command_finishing_before_cancel_deadline_is_not_cancelled(self):
        result = self.scenario("""
            result = processes.run_command(
                [sys.executable, '-c', 'pass'], env={'PATH': os.defpath},
                cwd=root, timeout=2, cancel_after=1, late_wait=0.05)
            print(json.dumps(result))
        """)
        self.assertEqual(result["rc"], 0)
        self.assertFalse(result["cancelled"])

    def test_missing_binary_is_a_startup_error(self):
        result = self.scenario("""
            try:
                processes.run_command([str(root / 'missing-executable')],
                    env={'PATH': os.defpath}, cwd=root, timeout=1)
            except FileNotFoundError:
                result = {'startup_error': True}
            else:
                result = {'startup_error': False}
            result['remaining'] = list(processes.descendants())
            print(json.dumps(result))
        """)
        self.assertTrue(result["startup_error"])
        self.assertEqual(result["remaining"], [])

    def test_deadline_is_bounded_and_cleans_up(self):
        result = self.scenario("""
            before = time.monotonic()
            result = processes.run_command(
                [sys.executable, '-c', 'import time; time.sleep(3)'],
                env={'PATH': os.defpath}, cwd=root, timeout=0.15)
            result['elapsed'] = time.monotonic() - before
            result['remaining'] = list(processes.descendants())
            print(json.dumps(result))
        """)
        self.assertTrue(result["timed_out"])
        self.assertFalse(result["cancelled"])
        self.assertLess(result["elapsed"], 2.5)
        self.assertEqual(result["remaining"], [])

    def test_adopted_detached_child_is_found_without_run_path_in_argv(self):
        result = self.scenario("""
            marker = root / 'child.pid'
            child_code = 'import time; time.sleep(3)'
            parent_code = (
                'import pathlib, subprocess, sys; '
                f'p = subprocess.Popen([sys.executable, "-c", {child_code!r}], start_new_session=True); '
                f'pathlib.Path({str(marker)!r}).write_text(str(p.pid))')
            parent = subprocess.Popen([sys.executable, '-c', parent_code],
                                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            parent.wait(timeout=2)
            pid = int(marker.read_text())
            found = processes.descendants()
            command = pathlib.Path(f'/proc/{pid}/cmdline').read_bytes()
            result = {'found': pid in found, 'entry': found.get(pid),
                      'self': os.getpid(), 'path_in_argv': str(root).encode() in command}
            processes.terminate_descendants(timeout=2)
            result['remaining'] = list(processes.descendants())
            print(json.dumps(result))
        """)
        self.assertTrue(result["found"])
        self.assertFalse(result["path_in_argv"])
        self.assertEqual(result["entry"]["ppid"], result["self"])
        self.assertIn("starttime", result["entry"])
        self.assertIn("state", result["entry"])
        self.assertEqual(result["remaining"], [])

    def test_detached_stdout_holder_is_recorded_and_cleaned_up_after_cancel(self):
        result = self.scenario("""
            child_code = 'import time; time.sleep(3)'
            parent_code = (
                'import subprocess, sys, time; '
                f'p = subprocess.Popen([sys.executable, "-c", {child_code!r}], start_new_session=True); '
                'print(p.pid, flush=True); time.sleep(3)')
            before = time.monotonic()
            result = processes.run_command([sys.executable, '-c', parent_code],
                env={'PATH': os.defpath}, cwd=root, timeout=2,
                cancel_after=0.2, late_wait=0.05)
            result['elapsed'] = time.monotonic() - before
            result['detached_pid'] = int(result['output'].strip())
            result['remaining'] = list(processes.descendants())
            print(json.dumps(result))
        """)
        self.assertTrue(result["cancelled"])
        self.assertFalse(result["timed_out"])
        self.assertIn(result["detached_pid"], [int(pid) for pid in result["survivors"]])
        self.assertTrue(result["drain_complete"])
        self.assertFalse(result["output_truncated"])
        self.assertTrue(result["descendants_verified"])
        self.assertLess(result["elapsed"], 2.5)
        self.assertEqual(result["remaining"], [])

    def test_early_survivor_evidence_is_retained_after_child_exits(self):
        result = self.scenario("""
            child_code = 'import time; time.sleep(0.7)'
            parent_code = (
                'import subprocess, sys, time; '
                f'p = subprocess.Popen([sys.executable, "-c", {child_code!r}], start_new_session=True); '
                'print(p.pid, flush=True); time.sleep(3)')
            result = processes.run_command([sys.executable, '-c', parent_code],
                env={'PATH': os.defpath}, cwd=root, timeout=2,
                cancel_after=0.2, late_wait=1)
            result['detached_pid'] = int(result['output'].strip())
            result['remaining'] = list(processes.descendants())
            print(json.dumps(result))
        """)
        self.assertTrue(result["cancelled"])
        self.assertIn(result["detached_pid"], [int(pid) for pid in result["survivors"]])
        self.assertEqual(result["remaining"], [])

    def test_detached_late_output_appends_before_cleanup(self):
        result = self.scenario("""
            child_code = 'import os, time; time.sleep(0.25); os.write(1, b"late\\\\n")'
            parent_code = (
                'import subprocess, sys, time; '
                f'p = subprocess.Popen([sys.executable, "-c", {child_code!r}], start_new_session=True); '
                'print("early", flush=True); time.sleep(3)')
            result = processes.run_command([sys.executable, '-c', parent_code],
                env={'PATH': os.defpath}, cwd=root, timeout=2,
                cancel_after=0.1, late_wait=0.4)
            result['remaining'] = list(processes.descendants())
            print(json.dumps(result))
        """)
        self.assertTrue(result["cancelled"])
        self.assertEqual(result["output"], "early\nlate\n")
        self.assertTrue(result["drain_complete"])
        self.assertFalse(result["output_truncated"])
        self.assertEqual(result["remaining"], [])


if __name__ == "__main__":
    unittest.main()
