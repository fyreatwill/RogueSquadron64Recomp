#!/usr/bin/env python3
"""s7651 gate sweep: run every closed-class census (tools/s7*_census.py) in one pass and say which have gone RED.

s7651 found 4 "closed" rerun-after-change gates (s7375, s7430, s7533, s7535) exiting nonzero after later sessions added code
in their scope (G6b controls, G6c stand-ins, s7535-s7647 instruments): nothing re-ran them, so CURRENT-TRUTH still called
them closed. This runs them all (with --controls when the tool takes it), 6 at a time, 600 s cap each (RS64_GATE_CAP; s7659), and classifies:
  GREEN      exit 0
  NEEDS-ARGS argparse usage / IndexError on sys.argv / missing input file: the tool needs an input (not a drift signal)
  RED        any other nonzero exit: drift or a real defect, triage by hand
  NEEDS-INPUT (s7655) a tool listed in NEEDS_INPUT printing its exact "input absent" text (other failures stay RED)
  REPORT     (s7657) a tool listed in REPORT whose source has no exit path: a summariser of one frozen capture, not a gate
s7657: the two-source censuses s7631/s7632/s7633 run with no args regenerate their scan/AST json from the live tree
(tools/ast_cache.fresh_census_args), so they gate the current code, not the s763x snapshot; --help prints this text.
Positive control (iron rule 1): a planted tool that exits 1 must read RED and one that exits 0 GREEN, else exit 3.
s7656 cache: every tool runs under tools/gate_trace.py (audit hook records each file it opens for reading, each directory it
lists, each glob); its verdict is cached in build/gate_sweep_cache.json keyed on (argv, size+mtime of every read file incl. the
tool itself, every listed directory's names, every glob's matches). Spawns: nm/objdump/zstd-class tools are keyed on their file
arguments; cc/c++/clang also on the exact header list clang writes to CC_PRINT_HEADERS_FILE; a program a compiler built in
the same run is allowed; git, shells and anything else keep the tool uncacheable (their reads are invisible). Cache control (iron rule 1): a planted tool reading a temp input must read GREEN, then a cache
HIT, then RED after the input is edited (else exit 3). --no-cache re-proves everything.
--new-red-vs FILE: exit 1 only for RED gates NOT listed (first column) in FILE, the committed allowed-RED baseline.
Usage: s7651_gate_sweep.py [--jobs N] [--only REGEX] [--tsv OUT] [--no-cache] [--new-red-vs FILE]
exit 0 iff no (new) RED (NEEDS-ARGS allowed)."""
import concurrent.futures as cf, glob, hashlib, json, os, re, subprocess, sys, tempfile, threading, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARGS_SIG = re.compile(r"IndexError: list index out of range|usage: |error: unrecognized arguments|error: the following arguments"
                      r"|FileNotFoundError|No such file or directory|struct\.error: unpack_from")


# s7655: tools that report on runtime inputs the sweep cannot supply. Keyed by tool AND the exact text it prints when the input
# is absent: if the tool's message changes (or it fails another way) it reads RED again.
NEEDS_INPUT = {
    "s7316_data_bound_census.py": (re.compile(r"ram_dumps=0\s*$"), "needs --ram rdram dumps (ROGUESQ_RDRAM_DUMP_DIR): G values unread"),
    "s7573_guard_census.py": (re.compile(r"^no game logs\s*$", re.M), "needs game stderr logs (LOG... or --retained DIR)"),
    # s7657: the s7215 run.log (ROGUESQ_VI_SHAPE_LOG=1, 21:9 long route) was never retained: scratch/s7215 holds 0 shape lines
    "s7215_shape_census.py": (re.compile(r"L = open\(sys\.argv\[1\].*\n(.*\n)?IndexError: list index out of range"),
                              "needs a ROGUESQ_VI_SHAPE_LOG=1 run.log (scratch/s7215/r.zsh); the s7215 log was not kept"),
}

# s7657: offline summarisers of ONE captured run / regen output. They have no failing exit (always 0), so a GREEN would be
# vacuous and their frozen inputs cannot drift with the code. Verified per run: if the source gains any exit path the tool is
# run like any other gate again.
REPORT = {
    "s7031_offmap_census.py": "summary of a [s7030]/[s7031] run.log (band/ring table), no verdict exit",
    "s7082_jal_census.py": "table of N64Recomp 'No function found for jal' lines, no verdict exit",
    "s7083_lowering_census.py": "jr/jump-table lowering table over a regen dir + ROM, no verdict exit",
    "s7210_field_census.py": "per-swap field-bit table of a G5B_FRAME .cap stream, no verdict exit",
    "s7441_rs64_census.py": "self-time table of rs64_* frames in sample_*.txt dumps, documented exit 0",
}
EXIT_PATH = re.compile(r"\bsys\.exit\(|\bexit\(|\breturn [1-9]\b|raise SystemExit")


# s7656: NEEDS-ARGS gates whose input lives on disk: run with that input so they count. Used only when every path exists.
# (argv, regex the output must contain, else RED): s7409/s7410 exit 0 even on CONTROL FAIL, so the text is the gate.
ARGS = {
    "s7409_fodd_census.py": (["../N64Recomp/RecompiledFuncs", "--plant"], r"CONTROL PASS"),   # planted FR0 MIXED row
    "s7410_csave_census.py": (["../N64Recomp/RecompiledFuncs", "--plant"], r"CONTROL PASS"),  # dropped ldc1 restore
    "s7091_ucode_insn_census.py": (["scratch/s7091/pristine", "build/factor5_ucode", "--controls"], None),  # rc 1 = unexplained
    # s7657: the d8 holder dump is only kept gzipped; --selftest proves classes A-E on the built-in synthetic listing (rc 2 FAIL)
    "s7317_field_compare_census.py": (["--selftest"], r"SELFTEST .* PASS"),
    # s7658: the three s7655/s7657 NEEDS-INPUT gates now carry a retained input captured once (NEEDS_INPUT stays the fallback
    # when the files are absent, e.g. a fresh clone). Planted controls in PORTING-STATE s7658.
    "s7215_shape_census.py": (["scratch/s7215/shape_lines.txt.zst"], r"without a mode switch within 1000 lines: 0"),
    "s7316_data_bound_census.py": (["--ram", "scratch/s7316/ram/rdram_0002000_fb80A62B80_1M5.bin.zst",
                                    "scratch/s7316/ram/rdram_0008000_fb8098AA00_1M5.bin.zst"], r"unclassified=0 .*ram_dumps=2"),
    "s7573_guard_census.py": (["--gate", "--retained", "scratch/s7573/retained"], r"GATE PASS"),
}
TRACER = os.path.join(ROOT, "tools", "gate_trace.py")
CACHE_PATH = os.path.join(ROOT, "build", "gate_sweep_cache.json")
CACHE, CACHE_LOCK, STATS = {}, threading.Lock(), {"hit": 0, "miss": 0, "uncacheable": 0}
USE_CACHE = True
# s7659: per-gate cap. Cold AST regen measured 240 s max (s7607) at load 8-14 = 80% of the old 300 s; a timeout reads RED
# and blocks stop_gate, so the default is 600 s (a hung gate still dies). RS64_GATE_CAP overrides.
GATE_CAP = int(os.environ.get("RS64_GATE_CAP", "600"))


def fingerprint(argv, tr):
    h = hashlib.sha256(("\0".join(argv) + "\1").encode())
    st = os.stat(os.path.abspath(__file__))  # a classifier change in this sweep invalidates every entry
    h.update(f"s{st.st_size}\0{st.st_mtime_ns}\n".encode())
    for r in tr["reads"]:
        try:
            st = os.stat(r)
            h.update(f"r{r}\0{st.st_size}\0{st.st_mtime_ns}\n".encode())
        except OSError:
            h.update(f"r{r}\0missing\n".encode())
    for d in tr["dirs"]:
        try:
            h.update(f"d{d}\0{chr(0).join(sorted(os.listdir(d)))}\n".encode())
        except OSError:
            h.update(f"d{d}\0missing\n".encode())
    for g in tr["globs"]:
        h.update(f"g{g}\0{chr(0).join(sorted(glob.glob(g, recursive=True)))}\n".encode())
    return h.hexdigest()


# s7656: spawns whose output is a pure function of their file arguments (and, for compilers, the headers clang reports via
# CC_PRINT_HEADERS_FILE) can be keyed; anything else (git, a shell, an arbitrary program) keeps the tool uncacheable.
PURE = {"nm", "objdump", "llvm-objdump", "mips64-elf-objdump", "otool", "zstd", "llvm-nm"}
COMPILERS = {"cc", "c++", "clang", "clang++"}  # Apple cc/c++ are clang; gcc does not honour CC_PRINT_HEADERS_FILE
IFLAGS = ("-I", "-isystem", "-iquote", "-include", "-F")


def spawn_inputs(tr, hdr_lines):
    """-> (cacheable, extra_reads, extra_dirs, why) for the trace's subprocesses."""
    reads, dirs, outs, cwds, compiled = set(), set(), set(), {ROOT}, False
    for sp in tr.get("spawn", []):
        argv, cwd = sp["argv"], sp["cwd"]
        cwds.add(cwd)
        a0 = argv[0] if argv else ""
        a0abs = os.path.normpath(os.path.join(cwd, a0)) if "/" in a0 else None
        base = os.path.basename(a0)
        if sp.get("shell"):
            return False, (), (), f"shell spawn {a0[:40]}"
        if base in COMPILERS:
            if not sp.get("env_ok"):
                return False, (), (), f"{base} with a custom env (no header list)"
            compiled = True
        elif base not in PURE and not (a0abs and a0abs in outs):
            return False, (), (), f"spawns {base}"
        nxt_out = False
        for i, t in enumerate(argv[1:]):
            if nxt_out:
                outs.add(os.path.normpath(os.path.join(cwd, t)))
                nxt_out = False
                continue
            if t == "-o":
                nxt_out = True
                continue
            for f in IFLAGS:
                if t.startswith(f) and len(t) > len(f):
                    t = t[len(f):]
                    break
            if t.startswith("-"):
                continue
            q = os.path.normpath(os.path.join(cwd, t))
            if os.path.isfile(q):
                reads.add(q)
            elif os.path.isdir(q):
                dirs.add(q)  # an -I dir: a new header there can shadow a later one
    if compiled:  # env_ok held for every compile, so an empty list means no #include (s7607's header-less witness .c)
        for h in hdr_lines:
            h = h.strip().lstrip(". ") if h.startswith(".") and not h.startswith("./") and not h.startswith("../") else h.strip()
            if not h:
                continue
            if os.path.isabs(h):
                reads.add(h)
            else:
                reads.update(os.path.normpath(os.path.join(c, h)) for c in cwds)
    reads -= outs
    return True, sorted(reads), sorted(dirs), ""


def traced(path, a):
    """Run path with args a under the tracer; return (rc, out, trace-or-None)."""
    fd, tf = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    os.unlink(tf)
    try:
        p = subprocess.run([sys.executable, TRACER, path] + a, cwd=ROOT, capture_output=True, text=True, errors="replace",
                           timeout=GATE_CAP, env=dict(os.environ, RS64_GATE_TRACE=tf, CC_PRINT_HEADERS="1",
                                                 CC_PRINT_HEADERS_FILE=tf + ".hdr"))
        rc, out = p.returncode, p.stdout + p.stderr
        try:
            tr = json.load(open(tf))
        except (OSError, ValueError):
            tr = None
        if tr is not None:
            try:
                hdr = open(tf + ".hdr", errors="replace").read().splitlines()
            except OSError:
                hdr = []
            ok, er, ed, why = spawn_inputs(tr, hdr)
            tr["spawn_ok"], tr["why"] = ok, why
            tr["reads"] = sorted(set(tr["reads"]) | set(er))
            tr["dirs"] = sorted(set(tr["dirs"]) | set(ed))
        return rc, out, tr
    finally:
        for f in (tf, tf + ".hdr"):
            if os.path.exists(f):
                os.unlink(f)


TIMES = {}  # s7659: per-gate wall seconds (cache hit ~0), printed as the slowest gates vs GATE_CAP


def run(path):
    t = time.time()
    try:
        return _run(path)
    finally:
        TIMES[os.path.basename(path)] = time.time() - t


def _run(path):
    key = os.path.abspath(path)
    if USE_CACHE:
        with CACHE_LOCK:
            ent = CACHE.get(key)
        if ent and fingerprint(ent["argv"], ent["trace"]) == ent["fp"]:
            with CACHE_LOCK:
                STATS["hit"] += 1
            return tuple(ent["row"])
    row, argv, tr = run_uncached(path)
    cacheable = tr is not None and tr.get("complete") and tr.get("spawn_ok") and row[2] != "timeout"
    with CACHE_LOCK:
        STATS["miss" if cacheable else "uncacheable"] += 1
        if cacheable:
            CACHE[key] = {"argv": argv, "trace": tr, "fp": fingerprint(argv, tr), "row": list(row)}
        else:
            CACHE.pop(key, None)
    return row


def run_uncached(path):
    src = open(path, errors="replace").read()
    rep = REPORT.get(os.path.basename(path))
    if rep and not EXIT_PATH.search(src):
        return (os.path.basename(path), "REPORT", "-", rep), [], {"reads": [os.path.abspath(path)], "dirs": [], "globs": [],
                                                                     "complete": True, "spawn_ok": True}
    a = ["--controls"] if "--controls" in src else []
    fixed, must = ARGS.get(os.path.basename(path), (None, None))
    if fixed and all(os.path.exists(os.path.join(ROOT, x)) for x in fixed if not x.startswith("-")):
        a = list(fixed)
    else:
        must = None
    try:
        rc, out, tr = traced(path, a)
    except subprocess.TimeoutExpired:
        return (os.path.basename(path), "RED", "timeout", f"timeout {GATE_CAP} s"), a, None
    tail = " | ".join(l.strip() for l in out.strip().split("\n")[-2:])[:200]
    if rc == 0 and must and not re.search(must, out):
        return (os.path.basename(path), "RED", rc, f"output lacks /{must}/: {tail}"), a, tr
    if rc == 0:
        return (os.path.basename(path), "GREEN", rc, tail), a, tr
    if "--controls" in a and "unrecognized arguments: --controls" in out:  # mentions --controls in text only: retry bare
        a = []
        rc, out, tr = traced(path, a)
        tail = " | ".join(l.strip() for l in out.strip().split("\n")[-2:])[:200]
        if rc == 0:
            return (os.path.basename(path), "GREEN", rc, tail), a, tr
    ni = NEEDS_INPUT.get(os.path.basename(path))
    if ni and ni[0].search(out.strip()[-400:]):
        return (os.path.basename(path), "NEEDS-INPUT", rc, ni[1]), a, tr
    return (os.path.basename(path), "NEEDS-ARGS" if ARGS_SIG.search(out[-3000:]) else "RED", rc, tail), a, tr


def cache_control(d):
    """Planted tool reading an input file: GREEN, then a cache hit, then RED once the input changes; a spawning tool is
    never cached. Uses its own cache dict so the real cache is untouched."""
    global CACHE, USE_CACHE
    saved, CACHE = CACHE, {}
    su, USE_CACHE = USE_CACHE, True  # s7659: the control tests the cache itself; --no-cache used to fail it (exit 3)
    s0 = dict(STATS)
    try:
        inp, tool = os.path.join(d, "cc_input.txt"), os.path.join(d, "cc_input_census.py")
        open(inp, "w").write("ok\n")
        open(tool, "w").write(f"import sys\nsys.exit(0 if open({inp!r}).read().strip() == 'ok' else 1)\n")
        r1 = run(tool)[1]
        h1 = STATS["hit"]
        r2 = run(tool)[1]
        hit = STATS["hit"] == h1 + 1
        time.sleep(0.01)
        open(inp, "w").write("broken\n")
        r3 = run(tool)[1]
        sp = os.path.join(d, "cc_spawn_census.py")
        open(sp, "w").write("import subprocess, sys\nsubprocess.run(['true'])\n")
        run(sp)
        spawn_uncached = os.path.abspath(sp) not in CACHE
        # compiler control: the tool reads only its .c; the header reaches the key via CC_PRINT_HEADERS alone
        hd, cs, ct = os.path.join(d, "cch"), os.path.join(d, "cc_m.c"), os.path.join(d, "cc_compile_census.py")
        os.makedirs(hd, exist_ok=True)
        open(os.path.join(hd, "cc_h.h"), "w").write("#define CC_OK 1\n")
        open(cs, "w").write('#include "cc_h.h"\nint x[CC_OK ? 1 : -1];\n')
        open(ct, "w").write("import subprocess, sys\n"
                            f"sys.exit(subprocess.run(['clang', '-fsyntax-only', '-I', {hd!r}, {cs!r}]).returncode)\n")
        c1 = run(ct)[1]
        hc = STATS["hit"]
        c2 = run(ct)[1]
        chit = STATS["hit"] == hc + 1
        time.sleep(0.01)
        open(os.path.join(hd, "cc_h.h"), "w").write("#define CC_OK 0\n")
        c3 = run(ct)[1]
        got = (r1, r2, hit, r3, spawn_uncached, c1, c2, chit, c3)
        return got == ("GREEN", "GREEN", True, "RED", True, "GREEN", "GREEN", True, "RED"), got
    finally:
        CACHE = saved
        USE_CACHE = su
        STATS.update(s0)


def main():
    global USE_CACHE, CACHE
    if "--help" in sys.argv or "-h" in sys.argv:  # s7657: used to run a full sweep
        print(__doc__)
        sys.exit(0)
    t0 = time.time()
    USE_CACHE = "--no-cache" not in sys.argv
    if USE_CACHE:
        try:
            CACHE = json.load(open(CACHE_PATH))
        except (OSError, ValueError):
            CACHE = {}
    newvs = sys.argv[sys.argv.index("--new-red-vs") + 1] if "--new-red-vs" in sys.argv else None
    jobs = int(sys.argv[sys.argv.index("--jobs") + 1]) if "--jobs" in sys.argv else 2
    only = re.compile(sys.argv[sys.argv.index("--only") + 1]) if "--only" in sys.argv else None
    tsv = sys.argv[sys.argv.index("--tsv") + 1] if "--tsv" in sys.argv else None
    with tempfile.TemporaryDirectory() as d:
        bad, good = os.path.join(d, "ctl_red_census.py"), os.path.join(d, "ctl_green_census.py")
        open(bad, "w").write("import sys\nprint('UNCLASSIFIED 1')\nsys.exit(1)\n")
        open(good, "w").write("print('ok')\n")
        # s7655: NEEDS-INPUT is keyed by name + text: the right text reads NEEDS-INPUT, the same name failing otherwise reads RED
        ni_ok, ni_bad = os.path.join(d, "s7573_guard_census.py"), os.path.join(d, "ni", "s7573_guard_census.py")
        os.makedirs(os.path.dirname(ni_bad))
        open(ni_ok, "w").write("import sys\nprint('no game logs')\nsys.exit(1)\n")
        open(ni_bad, "w").write("import sys\nprint('OPEN 1')\nsys.exit(1)\n")
        c = {r[0]: r[1] for r in map(run, (bad, good))}
        c["ni_text"], c["ni_other"] = run(ni_ok)[1], run(ni_bad)[1]
        # s7657: REPORT holds only while the tool has no exit path: the same name failing via sys.exit must read RED
        rp_ok, rp_bad = os.path.join(d, "rp", "s7031_offmap_census.py"), os.path.join(d, "rq", "s7031_offmap_census.py")
        for f, body in ((rp_ok, "print('table')\n"), (rp_bad, "import sys\nprint('table')\nsys.exit(1)\n")):
            os.makedirs(os.path.dirname(f))
            open(f, "w").write(body)
        c["rep_noexit"], c["rep_exit"] = run(rp_ok)[1], run(rp_bad)[1]
        for k in list(CACHE):  # controls never persist
            if k.startswith(os.path.abspath(d)):
                del CACHE[k]
        ccpass, cc = cache_control(d)
    cpass = c == {"ctl_red_census.py": "RED", "ctl_green_census.py": "GREEN", "ni_text": "NEEDS-INPUT", "ni_other": "RED",
                 "rep_noexit": "REPORT", "rep_exit": "RED"}
    print("[s7651] control planted red/green ->", c, "PASS" if cpass else "FAIL")
    print("[s7656] cache control read: green/green/hit/red-after-edit, spawn-uncached, compile: green/green/hit/red-after-header-edit ->", cc, "PASS" if ccpass else "FAIL")
    if not (cpass and ccpass):
        sys.exit(3)
    for k in ("hit", "miss", "uncacheable"):
        STATS[k] = 0
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
            o.writelines(f"{n}\t{c}\t{r}\t{t}\t{TIMES.get(n, 0):.1f}\n" for n, c, r, t in rows)
    if USE_CACHE:
        live = {os.path.abspath(t) for t in tools}
        if not only:  # drop entries for deleted tools
            CACHE = {k: v for k, v in CACHE.items() if k in live}
        os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
        json.dump(CACHE, open(CACHE_PATH + ".tmp", "w"))
        os.replace(CACHE_PATH + ".tmp", CACHE_PATH)
    slow = sorted(((TIMES.get(r[0], 0), r[0]) for r in rows), reverse=True)[:5]
    print(f"[s7659] slowest gates (s, cap {GATE_CAP}):", " ".join(f"{n}={v:.0f}" for v, n in slow))
    print("[s7651] gates", len(rows), dict(Counter(r[1] for r in rows)))
    print(f"[s7656] cache {'on' if USE_CACHE else 'off'} hit={STATS['hit']} miss={STATS['miss']} "
          f"uncacheable={STATS['uncacheable']} wall={time.time() - t0:.1f}s")
    red = [r[0] for r in rows if r[1] == "RED"]
    if newvs:
        allowed = {l.split()[0] for l in open(newvs) if l.strip() and not l.startswith("#")} if os.path.exists(newvs) else set()
        new = [n for n in red if n not in allowed]
        print(f"[s7656] new RED vs {os.path.relpath(newvs, ROOT)}: {len(new)} {' '.join(new)}")
        sys.exit(1 if new else 0)
    sys.exit(1 if red else 0)  # NEEDS-ARGS / NEEDS-INPUT allowed


if __name__ == "__main__":
    main()
