#!/usr/bin/env python3
"""s7893: keep the census gates' retained scratch captures out of the owner's 7-day scratch prune.

~/.local/bin/rs64-scratch-prune.sh (launchd, every 6 h, owner-approved 2026-11-12) deletes scratch files >64 KB older than 7
days unless the EXACT path (minus a trailing .zst) appears in a tracked non-scratch repo file. The gates cite their inputs
by DIRECTORY (tools/s7651_gate_sweep.py ARGS: 'scratch/s7435') or by a '.zst' name, so neither protects a file: the
2026-11-23 08:25 and 20:25 prune runs deleted the s7392-s7399 run logs (s7865) and the s7435/s7439/s7442 sample_N.txt
profiles (s7893), turning seven closed gates RED.

This writes tools/retained_captures.txt: every existing file >64 KB under each scratch/ path literal in the gate sweep and in
tools/s7*.py (recursive globs, bare 'scratch' and soak dirs excluded), one per line, '.zst' stripped. loop.sh refreshes it
each iteration; the prune greps the working tree, so a refreshed tracked file protects new captures before its next commit.
--check exits 1 when a retained file on disk is missing from the manifest. --control: a planted dir must land in the list.
s7933: third source = what the gates actually READ (build/gate_sweep_cache.json traces, tools/gate_trace.py). 16 traced scratch
inputs (s7852-s7864 oracle/rand captures, s7751/s7754 snaps, 4 old soak logs) were missing from the manifest, protected only by
incidental ledger citations. Traced reads now join the manifest, except the rolling soak_results dir (s7415 samples whatever
logs exist; no gate verdict depends on a fixed set, and the owner's prune should keep reclaiming it)."""
import fnmatch, glob, json, os, re, sys, tempfile

# zst-ok: never opens a capture - it globs/stats paths and strips .zst itself to name both forms (s7934: the s7932 printf
# literals l%d.txt matched zst-only level logs, a false s7804 RED measured at HEAD f9142b831 too)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "tools", "retained_captures.txt")
CACHE = os.path.join(ROOT, "build", "gate_sweep_cache.json")
FMT = re.compile(r"%[-+ #0-9.]*[sdixX]")  # s7932: a printf field in a literal ("log_l%d.txt.zst" % l) is a wildcard
LIT = re.compile(r"""['"](scratch/[^'"\n ]+)['"]""")


def refs():
    r = set()
    for t in [os.path.join(ROOT, "tools", "s7651_gate_sweep.py")] + glob.glob(os.path.join(ROOT, "tools", "s7[0-9]*.py")):
        r |= set(LIT.findall(open(t, errors="replace").read()))
    r = {x.rstrip("/.,:)") for x in r}
    return sorted(x for x in r if "**" not in x and "{" not in x and x != "scratch" and not x.startswith("scratch/agent"))


def files(root, rs):
    out = set()
    for r in rs:
        for g in glob.glob(os.path.join(root, FMT.sub("*", r))):  # s7932: was r.replace("%","*"): "l%d.txt" -> "l*d.txt" matched nothing
            ps = [os.path.join(a, f) for a, _, fs in os.walk(g) for f in fs] if os.path.isdir(g) else [g]
            for p in ps:
                try:
                    if os.path.getsize(p) <= 65536:
                        continue
                except OSError:
                    continue
                rel = os.path.relpath(p, root)
                out.add(rel[:-4] if rel.endswith(".zst") else rel)
    return sorted(out)


ROLLING = ("scratch/agent/soak_results/",)


def trace_files(root, cache):
    """s7933: every existing >64 KB scratch file a cached gate run opened for reading (s7934: or only stat-ed)."""
    try:
        c = json.load(open(cache))
    except (OSError, ValueError):
        return []
    out = set()
    for e in c.values():
        tr = e.get("trace") or {}
        ds, gs = set(tr.get("dirs", [])), tr.get("globs", [])
        # s7934: a stat-only path (exists/getsize) is an input when the gate NAMED it; one it found by listing a dir or by
        # a glob is a scan hit (s7804 lint, this tool's own walk: ~880 files) and would pin whole trees from the prune.
        named = [p for p in tr.get("stats", []) if os.path.dirname(p) not in ds and not any(fnmatch.fnmatch(p, g) for g in gs)]
        for p in tr.get("reads", []) + named:
            rel = os.path.relpath(p, root)
            if not rel.startswith("scratch/") or rel.startswith(ROLLING) or (p in named and rel.startswith("scratch/agent/")):
                continue
            if not os.path.isfile(os.path.join(root, rel)):
                continue
            try:
                if os.path.getsize(os.path.join(root, rel)) <= 65536:
                    continue
            except OSError:
                continue
            out.add(rel[:-4] if rel.endswith(".zst") else rel)
    return sorted(out)


def control():
    with tempfile.TemporaryDirectory() as d:
        os.makedirs(os.path.join(d, "scratch", "plant", "sub"))
        open(os.path.join(d, "scratch", "plant", "sub", "big.txt.zst"), "wb").write(b"x" * 70000)
        open(os.path.join(d, "scratch", "plant", "small.txt"), "wb").write(b"x")
        os.makedirs(os.path.join(d, "scratch", "fmt"))
        for n in ("log_l1.txt.zst", "log_l12.txt.zst"):  # s7932: the s7516/s7517 '%d' row shape
            open(os.path.join(d, "scratch", "fmt", n), "wb").write(b"x" * 70000)
        got = files(d, ["scratch/plant", "scratch/fmt/log_l%d.txt.zst"])
        # s7933: traced reads - a big read file lands, a small one, a rolling soak log and a gone file do not
        os.makedirs(os.path.join(d, "scratch", "tr")); os.makedirs(os.path.join(d, "scratch", "agent", "soak_results"))
        for n, sz in (("tr/read.log.zst", 70000), ("tr/tiny.log", 10), ("agent/soak_results/x.log.zst", 70000)):
            open(os.path.join(d, "scratch", n), "wb").write(b"x" * sz)
        cp = os.path.join(d, "cache.json")
        open(os.path.join(d, "scratch", "tr", "statonly.bin.zst"), "wb").write(b"x" * 70000)  # s7934: exists()-only input
        os.makedirs(os.path.join(d, "scratch", "scan"))  # s7934: found by listing its dir -> scan hit, not pinned
        open(os.path.join(d, "scratch", "scan", "hit.bin.zst"), "wb").write(b"x" * 70000)
        open(os.path.join(d, "scratch", "agent", "x.log"), "wb").write(b"x" * 70000)
        json.dump({"k": {"trace": {"reads": [os.path.join(d, "scratch", n) for n in
                   ("tr/read.log.zst", "tr/tiny.log", "agent/soak_results/x.log.zst", "tr/gone.bin")],
                   "stats": [os.path.join(d, "scratch", n) for n in ("tr/statonly.bin.zst", "scan/hit.bin.zst", "agent/x.log")],
                   "dirs": [os.path.join(d, "scratch", "scan")]}}}, open(cp, "w"))
        tgot = trace_files(d, cp)
        tmut = trace_files(d, os.path.join(d, "nocache.json"))
    ok = got == ["scratch/fmt/log_l1.txt", "scratch/fmt/log_l12.txt", "scratch/plant/sub/big.txt"]
    tok = tgot == ["scratch/tr/read.log", "scratch/tr/statonly.bin"] and tmut == []
    print(f"CONTROL planted dir -> {got} {'PASS' if ok else 'FAIL'}")
    print(f"CONTROL s7933 planted trace -> {tgot} (missing cache -> {tmut}) {'PASS' if tok else 'FAIL'}")
    return ok and tok


def main(a):
    if "--control" in a:
        return 0 if control() else 3
    rs = refs(); lit = files(ROOT, rs); tr = trace_files(ROOT, CACHE)
    fs = sorted(set(lit) | set(tr))
    if "--check" in a:
        have = set(open(OUT).read().split()) if os.path.exists(OUT) else set()
        miss = [f for f in fs if f not in have]
        print(f"s7893 retained={len(fs)} manifest={len(have)} missing={len(miss)}" + (f" e.g. {miss[:3]}" if miss else ""))
        # s7932: second source - the argv the sweep actually passes (ARGS, % already expanded), not the literal scan
        sys.path.insert(0, os.path.join(ROOT, "tools"))
        argv0, sys.argv = sys.argv, [sys.argv[0]]
        import s7651_gate_sweep as gs
        sys.argv = argv0
        argv_files = files(ROOT, sorted({x for a, _ in gs.ARGS.values() for x in a if x.startswith("scratch/")}))
        amiss = [f for f in argv_files if f not in have]
        print(f"s7932 sweep-argv retained={len(argv_files)} missing={len(amiss)}" + (f" e.g. {amiss[:3]}" if amiss else ""))
        tmiss = [f for f in tr if f not in have]
        print(f"s7933 sweep-trace retained={len(tr)} missing={len(tmiss)}" + (f" e.g. {tmiss[:3]}" if tmiss else ""))
        return 1 if (miss or amiss or tmiss) else 0
    with open(OUT, "w") as fh:
        fh.write("# s7893 generated by tools/s7893_retained_manifest.py: exact retained-capture paths the census gates read.\n"
                 "# Citing them here keeps ~/.local/bin/rs64-scratch-prune.sh from deleting them. Do not hand-edit.\n")
        fh.writelines(f + "\n" for f in fs)
    print(f"s7893 wrote {len(fs)} paths from {len(rs)} scratch refs (+{len(set(tr) - set(lit))} s7933 traced-only)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
