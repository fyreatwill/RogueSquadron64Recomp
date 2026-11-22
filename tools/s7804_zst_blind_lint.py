#!/usr/bin/env python3
"""s7804 zst-blind lint: no swept or CURRENT-TRUTH-cited tool may read a retained scratch/ capture by its raw name after the
capture was zstd-compressed (the s7801/s7802/s7803 class: s7726, s7753, s7756, s7441, s7442, s7773 each silently read 0 windows /
fewer logs / NEEDS-INPUT once their inputs became *.zst).

A purely static rule is noisy (66 of 271 tools carry a capture-like literal: reviewed .tsv tables, compile_commands.json, ...),
so the verdict is decided by the filesystem:
  for every tool that does NOT import rs64_zopen (and carries no `# zst-ok: <reason>` waiver), every string literal ending in a
  capture extension is expanded (format holes -> *) against the tool's input dirs (scratch/ paths in its sweep ARGS row, scratch/
  literals in its source, the repo root) and their direct subdirs. A .zst match whose raw sibling is absent is a capture the tool
  can no longer see -> RED. Literal matched only raw -> fine. Nothing matched at all -> NOINPUT (counted, not RED).
Controls (same run): a planted tool globbing sample_*.txt over a dir holding only sample_1.txt.zst must read RED; the same tool
importing rs64_zopen must read GREEN; a raw-only dir must read GREEN.
Exit 0 iff 0 RED and CONTROLS PASS."""
import glob, importlib.util, os, re, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIT = re.compile(r"""(['"])([^'"\n]*\.(?:txt|log|bin|cap|tlog|raw|dat|csv|out))\1""")
SCR = re.compile(r"""['"](scratch/[^'"\n]+)['"]""")
HOLE = re.compile(r"%[0-9.]*[sdx]|\{[^}]*\}")


def sweep_tables():
    spec = importlib.util.spec_from_file_location("s7651", os.path.join(ROOT, "tools", "s7651_gate_sweep.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.ARGS, m.EXTRA_GATES


def tool_set(args, extra):
    tools = {f for f in os.listdir(os.path.join(ROOT, "tools")) if re.match(r"s7\d+_.*_census\.py$", f) or f in extra}
    tools |= set(args)
    ct = open(os.path.join(ROOT, "docs", "CURRENT-TRUTH.md"), errors="replace").read()
    tools |= set(re.findall(r"tools/([a-z0-9_]+\.py)", ct))
    return sorted(f for f in tools if os.path.exists(os.path.join(ROOT, "tools", f)))


def input_dirs(src, argv, base):
    ds = {base}
    for a in list(argv) + SCR.findall(src):
        a = HOLE.sub("*", a)
        for p in glob.glob(os.path.join(base, a)) or [os.path.join(base, a)]:
            d = p if os.path.isdir(p) else os.path.dirname(p)
            if os.path.isdir(d):
                ds.add(d)
    out = set(ds)
    for d in ds:
        if d != base:
            out |= {os.path.join(d, e) for e in os.listdir(d) if os.path.isdir(os.path.join(d, e))}
    return sorted(out)


def lint(src, argv, base):
    """-> (verdict, detail). verdict in GREEN / RED / NOINPUT / WAIVED / ZOPEN."""
    if "rs64_zopen" in src:
        return "ZOPEN", ""
    if re.search(r"#\s*zst-ok:\s*\S", src):
        return "WAIVED", ""
    lits = sorted({HOLE.sub("*", m.group(2)) for m in LIT.finditer(src)})
    if not lits:
        return "GREEN", "no capture literal"
    dirs = input_dirs(src, argv, base)
    blind, seen = [], 0
    for l in lits:
        if not l.startswith("/") and "/" in l:  # repo-relative path ('scratch/x/*.log')
            roots = [base]
        else:  # bare name or a '/name' suffix joined onto a dir variable: look in every input dir
            l, roots = l.lstrip("/"), dirs
        for d in roots:
            pat = os.path.join(d, l)
            raw = glob.glob(pat)
            zst = [z for z in glob.glob(pat + ".zst") if not os.path.exists(z[:-4])]
            seen += len(raw) + len(zst)
            if zst:
                blind.append(f"{os.path.relpath(pat, base)}: zst-only={len(zst)} raw={len(raw)}")
    if blind:
        return "RED", "; ".join(blind[:4]) + (f" (+{len(blind) - 4})" if len(blind) > 4 else "")
    return ("GREEN", f"raw matches {seen}") if seen else ("NOINPUT", f"{len(lits)} literals, no retained match")


def controls():
    with tempfile.TemporaryDirectory() as d:
        os.makedirs(os.path.join(d, "scratch", "cap"))
        open(os.path.join(d, "scratch", "cap", "sample_1.txt.zst"), "w").write("x")
        os.makedirs(os.path.join(d, "scratch", "rawcap"))
        open(os.path.join(d, "scratch", "rawcap", "sample_1.txt"), "w").write("x")
        blind = "import glob\nfor f in glob.glob(d + '/sample_*.txt'): print(open(f).read())\n"
        fixed = "from rs64_zopen import zopen\n" + blind
        got = (lint(blind, ["scratch/cap"], d)[0], lint(fixed, ["scratch/cap"], d)[0], lint(blind, ["scratch/rawcap"], d)[0])
    ok = got == ("RED", "ZOPEN", "GREEN")
    print(f"CONTROL planted zst-only glob / same with zopen / raw-only dir -> {got} {'PASS' if ok else 'FAIL'}")
    return ok


def main():
    cok = controls()
    args, extra = sweep_tables()
    rows = []
    for f in tool_set(args, extra):
        src = open(os.path.join(ROOT, "tools", f), errors="replace").read()
        argv = args.get(f, ([], ""))[0]
        v, det = lint(src, argv, ROOT)
        rows.append((f, v, det))
        if v == "RED" or "-v" in sys.argv:
            print(f"  {v:8s} {f}  {det}")
    from collections import Counter
    c = Counter(v for _, v, _ in rows)
    red = c.get("RED", 0)
    print(f"s7804 tools={len(rows)} zopen={c.get('ZOPEN', 0)} waived={c.get('WAIVED', 0)} green={c.get('GREEN', 0)} "
          f"noinput={c.get('NOINPUT', 0)} blind={red}")
    if not cok:
        sys.exit(3)
    print(f"VERDICT {'GREEN' if red == 0 else 'RED'}: {red} tools read a zst-only retained capture by its raw name")
    sys.exit(1 if red else 0)


if __name__ == "__main__":
    main()
