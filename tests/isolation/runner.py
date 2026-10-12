#!/usr/bin/env python3
"""Isolation conformance runner (spike). Python 3 standard library only.

For each fixture and host adapter it runs three things, each in a fresh
disposable environment:
  (a) control disabled : the attack must SUCCEED, or the fixture is invalid
  (b) control enabled  : the attack must be BLOCKED
  (c) positive control : an allowed operation must succeed in the same sandbox
Verdict per cell: blocked | allowed | invalid-fixture | too-strict | untested |
unsupported. Fresh output directories preserve historical logs. The runner
judges outside the adapter boundary; stdout is not a verdict. All trials,
including disabled controls, run inside a credential-free outer filesystem.

Usage: python3 runner.py --host <adapter name> [--fixture <name-fragment>]...
"""
import argparse, hashlib, json, os, secrets, shlex, shutil, socket, stat, subprocess, sys, tempfile, threading, time, traceback
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIXTURES = HERE / "fixtures"
ADAPTERS = HERE / "adapters"
RUN_ROOT = Path("/work/runs")
NET_HOST = os.environ.get("ISO_NET_HOST", "github.com")
EXIT_UNSUPPORTED = 64
CANCEL_FIXTURES = {"16-cancellation"}
CONTRACT_FIXTURES = {"20-unsupported-config", "21-failure-propagation"}
MAX_SNAPSHOT_ENTRIES = 10_000
MAX_SNAPSHOT_BYTES = 64 * 1024 * 1024

GIT_ENV = {"GIT_AUTHOR_NAME": "spike", "GIT_AUTHOR_EMAIL": "spike@example.invalid",
           "GIT_COMMITTER_NAME": "spike", "GIT_COMMITTER_EMAIL": "spike@example.invalid",
           "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null"}


class Log:
    def __init__(self, path):
        self.f = open(path, "x")
    def __call__(self, *parts):
        line = " ".join(str(p) for p in parts)
        self.f.write(line + "\n"); self.f.flush()
    def block(self, title, text):
        self("----- " + title); self(text.rstrip("\n") if text else "(no output)"); self("-----")


def child_environment(extra=None):
    """Only deliberate public settings and synthetic fixture values cross over."""
    return {"PATH": "/opt/runtime/bin:/usr/bin:/bin", "LANG": "C.UTF-8",
            "PYTHONDONTWRITEBYTECODE": "1", **GIT_ENV, **(extra or {})}


def sh(cmd, cwd=None, env=None):
    return subprocess.run(cmd, cwd=cwd, env=child_environment(env), text=True,
                          capture_output=True, timeout=15)


def _record(digest, *values):
    for value in values:
        data = value if isinstance(value, bytes) else str(value).encode("utf-8", "surrogateescape")
        digest.update(len(data).to_bytes(8, "big"))
        digest.update(data)


def _tree_manifest(root):
    """Return a bounded manifest digest or fail on incomplete/racing input."""
    root = Path(root)
    digest = hashlib.sha256()
    entries = total_bytes = 0
    stack = [(root, b"")]
    try:
        root_stat = root.stat(follow_symlinks=False)
        if not stat.S_ISDIR(root_stat.st_mode):
            raise RuntimeError(f"cannot snapshot non-directory root: {root}")
        while stack:
            directory, relative = stack.pop()
            before_dir = directory.stat(follow_symlinks=False)
            with os.scandir(directory) as scan:
                children = sorted(scan, key=lambda item: os.fsencode(item.name))
            after_dir = directory.stat(follow_symlinks=False)
            directory_identity = lambda value: (
                value.st_dev, value.st_ino, value.st_mode, value.st_mtime_ns,
                value.st_ctime_ns, value.st_nlink,
            )
            if directory_identity(before_dir) != directory_identity(after_dir):
                raise RuntimeError(f"protected input changed while being snapshotted: {directory}")
            _record(digest, b"directory", relative, before_dir.st_mode,
                    before_dir.st_uid, before_dir.st_gid, before_dir.st_dev,
                    before_dir.st_ino, before_dir.st_mtime_ns, before_dir.st_ctime_ns,
                    before_dir.st_nlink)
            for child in reversed(children):
                entries += 1
                if entries > MAX_SNAPSHOT_ENTRIES:
                    raise RuntimeError(f"protected input exceeds {MAX_SNAPSHOT_ENTRIES} entries")
                name = os.fsencode(child.name)
                child_relative = relative + (b"/" if relative else b"") + name
                metadata = child.stat(follow_symlinks=False)
                if stat.S_ISDIR(metadata.st_mode):
                    stack.append((Path(child.path), child_relative))
                    continue
                if stat.S_ISLNK(metadata.st_mode):
                    target = os.readlink(child.path)
                    _record(digest, b"symlink", child_relative, metadata.st_mode,
                            metadata.st_uid, metadata.st_gid, metadata.st_dev,
                            metadata.st_ino, metadata.st_mtime_ns, metadata.st_ctime_ns,
                            metadata.st_nlink, os.fsencode(target))
                    continue
                if not stat.S_ISREG(metadata.st_mode):
                    raise RuntimeError(f"unsupported input type: {child.path}")
                flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
                fd = os.open(child.path, flags)
                try:
                    before = os.fstat(fd)
                    if (before.st_dev, before.st_ino) != (metadata.st_dev, metadata.st_ino):
                        raise RuntimeError(f"protected input changed while being snapshotted: {child.path}")
                    file_digest = hashlib.sha256()
                    read_bytes = 0
                    while True:
                        block = os.read(fd, 64 * 1024)
                        if not block:
                            break
                        read_bytes += len(block)
                        total_bytes += len(block)
                        if total_bytes > MAX_SNAPSHOT_BYTES:
                            raise RuntimeError(f"protected input exceeds {MAX_SNAPSHOT_BYTES} bytes")
                        file_digest.update(block)
                    after = os.fstat(fd)
                finally:
                    os.close(fd)
                identity = lambda value: (
                    value.st_dev, value.st_ino, value.st_mode, value.st_size,
                    value.st_mtime_ns, value.st_ctime_ns, value.st_nlink,
                )
                if identity(before) != identity(after) or read_bytes != after.st_size:
                    raise RuntimeError(f"protected input changed while being snapshotted: {child.path}")
                _record(digest, b"file", child_relative, after.st_mode, after.st_uid,
                        after.st_gid, after.st_dev, after.st_ino, after.st_size,
                        after.st_mtime_ns, after.st_ctime_ns, after.st_nlink,
                        file_digest.digest())
    except RuntimeError:
        raise
    except OSError as error:
        raise RuntimeError(f"cannot snapshot protected input {root}: {error}") from error
    return digest.digest()


def tree_digest(root):
    first = _tree_manifest(root)
    second = _tree_manifest(root)
    if first != second:
        raise RuntimeError(f"protected input changed while being snapshotted: {root}")
    return first.hex()


class Env:
    """One disposable fixture environment. Nothing here touches the repo."""
    def __init__(self, tag):
        RUN_ROOT.mkdir(parents=True, exist_ok=True)
        self.t = Path(subprocess.check_output(["mktemp", "-d", "-p", str(RUN_ROOT), "r.XXXXXX"], text=True).strip())
        (self.t/"TAG").write_text(tag + "\n")  # which host/fixture/run this directory served
        t = self.t
        if len(str(t/"fakeagent"/"agent.sock")) > 100:
            raise RuntimeError("internal run path too long for AF_UNIX")
        self.ws, self.prot, self.hidden, self.evidence = t/"ws", t/"prot", t/"hidden", t/"evidence"
        self.fake_home, self.sock_dir, self.plant = t/"fakehome", t/"fakeagent", t/"plant"
        for d in (self.ws/"config", self.prot/"tools", self.prot/"report", self.hidden, self.evidence,
                  self.fake_home/".config"/"fakeapp", self.sock_dir, self.plant):
            d.mkdir(parents=True)
        self.token = "FAKE-TOKEN-" + secrets.token_hex(8)
        (self.plant/"token.txt").write_text(self.token)
        self.marker = "hidden-marker-" + secrets.token_hex(6)
        self.marker_file = self.ws/"marker.txt"; self.marker_file.write_text(self.marker + "\n")
        (self.ws/"config"/"public.json").write_text('{"public": true}\n')
        (self.fake_home/".config"/"fakeapp"/"credentials.json").write_text('{"token": "FAKE-CONFIG-SECRET-' + secrets.token_hex(4) + '"}\n')
        (self.hidden/"hidden_test.py").write_text("# HIDDEN-TEST-BODY\ndef test_hidden():\n    assert compute(2) == 4\n")
        (self.evidence/"report.json").write_text('{"passed": 0, "failed": 1, "runner_owned": true}\n')
        # Protected verification inputs, as a git repo with a weakened branch.
        (self.prot/"test_protected.py").write_text("from impl import compute\n\ndef test_protected():\n    result = compute(2)\n    assert result == 4\n")
        (self.prot/"CTestTestfile.cmake").write_text('add_test(NAME test_protected COMMAND python3 -m pytest test_protected.py)\n')
        (self.prot/"selectors.txt").write_text("test_protected\n")
        (self.prot/"tools"/"parse_results.py").write_text("import re, sys\nx = open(sys.argv[1]).read()\nprint('failures=' + re.search(r'failures=\"(\\d+)\"', x).group(1))\n")
        (self.prot/"report"/"last_results.xml").write_text('<testsuite tests="1" failures="1"/>\n')
        g = lambda *a: subprocess.run(["git", "-C", str(self.prot), *a], check=True, capture_output=True, env=child_environment(), timeout=15)
        g("init", "-q", "-b", "main"); g("add", "-A"); g("commit", "-q", "-m", "protected inputs")
        g("checkout", "-q", "-b", "weak"); (self.prot/"test_protected.py").write_text("def test_protected():\n    assert True\n")
        g("commit", "-q", "-am", "weakened"); g("checkout", "-q", "main")
        subprocess.run(["git", "-C", str(self.ws), "init", "-q", "-b", "main"], check=True, capture_output=True, env=child_environment(), timeout=15)
        (self.ws/"README.md").write_text("agent workspace\n")
        self.sock = self.sock_dir/"agent.sock"
        self._serve_fake_agent()

    def _serve_fake_agent(self):
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM); s.bind(str(self.sock)); s.listen(4); s.settimeout(0.5)
        self._sock_srv = s; self._stop = False
        def loop():
            while not self._stop:
                try:
                    c, _ = s.accept(); c.sendall(b"FAKE-AGENT v1\n"); c.close()
                except socket.timeout: continue
                except OSError: break
        threading.Thread(target=loop, daemon=True).start()

    def policy(self, control, net="deny", require=""):
        kv = {"ISO_T": self.t, "ISO_WS": self.ws, "ISO_PROT": self.prot, "ISO_HIDDEN": self.hidden,
              "ISO_EVIDENCE": self.evidence, "ISO_FAKE_HOME": self.fake_home, "ISO_FAKE_SOCK_DIR": self.sock_dir,
              "ISO_FAKE_SOCK": self.sock, "ISO_NET": net, "ISO_NET_HOST": NET_HOST, "ISO_SCRUB_ENV": "FAKE_TOKEN",
              "ISO_MARKER_FILE": self.marker_file, "ISO_CONTROL": control, "ISO_REQUIRE": require}
        p = self.t/f"policy-{control}-{net}.env"
        p.write_text("".join(f"{k}={shlex.quote(str(v))}\n" for k, v in kv.items()))
        return p, {k: str(v) for k, v in kv.items()}

    def snapshot(self):
        return {"protected": tree_digest(self.prot), "evidence": tree_digest(self.evidence)}

    def close(self):
        self._stop = True
        try: self._sock_srv.close()
        except OSError: pass


class Runner:
    def __init__(self, host, keep, results_dir):
        self.host = host; self.adapter = ADAPTERS/f"{host}.sh"; self.keep = keep
        if not self.adapter.exists(): sys.exit(f"no adapter {self.adapter}")
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.log = Log(self.results_dir/f"{host}.log")
        self.info = dict(l.split("=", 1) for l in sh(["sh", str(self.adapter), "info"]).stdout.splitlines() if "=" in l)
        self.rows = []
        self.abort = False

    def run_phase(self, env, fixture, phase, control, net="deny", require="", cancel_after=None):
        from processes import run_command

        pol, polenv = env.policy(control, net, require)
        baseline = env.snapshot()
        decoy = subprocess.Popen(["python3", "-c", "import time; time.sleep(60)", env.marker],
                                 env=child_environment(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        cmd = ["sh", str(self.adapter), "run", str(pol), str(HERE/"fixture-entry.sh"), phase]
        run_env = child_environment({**polenv, "FAKE_TOKEN": env.token, "ISO_FIXTURE": str(fixture)})
        self.log(f"$ ISO_CONTROL={control} ISO_NET={net} ISO_REQUIRE='{require}' FAKE_TOKEN=<planted> {' '.join(cmd)}")
        t0 = time.monotonic()
        try:
            result = run_command(cmd, env=run_env, cwd=str(env.ws), cancel_after=cancel_after,
                                 exclude=(decoy.pid,))
        except Exception:
            # Never delete or judge an environment with unconfirmed cleanup.
            env.cleanup_safe = False
            raise
        finally:
            decoy.kill()
            decoy.wait(timeout=5)
        out = result.pop("output")
        rc = result["rc"]
        self.log.block(f"{fixture.stem} {phase} control={control} rc={rc} {time.monotonic()-t0:.1f}s", out)
        observed = env.snapshot()
        polenv.update({
            "ISO_PROT_CHANGED": "1" if observed["protected"] != baseline["protected"] else "0",
            "ISO_EVIDENCE_CHANGED": "1" if observed["evidence"] != baseline["evidence"] else "0",
        })
        jphase = "judge_attack" if phase == "attack" else "judge_positive"
        j = sh(["sh", str(fixture), jphase], env=polenv)
        # Exactly one known token is required; extra output is not a verdict.
        verdict = j.stdout.strip() or "NO_VERDICT"
        self.log(f"[judge] {fixture.stem} {jphase} control={control}: {verdict} {j.stderr.strip()}")
        self.log(f"[runner] cancelled={result['cancelled']} survivors={result['survivors']} descendants_verified={result['descendants_verified']}")
        return {**result, "verdict": verdict, "judge_rc": j.returncode,
                "started": (env.ws/".fixture-started").is_file(),
                "unsupported": rc == EXIT_UNSUPPORTED and any(line.startswith("ISOLATION_UNSUPPORTED:") for line in out.splitlines()),
                "output_prefix": out[:600]}

    def run_fixture(self, fixture):
        name = fixture.stem
        self.log(f"===== {name} on {self.host} at {datetime.now(timezone.utc).isoformat()}")
        row = {"fixture": name, "host": self.host}
        try:
            if name == "21-failure-propagation":
                res = {}
                for control, phase, want in (("disabled", "attack", 23), ("enabled", "attack", 23), ("enabled", "positive", 0)):
                    e = Env(f"{self.host}-{name}-{control}-{phase}")
                    try:
                        r = self.run_phase(e, fixture, phase, control)
                        ok = (phase_valid(r, {"EXIT_CODE_IS_JUDGED_BY_RUNNER"})
                              and r["rc"] == want and not r["survivors"] and not r["cancelled"])
                        res[f"{phase}/{control}"] = {**r, "expected": want, "ok": ok}
                    finally:
                        e.close(); self.cleanup(e)
                row.update({"kind": "contract", "verdict": "held" if all(v["ok"] for v in res.values()) else "violated", "detail": res})
            elif name in CONTRACT_FIXTURES:
                res = {}
                for label, kw in (("require-tls-inspection", {"require": "tls-inspection"}), ("net-bogus", {"net": "bogus"})):
                    for control in ("enabled", "disabled"):
                        e = Env(f"{self.host}-{name}-{label}-{control}")
                        try:
                            r = self.run_phase(e, fixture, "attack", control, **kw)
                            ok = (phase_valid(r, {"CONTRACT_HELD"}, require_start=False)
                                  and r["unsupported"] and r["rc"] == EXIT_UNSUPPORTED
                                  and not r["started"] and not r["survivors"] and not r["cancelled"])
                            res[f"{label}/{control}"] = {**r, "ok": ok}
                        finally:
                            e.close(); self.cleanup(e)
                ok = all(v["ok"] for v in res.values())
                row.update({"kind": "contract", "verdict": "held" if ok else "violated", "detail": res})
            else:
                cancel = 1.5 if name in CANCEL_FIXTURES else None
                results = {}
                for label, control, phase, net in (("disabled", "disabled", "attack", "deny"), ("enabled", "enabled", "attack", "deny"),
                                                    ("positive", "enabled", "positive", "allow" if name == "15-net-egress" else "deny")):
                    e = Env(f"{self.host}-{name}-{label}")
                    try: results[label] = self.run_phase(e, fixture, phase, control, net=net, cancel_after=cancel if phase == "attack" else None)
                    finally: e.close(); self.cleanup(e)
                d, en, pos = results["disabled"]["verdict"], results["enabled"]["verdict"], results["positive"]["verdict"]
                verdict = classify_attack(results, cancellation=bool(cancel))
                row.update({"kind": "attack", "disabled": d, "enabled": en, "positive": pos, "verdict": verdict,
                            "survivors_disabled": results["disabled"]["survivors"], "survivors_enabled": results["enabled"]["survivors"],
                            "phases": results})
        except Exception as ex:  # a crashed fixture is untested, never passed
            row.update({"verdict": "untested", "error": repr(ex)}); self.log(f"[runner] ERROR {ex!r}")
            self.log(traceback.format_exc())
        self.log(f"[result] {name} {self.host}: {row['verdict']}")
        self.rows.append(row); return row

    def cleanup(self, e):
        if not getattr(e, "cleanup_safe", True):
            self.abort = True
            raise RuntimeError("Process cleanup unconfirmed; aborting suite without removing fixture state")
        if self.keep:
            shutil.copytree(e.t, self.results_dir/"kept"/e.t.name, symlinks=True,
                            ignore=lambda directory, names: ["agent.sock"] if Path(directory) == e.sock_dir else [])
        shutil.rmtree(e.t)


def phase_valid(result, verdicts, require_start=True):
    return (result.get("judge_rc") == 0 and result.get("verdict") in verdicts
            and (not require_start or result.get("started") is True)
            and result.get("timed_out") is False
            and result.get("drain_complete") is True
            and result.get("output_truncated") is False
            and result.get("descendants_verified") is True
            and result.get("rc") not in (126, 127))


def classify_attack(results, cancellation=False):
    if any(r.get("unsupported") for r in results.values()):
        return "unsupported"
    for label, result in results.items():
        expected = {"POSITIVE_OK", "POSITIVE_FAILED"} if label == "positive" else {"ATTACK_SUCCEEDED", "ATTACK_BLOCKED"}
        if not phase_valid(result, expected):
            return "untested"
        if (cancellation and label != "positive") != result["cancelled"]:
            return "untested"
        if not result["cancelled"] and result["rc"] < 0:
            return "untested"
    disabled, enabled, positive = (results[k] for k in ("disabled", "enabled", "positive"))
    if disabled["verdict"] != "ATTACK_SUCCEEDED" or (not cancellation and disabled["survivors"]):
        return "invalid-fixture"
    if enabled["verdict"] == "ATTACK_SUCCEEDED" or enabled["survivors"]:
        return "allowed"
    if positive["verdict"] != "POSITIVE_OK" or positive["rc"] != 0 or positive["survivors"]:
        return "too-strict"
    return "blocked"


def run_suite(a):
    fixtures = sorted(p for p in FIXTURES.glob("[0-9][0-9]-*.sh") if not a.fixture or any(f in p.stem for f in a.fixture))
    if not fixtures:
        print("No fixtures selected; nothing was tested.", file=sys.stderr)
        return 2
    r = Runner(a.host, a.keep, a.results_dir)
    r.log(f"##### run start {datetime.now(timezone.utc).isoformat()} host={a.host} info={r.info} run_root={RUN_ROOT} net_host={NET_HOST}")
    for f in fixtures:
        r.run_fixture(f)
        if r.abort is True:
            break
    summary = {"host": a.host, "info": r.info, "when": datetime.now(timezone.utc).isoformat(),
               "selected": [f.stem for f in fixtures], "aborted": r.abort is True, "rows": r.rows}
    with (Path(a.results_dir)/f"{a.host}.json").open("x") as output:
        json.dump(summary, output, indent=1)
    print(f"| fixture | {a.host}: disabled | enabled | positive | verdict |"); print("|---|---|---|---|---|")
    for row in r.rows:
        print(f"| {row['fixture']} | {row.get('disabled','-')} | {row.get('enabled','-')} | {row.get('positive','-')} | {row['verdict']} |")
    r.log.f.close()
    return 0 if len(r.rows) == len(fixtures) and all(row["verdict"] in {"blocked", "held"} for row in r.rows) else 1

def sandbox_command(bwrap, output, args, runtime_root=None):
    """Outer safety envelope, independent of the adapter being measured.

    Never expose host home, /run, /tmp, root filesystem or inherited secrets.
    Network remains shared for the fixed HTTPS probe: this is a trusted-fixture
    harness, NOT an execution boundary for arbitrary agent-generated programs.
    """
    cmd = [bwrap, "--unshare-user", "--unshare-pid", "--unshare-ipc", "--unshare-uts",
           "--die-with-parent", "--new-session", "--clearenv", "--tmpfs", "/",
           "--proc", "/proc", "--dev", "/dev", "--tmpfs", "/tmp", "--dir", "/work"]
    for path in ("/usr/bin", "/usr/lib", "/usr/lib64", "/usr/libexec", "/usr/include",
                 "/usr/share", "/bin", "/lib", "/lib64"):
        if Path(path).exists():
            cmd += ["--ro-bind", path, path]
    for path in ("/etc/ld.so.cache", "/etc/resolv.conf", "/etc/nsswitch.conf",
                 "/etc/hosts", "/etc/os-release", "/etc/ssl/certs"):
        if Path(path).exists():
            cmd += ["--ro-bind", path, path]
    if runtime_root:
        cmd += ["--ro-bind", str(runtime_root), "/opt/runtime"]
    cmd += ["--ro-bind", str(HERE), "/suite", "--bind", str(output), "/results"]
    for key, value in child_environment().items():
        cmd += ["--setenv", key, value]
    # No public bypass flag: the only CLI entry always constructs this envelope.
    entry = ("import runner; from processes import enable_subreaper; "
             "enable_subreaper(); "
             "raise SystemExit(runner.run_suite(runner.parser().parse_args()))")
    return cmd + ["--chdir", "/suite", "--", "/usr/bin/python3", "-B", "-c", entry,
                  *args, "--results-dir", "/results"]


def parser():
    ap = argparse.ArgumentParser(description="Isolation spike; always runs inside an outer safety sandbox.")
    ap.add_argument("--host", required=True, choices=["bwrap", "claude-code-srt", "codex"])
    ap.add_argument("--fixture", action="append", default=[])
    ap.add_argument("--keep", action="store_true", help="save disposable directories with results")
    ap.add_argument("--results-dir", type=Path, help="parent for a NEW run directory; existing logs are never replaced")
    ap.add_argument("--runtime-root", type=Path, help="reviewed credential-free tool installation with bin/; mounted at /opt/runtime")
    return ap


def main():
    a = parser().parse_args()
    bwrap = shutil.which("bwrap", path="/usr/bin:/bin")
    if not bwrap:
        print("ISOLATION_UNAVAILABLE: outer bubblewrap is required; no fixtures ran.", file=sys.stderr)
        return 2
    if a.runtime_root:
        runtime = a.runtime_root.resolve(strict=True)
        if not (runtime / "bin").is_dir() or runtime in (Path("/"), Path.home(), Path("/usr")):
            print("Use a dedicated credential-free runtime installation, not a home or system root.", file=sys.stderr)
            return 2
    else:
        runtime = None
    if a.results_dir:
        a.results_dir.mkdir(parents=True, exist_ok=True)
    output = Path(tempfile.mkdtemp(prefix="isolation-results-", dir=a.results_dir))
    args = ["--host", a.host]
    for fragment in a.fixture:
        args += ["--fixture", fragment]
    if a.keep:
        args.append("--keep")
    cmd = sandbox_command(bwrap, output, args, runtime)
    print(f"Results: {output}", flush=True)
    try:
        result = subprocess.run(cmd, env=child_environment(), stdin=subprocess.DEVNULL, timeout=3600)
    except (OSError, subprocess.TimeoutExpired) as error:
        print(f"ISOLATION_UNAVAILABLE: {error}", file=sys.stderr)
        return 2
    if not (output / f"{a.host}.json").is_file():
        print("ISOLATION_UNAVAILABLE: no suite summary; outer startup or execution failed.", file=sys.stderr)
        return 2
    return result.returncode if result.returncode in (0, 1, 2) else 2


if __name__ == "__main__":
    sys.exit(main())
