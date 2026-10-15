"""Run candidate duplication tools against the fixtures.

Each case is the base tree plus one added file. Only pairs that involve the added
file count; this stands in for the proposal's changed-lines rule.
"""
import argparse
import csv
import json
import os
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
FIXTURES = os.path.join(HERE, "fixtures")
CASES = {"f1": "terrain_pass.cpp", "f2": "terrain_pass.cpp", "f3": "tonemap_pass.cpp"}
TOKENS = [20, 30, 40, 50, 60, 65, 70, 75, 100, 150, 200, 245, 250, 300]
NORMALISE = ["--ignore-identifiers", "--ignore-literals"]
CPD_MODES = {"exact": [], "ids-literals": NORMALISE}
JSCPD_MODES = {
    "exact": [],
    "ids-literals": NORMALISE,
    "ids-literals+gap2": NORMALISE + ["--max-gap-lines", "2"],
    "ids-literals+gap4": NORMALISE + ["--max-gap-lines", "4"],
    "ids-literals+gap8": NORMALISE + ["--max-gap-lines", "8"],
}
CPD_NS = "{https://pmd-code.org/schema/cpd-report}"
GIT = ["git", "-c", "user.name=spike", "-c", "user.email=spike@example.invalid"]


def assemble(case, root):
    src = os.path.join(root, "src")
    shutil.copytree(os.path.join(FIXTURES, "base", "src"), src)
    shutil.copy(os.path.join(FIXTURES, case, CASES[case]), os.path.join(src, "render"))
    return src


def run(command, cwd=None, env=None):
    proc = subprocess.run(command, cwd=cwd, env=env, capture_output=True, text=True)
    if proc.returncode != 0:
        sys.exit(f"{' '.join(command)} failed ({proc.returncode}): {proc.stderr}")
    return proc


def git_commit(root, message):
    run(GIT + ["add", "-A"], cwd=root)
    run(GIT + ["commit", "-q", "--allow-empty", "-m", message], cwd=root)


def cpd(args, src, added, tokens, extra):
    env = dict(os.environ, JAVA_HOME=args.java_home,
               PATH=os.path.join(args.java_home, "bin") + os.pathsep + os.environ["PATH"])
    with tempfile.TemporaryDirectory() as cwd:
        out = run([args.pmd, "cpd", "--language", "cpp", "--minimum-tokens", str(tokens),
                   "--format", "xml", "--no-fail-on-violation", *extra, src], cwd=cwd, env=env)
    pairs = []
    for dup in ET.fromstring(out.stdout).iter(CPD_NS + "duplication"):
        files = [(os.path.basename(f.get("path")), int(f.get("line")), int(f.get("endline")))
                 for f in dup.iter(CPD_NS + "file")]
        if any(name == added for name, _, _ in files):
            pairs.append((int(dup.get("tokens")), files))
    return pairs


def jscpd(args, src, added, tokens, extra, cwd=None):
    with tempfile.TemporaryDirectory() as out_dir, tempfile.TemporaryDirectory() as empty:
        run(["node", args.jscpd, "--no-tips", "-s", "--min-tokens", str(tokens), "--min-lines", "1",
             "--cross-formats", "c,c-header,cpp,cpp-header", "--reporters", "json",
             "--output", out_dir, *extra, src], cwd=cwd or empty)
        report = json.load(open(os.path.join(out_dir, "jscpd-report.json")))
    pairs = []
    for dup in report["duplicates"]:
        files = [(os.path.basename(f["name"]), f["start"], f["end"])
                 for f in (dup["firstFile"], dup["secondFile"])]
        if any(name == added for name, _, _ in files):
            pairs.append((dup["tokens"], files, dup.get("isNew")))
    return pairs


def summary(pairs):
    return f"{len(pairs)} pairs (max {max([p[0] for p in pairs], default=0)} tokens)"


def sweep(tool, modes, args):
    for mode, extra in modes.items():
        for tokens in TOKENS:
            row = []
            for case, added in CASES.items():
                with tempfile.TemporaryDirectory() as root:
                    row.append(f"{case}: {summary(tool(args, assemble(case, root), added, tokens, extra))}")
            print(f"{mode:18} min-tokens={tokens:3}  " + "  ".join(row))
    for case, added in CASES.items():
        with tempfile.TemporaryDirectory() as root:
            for tokens, files, *_ in tool(args, assemble(case, root), added, 100, NORMALISE):
                print(f"ids-literals min-tokens=100 {case}: {tokens} tokens {files}")


def dolos(args):
    for k in [None, 12, 16, 30]:
        for case, added in CASES.items():
            with tempfile.TemporaryDirectory() as root, tempfile.TemporaryDirectory() as out:
                render = os.path.join(assemble(case, root), "render")
                files = sorted(os.path.join(render, name) for name in os.listdir(render))
                run(["node", args.dolos, "run", "-l", "cpp", "-f", "csv", "-o", os.path.join(out, "r"),
                     *(["-k", str(k)] if k else []), *files])
                rows = [r for r in csv.DictReader(open(os.path.join(out, "r", "pairs.csv")))
                        if added in (os.path.basename(r["leftFilePath"]), os.path.basename(r["rightFilePath"]))]
            top = max(rows, key=lambda r: float(r["similarity"]))
            pair = f"{os.path.basename(top['leftFilePath'])}~{os.path.basename(top['rightFilePath'])}"
            print(f"k={k or 'default':7} {case}: {pair} similarity={float(top['similarity']):.2f} "
                  f"longest-fragment={top['longestFragment']}")


def lizard(args):
    for case, added in CASES.items():
        with tempfile.TemporaryDirectory() as root:
            out = run([args.lizard, "-Eduplicate", assemble(case, root)]).stdout
        blocks = out.split("Duplicate block:")[1:]
        print(f"{case}: {sum(1 for b in blocks if added in b)} duplicate blocks involving {added}")


def add_markers(path, start, end):
    lines = open(path).read().splitlines()
    lines.insert(8, start)
    lines.insert(len(lines) - 1, end)
    open(path, "w").write("\n".join(lines) + "\n")


def probes(args):
    added = CASES["f1"]
    with tempfile.TemporaryDirectory() as root:
        src = assemble("f1", root)
        add_markers(os.path.join(src, "render", added), "// CPD-OFF", "// CPD-ON")
        print(f"cpd, CPD-OFF/CPD-ON around the F1 copy: {summary(cpd(args, src, added, 100, NORMALISE))}")
    with tempfile.TemporaryDirectory() as root:
        src = assemble("f1", root)
        add_markers(os.path.join(src, "render", added), "// jscpd:ignore-start", "// jscpd:ignore-end")
        print(f"jscpd, ignore-start/end around the F1 copy: {summary(jscpd(args, src, added, 100, NORMALISE))}")

    for name, content in [(".jscpd.json", {"ignore": ["**/terrain_pass.cpp"]}),
                          ("package.json", {"name": "x", "jscpd": {"ignore": ["**/terrain_pass.cpp"]}})]:
        with tempfile.TemporaryDirectory() as root:
            src = assemble("f1", root)
            json.dump(content, open(os.path.join(src, name), "w"))
            inside = summary(jscpd(args, ".", added, 100, NORMALISE, cwd=src))
            outside = summary(jscpd(args, src, added, 100, NORMALISE))
            print(f"jscpd, {name} ignoring the copy: run inside tree {inside}; run outside {outside}")

    with tempfile.TemporaryDirectory() as root:
        src = assemble("f1", root)
        run(GIT + ["init", "-q", "-b", "main"], cwd=root)
        git_commit(root, "base")
        open(os.path.join(root, ".gitignore"), "w").write(f"src/render/{added}\n")
        default = summary(jscpd(args, "src", added, 100, NORMALISE, cwd=root))
        disabled = summary(jscpd(args, "src", added, 100, NORMALISE + ["--no-gitignore"], cwd=root))
        print(f"jscpd, .gitignore lists the committed copy: default {default}; --no-gitignore {disabled}")
        print(f"cpd, .gitignore lists the committed copy: {summary(cpd(args, src, added, 100, NORMALISE))}")

    with tempfile.TemporaryDirectory() as root:
        run(GIT + ["init", "-q", "-b", "main"], cwd=root)
        git_commit(root, "root")
        shutil.copytree(os.path.join(FIXTURES, "base", "src"), os.path.join(root, "src"))
        shutil.copy(os.path.join(FIXTURES, "f1", added), os.path.join(root, "src", "render", "old_copy.cpp"))
        git_commit(root, "base")
        run(GIT + ["checkout", "-q", "-b", "head"], cwd=root)
        shutil.copy(os.path.join(FIXTURES, "f2", added), os.path.join(root, "src", "render"))
        git_commit(root, "head")
        pairs = jscpd(args, "src", "forward_pass.cpp", 100, NORMALISE + ["--max-gap-lines", "4",
                      "--baseline-from-ref", "main"], cwd=root)
        for tokens, files, is_new in pairs:
            print(f"jscpd --baseline-from-ref main: {'new' if is_new else 'old'} {tokens} tokens {files}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", choices=["cpd", "jscpd", "dolos", "lizard", "probes"])
    parser.add_argument("--pmd", help="PMD launcher, pmd-bin-VERSION/bin/pmd")
    parser.add_argument("--java-home", help="JDK for PMD")
    parser.add_argument("--jscpd", help="node_modules/.bin/jscpd")
    parser.add_argument("--dolos", help="node_modules/.bin/dolos")
    parser.add_argument("--lizard", help="lizard executable")
    args = parser.parse_args()
    if args.run == "cpd":
        sweep(cpd, CPD_MODES, args)
    elif args.run == "jscpd":
        sweep(jscpd, JSCPD_MODES, args)
    elif args.run == "dolos":
        dolos(args)
    elif args.run == "lizard":
        lizard(args)
    else:
        probes(args)


if __name__ == "__main__":
    main()
