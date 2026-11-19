#!/usr/bin/env python3
"""s7651 gate sweep: run every closed-class census (tools/s7*_census.py) in one pass and say which have gone RED.

s7651 found 4 "closed" rerun-after-change gates (s7375, s7430, s7533, s7535) exiting nonzero after later sessions added code
in their scope (G6b controls, G6c stand-ins, s7535-s7647 instruments): nothing re-ran them, so CURRENT-TRUTH still called
them closed. This runs them all (with --controls when the tool takes it), 6 at a time, 300 s cap each, and classifies:
  GREEN      exit 0
  NEEDS-ARGS argparse usage / IndexError on sys.argv / missing input file: the tool needs an input (not a drift signal)
  RED        any other nonzero exit: drift or a real defect, triage by hand
Positive control (iron rule 1): a planted tool that exits 1 must read RED and one that exits 0 GREEN, else exit 3.
Usage: s7651_gate_sweep.py [--jobs N] [--only REGEX] [--tsv OUT]      exit 0 iff no RED (NEEDS-ARGS allowed)."""
import concurrent.futures as cf, os, re, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARGS_SIG = re.compile(r"IndexError: list index out of range|usage: |error: unrecognized arguments|error: the following arguments"
                      r"|FileNotFoundError|No such file or directory|struct\.error: unpack_from")


def run(path):
    src = open(path, errors="replace").read()
    a = ["--controls"] if "--controls" in src else []
    try:
        p = subprocess.run([sys.executable, path] + a, cwd=ROOT, capture_output=True, text=True, errors="replace", timeout=300)
        rc, out = p.returncode, p.stdout + p.stderr
    except subprocess.TimeoutExpired:
        return os.path.basename(path), "RED", "timeout", "timeout 300 s"
    tail = " | ".join(l.strip() for l in out.strip().split("\n")[-2:])[:200]
    if rc == 0:
        return os.path.basename(path), "GREEN", rc, tail
    if "--controls" in a and "unrecognized arguments: --controls" in out:  # mentions --controls in text only: retry bare
        p = subprocess.run([sys.executable, path], cwd=ROOT, capture_output=True, text=True, errors="replace", timeout=300)
        rc, out = p.returncode, p.stdout + p.stderr
        tail = " | ".join(l.strip() for l in out.strip().split("\n")[-2:])[:200]
        if rc == 0:
            return os.path.basename(path), "GREEN", rc, tail
    return os.path.basename(path), "NEEDS-ARGS" if ARGS_SIG.search(out[-3000:]) else "RED", rc, tail


def main():
    jobs = int(sys.argv[sys.argv.index("--jobs") + 1]) if "--jobs" in sys.argv else 6
    only = re.compile(sys.argv[sys.argv.index("--only") + 1]) if "--only" in sys.argv else None
    tsv = sys.argv[sys.argv.index("--tsv") + 1] if "--tsv" in sys.argv else None
    with tempfile.TemporaryDirectory() as d:
        bad, good = os.path.join(d, "ctl_red_census.py"), os.path.join(d, "ctl_green_census.py")
        open(bad, "w").write("import sys\nprint('UNCLASSIFIED 1')\nsys.exit(1)\n")
        open(good, "w").write("print('ok')\n")
        c = {r[0]: r[1] for r in map(run, (bad, good))}
    cpass = c == {"ctl_red_census.py": "RED", "ctl_green_census.py": "GREEN"}
    print("[s7651] control planted red/green ->", c, "PASS" if cpass else "FAIL")
    if not cpass:
        sys.exit(3)
    tools = sorted(os.path.join(ROOT, "tools", f) for f in os.listdir(os.path.join(ROOT, "tools"))
                   if re.match(r"s7\d+_.*_census\.py$", f) and (not only or only.search(f)))
    with cf.ThreadPoolExecutor(jobs) as ex:
        rows = sorted(ex.map(run, tools))
    from collections import Counter
    for name, cls, rc, tail in rows:
        if cls != "GREEN":
            print(f"  {cls:10s} rc={rc} {name}  {tail}")
    if tsv:
        with open(tsv, "w") as o:
            o.writelines(f"{n}\t{c}\t{r}\t{t}\n" for n, c, r, t in rows)
    print("[s7651] gates", len(rows), dict(Counter(r[1] for r in rows)))
    sys.exit(1 if any(r[1] == "RED" for r in rows) else 0)


if __name__ == "__main__":
    main()
