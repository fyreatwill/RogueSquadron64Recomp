#!/usr/bin/env python3
"""s7934 stat-key gate: gate_trace.py records stat-only paths (os.stat/lstat: exists, isfile, getsize, pathlib) in "stats",
and tools/s7651_gate_sweep.py fingerprint() keys them, so a gate whose verdict depends only on a path EXISTING (or its size)
is re-run when that changes, and tools/s7893_retained_manifest.py protects such >64 KB scratch inputs from the prune.
--controls: (1) the tracer's own planted arms (exists/getsize/pathlib -> stats, open -> reads, no-wrap mutation -> nothing);
(2) fingerprint arms on a planted stat-only file: delete and resize must CHANGE the key, an untouched re-key must be EQUAL,
and the mutation (same change, trace without "stats") must stay EQUAL - i.e. before s7934 the delete was invisible."""
import importlib.util, os, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    p = subprocess.run([sys.executable, os.path.join(HERE, "gate_trace.py"), "--selftest"], capture_output=True, text=True)
    print("\n".join("tracer " + l for l in p.stdout.strip().split("\n")))
    spec = importlib.util.spec_from_file_location("s7651_gate_sweep", os.path.join(HERE, "s7651_gate_sweep.py"))
    sw = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sw)
    with tempfile.TemporaryDirectory() as d:
        f = os.path.join(d, "statonly.bin")
        open(f, "wb").write(b"x" * 10)
        tr = {"reads": [], "dirs": [], "globs": [], "stats": [f]}
        mut = {"reads": [], "dirs": [], "globs": []}
        k0, m0 = sw.fingerprint(["a"], tr), sw.fingerprint(["a"], mut)
        same = sw.fingerprint(["a"], tr) == k0
        open(f, "wb").write(b"x" * 20)
        resize = sw.fingerprint(["a"], tr) != k0
        os.unlink(f)
        delete = sw.fingerprint(["a"], tr) != k0
        mutation = sw.fingerprint(["a"], mut) == m0
    ok = p.returncode == 0 and same and resize and delete and mutation
    c = lambda b: "CHANGED" if b else "EQUAL"
    print(f"CONTROL fingerprint delete={c(delete)} resize={c(resize)} same={'EQUAL' if same else 'CHANGED'} "
          f"mutation={'EQUAL' if mutation else 'CHANGED'} {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
