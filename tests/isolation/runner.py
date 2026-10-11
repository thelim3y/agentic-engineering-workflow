#!/usr/bin/env python3
"""Isolation conformance runner (spike). Python 3 standard library only.

For each fixture and host adapter it runs three things, each in a fresh
disposable environment:
  (a) control disabled : the attack must SUCCEED, or the fixture is invalid
  (b) control enabled  : the attack must be BLOCKED
  (c) positive control : an allowed operation must succeed in the same sandbox
Verdict per cell: blocked | allowed | invalid-fixture | too-strict | untested.
Raw output of every command goes to results/<host>.log; a machine summary to
results/<host>.json. The runner judges from outside the sandbox; nothing a
fixture prints is trusted for the verdict.

Usage: python3 runner.py --host <adapter name> [--fixture <name-fragment>]...
"""
import argparse, json, os, secrets, shutil, signal, socket, subprocess, sys, threading, time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIXTURES = HERE / "fixtures"
ADAPTERS = HERE / "adapters"
RUN_ROOT = Path(os.environ.get("ISO_RUN_ROOT", str(Path.home() / "iso-runs")))
NET_HOST = os.environ.get("ISO_NET_HOST", "github.com")
EXIT_UNSUPPORTED = 64
CANCEL_FIXTURES = {"16-cancellation"}
CONTRACT_FIXTURES = {"20-unsupported-config", "21-failure-propagation"}

GIT_ENV = {"GIT_AUTHOR_NAME": "spike", "GIT_AUTHOR_EMAIL": "spike@example.invalid",
           "GIT_COMMITTER_NAME": "spike", "GIT_COMMITTER_EMAIL": "spike@example.invalid",
           "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null"}


class Log:
    def __init__(self, path):
        self.f = open(path, "w")
    def __call__(self, *parts):
        line = " ".join(str(p) for p in parts)
        self.f.write(line + "\n"); self.f.flush()
    def block(self, title, text):
        self("----- " + title); self(text.rstrip("\n") if text else "(no output)"); self("-----")


def sh(cmd, cwd=None, env=None):
    return subprocess.run(cmd, cwd=cwd, env=env, text=True, capture_output=True)


def tree_hash(d):
    out = sh(["sh", "-c", "find . -type f -not -path './.git/*' -print0 | sort -z | xargs -0 sha256sum | sha256sum | cut -c1-64"], cwd=d)
    return out.stdout.strip()


class Env:
    """One disposable fixture environment. Nothing here touches the repo."""
    def __init__(self, tag):
        RUN_ROOT.mkdir(parents=True, exist_ok=True)
        self.t = Path(subprocess.check_output(["mktemp", "-d", "-p", str(RUN_ROOT), "r.XXXXXX"], text=True).strip())
        (self.t/"TAG").write_text(tag + "\n")  # which host/fixture/run this directory served
        t = self.t
        if len(str(t/"fakeagent"/"agent.sock")) > 100:
            raise RuntimeError("run root path too long for AF_UNIX; set ISO_RUN_ROOT to a shorter path")
        self.ws, self.prot, self.hidden, self.evidence = t/"ws", t/"prot", t/"hidden", t/"evidence"
        self.fake_home, self.sock_dir, self.plant, self.baseline = t/"fakehome", t/"fakeagent", t/"plant", t/"baseline"
        for d in (self.ws/"config", self.prot/"tools", self.prot/"report", self.hidden, self.evidence,
                  self.fake_home/".config"/"fakeapp", self.sock_dir, self.plant, self.baseline):
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
        g = lambda *a: subprocess.run(["git", "-C", str(self.prot), *a], check=True, capture_output=True, env={**os.environ, **GIT_ENV})
        g("init", "-q", "-b", "main"); g("add", "-A"); g("commit", "-q", "-m", "protected inputs")
        g("checkout", "-q", "-b", "weak"); (self.prot/"test_protected.py").write_text("def test_protected():\n    assert True\n")
        g("commit", "-q", "-am", "weakened"); g("checkout", "-q", "main")
        subprocess.run(["git", "-C", str(self.ws), "init", "-q", "-b", "main"], check=True, capture_output=True)
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
        p.write_text("".join(f"{k}='{v}'\n" for k, v in kv.items()))
        return p, {k: str(v) for k, v in kv.items()}

    def snapshot(self):
        (self.baseline/"prot.sha256").write_text(tree_hash(self.prot))
        (self.baseline/"evidence.sha256").write_text(tree_hash(self.evidence))

    def close(self):
        self._stop = True
        try: self._sock_srv.close()
        except OSError: pass


class Runner:
    def __init__(self, host, keep):
        self.host = host; self.adapter = ADAPTERS/f"{host}.sh"; self.keep = keep
        if not self.adapter.exists(): sys.exit(f"no adapter {self.adapter}")
        (HERE/"results").mkdir(exist_ok=True)
        self.log = Log(HERE/"results"/f"{host}.log")
        self.info = dict(l.split("=", 1) for l in sh(["sh", str(self.adapter), "info"]).stdout.splitlines() if "=" in l)
        self.rows = []

    def run_phase(self, env, fixture, phase, control, net="deny", require="", cancel_after=None):
        pol, polenv = env.policy(control, net, require)
        env.snapshot()
        decoy = subprocess.Popen(["python3", "-c", "import time; time.sleep(60)", env.marker],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        cmd = ["sh", str(self.adapter), "run", str(pol), str(fixture), phase]
        run_env = {**os.environ, **GIT_ENV, **polenv, "FAKE_TOKEN": env.token}
        self.log(f"$ ISO_CONTROL={control} ISO_NET={net} ISO_REQUIRE='{require}' FAKE_TOKEN=<planted> {' '.join(cmd)}")
        t0 = time.time()
        p = subprocess.Popen(cmd, env=run_env, cwd=str(env.ws), text=True, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT, start_new_session=True)
        cancelled = False; out = ""
        try:
            if cancel_after:
                try:
                    out, _ = p.communicate(timeout=cancel_after)
                except subprocess.TimeoutExpired:
                    os.killpg(p.pid, signal.SIGKILL); cancelled = True
                    out, _ = p.communicate(timeout=10)
                    time.sleep(0.3); early = self.survivors(env)
                    self.log(f"[runner] sent SIGKILL to process group {p.pid} after {cancel_after}s; processes still referencing the run dir 0.3s later: {early or 'none'}; waiting 6s for late effects")
                    time.sleep(6)
            else:
                out, _ = p.communicate(timeout=120)
        except subprocess.TimeoutExpired:
            os.killpg(p.pid, signal.SIGKILL); out, _ = p.communicate(); out += "\n[runner] TIMEOUT, killed"
        rc = p.returncode
        survivors = self.survivors(env) if cancelled else []
        decoy.kill()
        self.log.block(f"{fixture.stem} {phase} control={control} rc={rc} {time.time()-t0:.1f}s", out)
        jphase = "judge_attack" if phase == "attack" else "judge_positive"
        j = sh(["sh", str(fixture), jphase], env={**os.environ, **polenv})
        verdict = (j.stdout.strip().splitlines() or ["NO_VERDICT"])[-1]
        self.log(f"[judge] {fixture.stem} {jphase} control={control}: {verdict} {j.stderr.strip()}")
        if cancelled:
            self.log(f"[runner] after the wait, processes still referencing the run dir: {survivors or 'none'}; outputs of a cancelled run are never accepted by the runner")
        return {"rc": rc, "verdict": verdict, "cancelled": cancelled, "survivors": survivors, "unsupported": rc == EXIT_UNSUPPORTED and "ISOLATION_UNSUPPORTED" in out, "output_tail": out[-600:]}

    def survivors(self, env):
        """PIDs outside the runner whose command line references this run directory."""
        found = []
        for pid in os.listdir("/proc"):
            if not pid.isdigit() or int(pid) == os.getpid(): continue
            try: c = open(f"/proc/{pid}/cmdline", "rb").read()
            except OSError: continue
            if str(env.t).encode() in c: found.append(pid)
        return found

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
                        res[f"{phase}/{control}"] = {"rc": r["rc"], "expected": want, "ok": r["rc"] == want}
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
                            res[f"{label}/{control}"] = {"typed_error": r["unsupported"], "rc": r["rc"], "fixture_ran": r["verdict"] == "CONTRACT_VIOLATED"}
                        finally:
                            e.close(); self.cleanup(e)
                ok = all(v["typed_error"] and not v["fixture_ran"] for v in res.values())
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
                if any(r["unsupported"] for r in results.values()): verdict = "unsupported"
                elif d != "ATTACK_SUCCEEDED": verdict = "invalid-fixture"
                elif en == "ATTACK_SUCCEEDED": verdict = "allowed"
                elif pos != "POSITIVE_OK": verdict = "too-strict"
                else: verdict = "blocked"
                row.update({"kind": "attack", "disabled": d, "enabled": en, "positive": pos, "verdict": verdict,
                            "survivors_disabled": results["disabled"]["survivors"], "survivors_enabled": results["enabled"]["survivors"]})
        except Exception as ex:  # a crashed fixture is untested, never passed
            row.update({"verdict": "untested", "error": repr(ex)}); self.log(f"[runner] ERROR {ex!r}")
        self.log(f"[result] {name} {self.host}: {row['verdict']}")
        self.rows.append(row); return row

    def cleanup(self, e):
        if not self.keep: shutil.rmtree(e.t, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--host", required=True); ap.add_argument("--fixture", action="append", default=[])
    ap.add_argument("--keep", action="store_true", help="keep disposable directories")
    a = ap.parse_args()
    fixtures = sorted(p for p in FIXTURES.glob("[0-9][0-9]-*.sh") if not a.fixture or any(f in p.stem for f in a.fixture))
    r = Runner(a.host, a.keep)
    r.log(f"##### run start {datetime.now(timezone.utc).isoformat()} host={a.host} info={r.info} run_root={RUN_ROOT} net_host={NET_HOST}")
    for f in fixtures: r.run_fixture(f)
    summary = {"host": a.host, "info": r.info, "when": datetime.now(timezone.utc).isoformat(), "rows": r.rows}
    (HERE/"results"/f"{a.host}.json").write_text(json.dumps(summary, indent=1))
    print(f"| fixture | {a.host}: disabled | enabled | positive | verdict |"); print("|---|---|---|---|---|")
    for row in r.rows:
        print(f"| {row['fixture']} | {row.get('disabled','-')} | {row.get('enabled','-')} | {row.get('positive','-')} | {row['verdict']} |")

if __name__ == "__main__":
    main()
