"""Linux-only process accounting for the trusted, sequential spike runner.

Subreaping preserves ancestry across setsid/double-fork/renamed commands. The
outer PID namespace contains the whole suite. This is not a general job runner.
"""
import ctypes
import os
from pathlib import Path
import signal
import subprocess
import tempfile
import time


def enable_subreaper():
    libc = ctypes.CDLL(None, use_errno=True)
    if libc.prctl(36, 1, 0, 0, 0) != 0:  # PR_SET_CHILD_SUBREAPER
        raise OSError(ctypes.get_errno(), "cannot enable child subreaper")


def _require_subreaper():
    value = ctypes.c_int()
    libc = ctypes.CDLL(None, use_errno=True)
    if libc.prctl(37, ctypes.byref(value), 0, 0, 0) != 0 or value.value != 1:
        raise RuntimeError("Process accounting requires a child subreaper")


def _stat(pid):
    # comm can contain spaces and parentheses; fields after its final ')' are fixed.
    fields = (Path("/proc")/str(pid)/"stat").read_text().rsplit(")", 1)[1].split()
    return {"state": fields[0], "ppid": int(fields[1]), "starttime": int(fields[19])}


def descendants(exclude=()):
    _require_subreaper()
    snapshot = {}
    for item in Path("/proc").iterdir():
        if not item.name.isdigit():
            continue
        try:
            snapshot[int(item.name)] = _stat(int(item.name))
        except (FileNotFoundError, ProcessLookupError):
            continue  # process exited during the scan; other errors fail closed
    parents = {os.getpid()}
    found = {}
    while True:
        children = {pid: data for pid, data in snapshot.items()
                    if data["ppid"] in parents and pid not in found and pid not in exclude}
        if not children:
            return found
        found.update(children)
        parents.update(children)


def _reap():
    while True:
        try:
            if os.waitpid(-1, os.WNOHANG)[0] == 0:
                return
        except ChildProcessError:
            return


def terminate_descendants(exclude=(), timeout=2):
    deadline = time.monotonic() + timeout
    while True:
        remaining = descendants(exclude)
        for pid, expected in remaining.items():
            if expected["state"] == "Z":
                continue
            try:
                # Signal a stable identity, never a recycled PID from a stale scan.
                fd = os.pidfd_open(pid)
                try:
                    if _stat(pid)["starttime"] == expected["starttime"]:
                        signal.pidfd_send_signal(fd, signal.SIGKILL)
                finally:
                    os.close(fd)
            except (FileNotFoundError, ProcessLookupError):
                continue
        _reap()
        if not descendants(exclude):
            return
        if time.monotonic() >= deadline:
            raise RuntimeError("Could not confirm descendant termination")
        time.sleep(0.02)


def run_command(cmd, env, cwd, timeout=120, cancel_after=None, late_wait=6, exclude=()):
    _require_subreaper()
    cancelled = timed_out = False
    observed = set()
    # A regular file avoids communicate() waiting on a detached inherited pipe.
    with tempfile.TemporaryFile() as output:
        process = subprocess.Popen(cmd, env=env, cwd=cwd, stdout=output,
                                   stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                                   start_new_session=True)
        try:
            try:
                process.wait(timeout=cancel_after if cancel_after is not None else timeout)
            except subprocess.TimeoutExpired:
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                else:
                    cancelled = cancel_after is not None
                timed_out = cancel_after is None
                process.wait(timeout=2)
            # Include early survivors even if they exit before the late-effect check.
            observed.update(pid for pid, data in descendants(exclude).items() if data["state"] != "Z")
            if cancelled:
                time.sleep(late_wait)
                observed.update(pid for pid, data in descendants(exclude).items() if data["state"] != "Z")
        finally:
            if process.poll() is None:
                process.kill()
                process.wait(timeout=2)
            terminate_descendants(exclude)
        output.seek(0)
        content = output.read(1024 * 1024 + 1)
        complete = len(content) <= 1024 * 1024
        return {"rc": process.returncode, "cancelled": cancelled, "timed_out": timed_out,
                "survivors": sorted(observed), "descendants_verified": True,
                "drain_complete": complete, "output": content[:1024 * 1024].decode("utf-8", errors="replace")}
