#!/usr/bin/env python3
"""s6863: does each replayed apply script's text reach the live tree? Reads the RS64_REPLAY_TRACE file from a scratch replay
(see rs64_replay_apply_scripts) and checks every line a step added against the live RecompiledFuncs, so it also covers the
scripts that have no MARK (the check in tools/audit_heap_addr_tests.py cannot see those). A line counts as lost when it is in
no live file after whitespace is removed. Lost lines are split into those that only log or count and the rest (BEHAVIOUR).
Controls: s4296 A14 yield must survive, s4222 vol must be lost (strip_diag_layers removes it on purpose).
Usage: tools/audit_replay_survival.py <trace.jsonl> [--lines] [live_dir]"""
import collections, json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
TRIVIAL = re.compile(r"^[\s{}();]*$|^\s*(//|/\*.*\*/\s*$)|^\s*#\s*(if|endif|else)")
DIAG = re.compile(r"fprintf|printf\(|getenv|static (unsigned |uint\d+_t |int |long |volatile )|extern |backtrace|fflush|"
                  r"rs64_(s\d+|m\d+|e\d+)\w*_(log|watch|probe|rec|stk|store|event|dump|vol|note|mark)|store_watch|_census|\+\+\w+;")


def norm(line):
    return re.sub(r"\s+", "", line)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    show = "--lines" in sys.argv
    live_dir = pathlib.Path(args[1]) if len(args) > 1 else ROOT.parent / "N64Recomp" / "RecompiledFuncs"
    live = set()
    for f in live_dir.iterdir():
        if f.is_file():
            live.update(norm(x) for x in f.read_text(errors="surrogateescape").split("\n"))
    rows = []
    for rec in map(json.loads, open(args[0], errors="surrogateescape")):
        added = [l for v in rec["files"].values() for l in v["add"] if not TRIVIAL.match(l)]
        lost = [l for l in added if norm(l) not in live]
        rows.append((rec["step"], len(added), lost))
    by = {r[0]: r for r in rows}
    noop = [r[0] for r in rows if r[1] == 0]
    part = [r for r in rows if r[1] and r[2]]
    beh = collections.Counter()
    print(f"steps {len(rows)}  no added text {len(noop)}  full survival {len(rows) - len(noop) - len(part)}  lost lines in {len(part)}")
    for step, n, lost in sorted(part, key=lambda r: -len(r[2])):
        b = [l for l in lost if not DIAG.search(l)]
        beh[step] = len(b)
        print(f"  {step:48s} added {n:6d} lost {len(lost):6d} behaviour-shaped {len(b):5d}")
        if show:
            for l in b[:12]:
                print("      ", l.strip()[:150])
    ok = True
    for name, want_lost in (("apply_s4296", False), ("apply_s4222_vol", True)):
        hit = [r for r in rows if r[0].startswith(name)]
        if not hit or any(bool(r[2]) != want_lost and r[1] for r in hit):
            ok = False
    print("controls", "ok" if ok else "FAILED")
    print("no-op steps:", " ".join(noop))
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
