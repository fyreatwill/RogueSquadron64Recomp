#!/usr/bin/env python3
"""s7655 shared clang-AST cache freshness for the census tools (s7613 HP, s7614 HM, s7615 DQ, s7616 RQ).

Those censuses compare a live regex scan with a clang -ast-dump second source cached in scratch/s76xx/ast.json. Nothing
re-ran the AST after later sessions added code (G6a rumble, G6b bindings/F6 panel, s7644 instrument), so s7613/s7615/s7616
read RED on "regex-only" / line-shifted rows that were pure cache staleness (s7655: 80 s7616 DISAGREE rows from line drift,
5 s7613 + 1 s7615 regex-only rows; all vanished after regeneration).

ensure(cache, gen_tool) regenerates the cache (gen_tool --out cache, under an flock so parallel sweep jobs do not race) when
any source the AST could have read is newer than it: every TU in build/compile_commands.json, every header under src/ and
lib/*/ (contrib excluded), and compile_commands.json itself. Returns "fresh" or "regenerated".
--selftest: a temp cache older than one source must read stale, one newer than every source fresh, else exit 1.
"""
import fcntl, json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HDR = (".h", ".hpp", ".hh", ".inl")


def sources():
    cc = os.path.join(ROOT, "build/compile_commands.json")
    out = [cc]
    try:
        out += [e["file"] if os.path.isabs(e["file"]) else os.path.join(e.get("directory", ROOT), e["file"]) for e in json.load(open(cc))]
    except (OSError, ValueError):
        pass
    for base in ("src", "lib/rt64/src", "lib/N64ModernRuntime"):
        for d, ds, fs in os.walk(os.path.join(ROOT, base)):
            ds[:] = [x for x in ds if x not in ("contrib", ".git", "build")]
            out += [os.path.join(d, f) for f in fs if f.endswith(HDR)]
    return out


def newest(paths):
    best, who = 0.0, None
    for p in paths:
        try:
            m = os.stat(p).st_mtime
        except OSError:
            continue
        if m > best:
            best, who = m, p
    return best, who


def stale(cache, paths=None):
    try:
        cm = os.stat(cache).st_mtime
    except OSError:
        return True, "missing"
    m, who = newest(sources() if paths is None else paths)
    return (m > cm), (os.path.relpath(who, ROOT) if who else "")


def ensure(cache, gen_tool):
    s, why = stale(cache)
    if not s:
        return "fresh"
    os.makedirs(os.path.dirname(cache), exist_ok=True)
    with open(cache + ".lock", "w") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        s, why = stale(cache)  # another job may have regenerated it while we waited
        if not s:
            return "fresh"
        print("[ast-cache] %s stale (newer: %s) -> regenerating" % (os.path.relpath(cache, ROOT), why), file=sys.stderr)
        tmp = cache + ".tmp"
        subprocess.run([sys.executable, os.path.join(ROOT, gen_tool), "--out", tmp], check=True, cwd=ROOT,
                       stdout=subprocess.DEVNULL)
        os.replace(tmp, cache)
    return "regenerated"


def selftest():
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        src, cache = os.path.join(d, "a.h"), os.path.join(d, "ast.json")
        open(src, "w").write("x"); open(cache, "w").write("[]")
        os.utime(cache, (1000, 1000)); os.utime(src, (2000, 2000))
        a = stale(cache, [src])[0]
        os.utime(cache, (3000, 3000))
        b = stale(cache, [src])[0]
    ok = a is True and b is False
    print("[ast-cache] selftest older-cache stale=%s newer-cache stale=%s -> %s" % (a, b, "PASS" if ok else "FAIL"))
    return ok


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(0 if selftest() else 1)
    for c, g in (("scratch/s7613/ast.json", "tools/s7613_hp_ast.py"), ("scratch/s7614/ast.json", "tools/s7614_hm_ast.py"),
                 ("scratch/s7616/ast.json", "tools/s7616_rq_ast.py")):
        print(c, stale(os.path.join(ROOT, c)))
