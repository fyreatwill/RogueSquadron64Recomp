#!/usr/bin/env python3
"""s7420 class CC: RecompiledFuncs function-split parser agreement with the weak headers.

tools/weaken_patched_funcs.py rewrites 3 headers to `__attribute__((weak)) RECOMP_FUNC void NAME(` (isCinematicActive,
setRngSeed, findAndUnlinkSmallestEntry). A parser whose header pattern needs `RECOMP_FUNC` at line start (or re.match on a
line, or a "\\nRECOMP_FUNC" literal) does not see those 3 functions: their rows land in the function before them.

For every tools/*.py this census extracts every string constant containing RECOMP_FUNC, decides from its call site how it
is applied (re.match / ^-anchored compile / re.search / str.find / startswith), and tests it on a normal header and on
its weak form. A constant that accepts the normal line but not the weak one is WEAK-BLIND. Each tool is then placed:
  CHAIN-PRE   runs before weaken in tools/regen_replay.sh (RS64_REPLAY scripts, vendored fixups): never sees a weak header
  WEAKENER    weaken_patched_funcs.py itself (its anchored regex targets the un-weakened header by design: SELF)
  CHAIN-POST  runs after weaken in regen_replay.sh (cut_decoded_tails, rename, s736x censuses)
  PATCHES-TREE tools CMake runs on RecompiledPatches/patches.c (fixup_patches_host.py): that tree is never weakened, so a
              blind regex there is IMMUNE-TREE while patches.c has 0 weak headers, OPEN otherwise (s7563)
  STANDALONE  everything else (audits, historical apply_* run by hand on the live tree, which IS weakened)
and its targets are intersected with the affected set (3 weak functions + the function before each one in the live tree).
Verdict: OPEN if a blind EDITOR targets an affected function outside CHAIN-PRE, or a blind CHAIN-POST tool exists.
Also prints how many `// 0x` rows a blind whole-tree reader mis-attributes.

--controls: (1) a planted blind editor (anchored regex on setRngSeed) must be OPEN; (2) a planted weak-aware one must
not be blind; (4) a planted weak header in the patches tree must reopen fixup_patches_host.py; (3) a blind split over a temp copy of funcs_1.c with a planted weak header must move rows; (5) s7806: an absent patches tree must read DEFER, never IMMUNE-TREE.
--require-tree: s7806, DEFER (RecompiledPatches/patches.c not generated yet) fails; build-from-scratch.sh uses it after the build.
--dynamic: run every blind standalone audit against a live copy and a de-weakened copy in sandboxes and diff the output.
usage: tools/s7420_parser_census.py [--verbose] [--controls] [--require-tree] [--dynamic]   exit 1 = OPEN row, failed control, or DEFER under --require-tree
"""
import ast, glob, os, re, sys, tempfile, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FUNCS = os.path.join(os.path.dirname(ROOT), "N64Recomp", "RecompiledFuncs")
WEAK = ["isCinematicActive", "setRngSeed", "findAndUnlinkSmallestEntry"]
HDR = re.compile(r'^(?:__attribute__\(\(weak\)\) )?RECOMP_FUNC void (\w+)\(', re.M)
CMT = re.compile(r'// 0x([0-9A-F]{8}):')
POST = {"fixup_cut_decoded_tails.py", "rename_generated_symbols.py", "s7361_memzext_census.py", "s7362_rdramraw_census.py",
        "s7363_hostarr_census.py", "s7364_heapbuf_census.py", "s7365_invalidation_census.py", "s7366_lockset_census.py"}


def live_split():
    """reference (weak-aware) split: ordered [(file, name, rows)]"""
    out = []
    for f in sorted(glob.glob(FUNCS + "/funcs_*.c")):
        t = open(f, errors="replace").read()
        hs = list(HDR.finditer(t))
        for k, m in enumerate(hs):
            end = hs[k + 1].start() if k + 1 < len(hs) else len(t)
            out.append((os.path.basename(f), m.group(1), len(CMT.findall(t, m.start(), end))))
    return out


def affected(split):
    aff, rows = {}, {}
    for i, (f, n, r) in enumerate(split):
        if n in WEAK:
            aff[n] = "weak"
            rows[n] = r
            j = i - 1
            while j >= 0 and split[j][1] == n: j -= 1
            if j >= 0 and split[j][0] == f: aff.setdefault(split[j][1], "pred-of-" + n)
    return aff, rows


PATCHES_C = os.path.join(ROOT, "RecompiledPatches", "patches.c")


def patches_tree_tools():
    """s7563: tools CMake runs on RecompiledPatches/patches.c (N64Recomp output of patches.elf). weaken_patched_funcs.py only
    touches RecompiledFuncs/funcs_*.c, so this tree has strong headers by construction: a weak-blind regex there is not blind
    to anything. Derived from CMakeLists (a tools/X.py COMMAND whose args name RECOMPILED_PATCHES_DIR)."""
    t = open(os.path.join(ROOT, "CMakeLists.txt"), errors="replace").read()
    return set(re.findall(r'tools/(\w+\.py)"\s*\n\s*"\$\{RECOMPILED_PATCHES_DIR\}', t))


def patches_tree_weak(text=None):
    """weak headers in the patches tree (must be 0 for IMMUNE-TREE to hold); -1 = tree absent (cannot vouch)"""
    if text is None:
        if not os.path.exists(PATCHES_C): return -1
        text = open(PATCHES_C, errors="replace").read()
    return len(re.findall(r'^__attribute__\(\(weak\)\) RECOMP_FUNC void ', text, re.M))


def chain_pre():
    pre = set()
    v = open(os.path.join(ROOT, "tools", "fixup_game_funcs_vendored.py"), errors="replace").read()
    pre |= set(re.findall(r'"((?:apply|fixup)_\w+\.py)"', v))
    pre |= set(re.findall(r'with_name\("(\w+\.py)"\)', v))
    for s in ("fixup_game_funcs_vendored", "fixup_movz_movn", "strip_diag_layers", "fixup_live_replay"):
        pre.add(s + ".py")
    return pre


def sample(name):
    n = "RECOMP_FUNC void %s(uint8_t* rdram, recomp_context* ctx) {\n    uint64_t hi = 0, lo = 0, result = 0;\n" % name
    return n, "__attribute__((weak)) " + n


def fill(s, name):
    s = s.replace("%s", name).replace("{name}", name).replace("{}", name)
    return re.sub(r"\{\w*\}", name, s)


def classify_const(s, mode):
    """-> (matches_normal, matches_weak) for one constant under one application mode"""
    for name in ("setRngSeed", "lv1_checkComplexObjectives", "initMission", "playerXwingUpdate", "fooBar"):
        n, w = sample(name)
        pat = fill(s, name)
        if mode == "literal":
            mn, mw = pat in "\n" + n, pat in "\n" + w
        elif mode == "startswith":
            mn, mw = n.startswith(pat), w.startswith(pat)
        else:
            try:
                rx = re.compile(pat, re.M)
            except re.error:
                return None
            if mode == "match":
                mn, mw = bool(rx.match(n)), bool(rx.match(w))
            else:
                mn, mw = bool(rx.search("\n" + n)), bool(rx.search("\n" + w))
        if mn: return mn, mw
    return None


def consts(path):
    """[(lineno, const, mode)] for string constants containing RECOMP_FUNC"""
    src = open(path, errors="replace").read()
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return [(0, m.group(0), "literal") for m in re.finditer(r"RECOMP_FUNC[^'\"\n]*", src)], src
    parent = {}
    for p in ast.walk(tree):
        for c in ast.iter_child_nodes(p): parent[c] = p
    compiled = {}
    for node in ast.walk(tree):  # NAME = re.compile(...)  -> how NAME is later applied
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call) and getattr(node.value.func, "attr", "") == "compile":
            for t in node.targets:
                if isinstance(t, ast.Name):
                    uses = set(re.findall(r"\b%s\.(match|fullmatch|search|finditer|findall|sub|split)\(" % re.escape(t.id), src))
                    compiled[id(node.value)] = "match" if uses & {"match", "fullmatch"} else "search"
    out = []
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Constant) and isinstance(node.value, str) and "RECOMP_FUNC" in node.value): continue
        s, p = node.value, parent.get(node)
        while isinstance(p, (ast.BinOp, ast.JoinedStr, ast.FormattedValue)) and p in parent: p = parent[p]
        mode = "literal"
        if isinstance(p, ast.Call):
            fn = getattr(p.func, "attr", getattr(p.func, "id", ""))
            if fn in ("match", "fullmatch"): mode = "match"
            elif fn in ("search", "finditer", "findall", "sub", "subn", "split"): mode = "search"
            elif fn == "compile": mode = compiled.get(id(p), "search")
            elif fn == "startswith": mode = "startswith"
        out.append((node.lineno, s, mode))
    return out, src


def audit(paths, split, aff, pre, verbose=False, ptree=None, pweak=None):
    rows = []
    ptree = patches_tree_tools() if ptree is None else ptree
    pweak = patches_tree_weak() if pweak is None else pweak
    for path in paths:
        name = os.path.basename(path)
        cs, src = consts(path)
        blind = []
        for ln, s, mode in cs:
            r = classify_const(s, mode)
            if r and r[0] and not r[1]: blind.append((ln, mode, s[:60]))
        if not cs: continue
        editor = bool(re.search(r"write_text\(|open\([^)]*['\"][wa]\+?['\"]|\.write\(", src))
        reads_tree = "RecompiledFuncs" in src or "funcs_" in src or "sys.argv" in src
        phase = ("WEAKENER" if name == "weaken_patched_funcs.py" else "CHAIN-PRE" if name in pre
                 else "CHAIN-POST" if name in POST else "PATCHES-TREE" if name in ptree else "STANDALONE")
        hits = sorted(n for n in aff if re.search(r"\b%s\b" % re.escape(n), src))
        verdict = "ok"
        if blind and phase == "WEAKENER":
            verdict = "SELF"  # matches the un-weakened header on purpose; idempotent (re-run finds nothing to rewrite)
        elif blind:
            if phase == "CHAIN-POST": verdict = "OPEN"
            # s7806: -1 = tree not generated yet (regen_replay runs before CMake makes patches.c, e.g. a clean public build):
            # it cannot vouch either way -> DEFER (not OPEN, not IMMUNE). --require-tree turns DEFER into a failure.
            elif phase == "PATCHES-TREE": verdict = "IMMUNE-TREE" if pweak == 0 else "DEFER" if pweak == -1 else "OPEN"
            elif editor and hits and phase != "CHAIN-PRE": verdict = "OPEN"
            elif hits: verdict = "IMMUNE-PRE" if phase == "CHAIN-PRE" else "READ-HIT"
            else: verdict = "BLIND-NOHIT"
        rows.append((name, phase, editor, reads_tree, len(cs), blind, hits, verdict))
    return rows


def dynamic(names, jobs=6, timeout=240):
    """Run each tool twice from throwaway sandboxes whose N64Recomp/RecompiledFuncs is (a) a copy of the live tree and
    (b) the same copy with the 3 weak prefixes removed; same sandbox paths, so stdout+stderr must be byte-equal unless
    the weak headers change what the tool reports. -> {name: (rc_a, rc_b, equal, ndiff)}"""
    import subprocess, concurrent.futures as cf
    live_root = ROOT
    live_funcs = FUNCS
    out = {}
    base = tempfile.mkdtemp(prefix="s7420_dyn_")
    try:
        for arm in ("a", "b"):
            sb = os.path.join(base, arm)
            fd = os.path.join(sb, "N64Recomp", "RecompiledFuncs")
            shutil.copytree(live_funcs, fd, ignore=shutil.ignore_patterns("build", "*.md"))
            if arm == "b":
                for f in glob.glob(fd + "/funcs_*.c"):
                    t = open(f, errors="surrogateescape").read()
                    if "__attribute__((weak)) RECOMP_FUNC" in t:
                        open(f, "w", errors="surrogateescape").write(t.replace("__attribute__((weak)) RECOMP_FUNC", "RECOMP_FUNC"))
            rs = os.path.join(sb, "RS64")
            os.makedirs(os.path.join(rs, "tools"))
            for q in glob.glob(os.path.join(live_root, "tools", "*")):
                if not os.path.isfile(q): continue
                d = os.path.join(rs, "tools", os.path.basename(q))
                if q.endswith(".py"):
                    t = open(q, errors="surrogateescape").read()
                    t = t.replace(live_funcs, fd).replace(live_root, rs)
                    open(d, "w", errors="surrogateescape").write(t)
                else:
                    shutil.copy(q, d)
            for rel in ("docs", "src", "include", "scratch/s7419", "scratch/s7082", "scratch/s7089", "scratch/s7317"):
                if os.path.isdir(os.path.join(live_root, rel)):
                    shutil.copytree(os.path.join(live_root, rel), os.path.join(rs, rel), symlinks=True)
            os.symlink(os.path.join(live_root, "build"), os.path.join(rs, "build"))
            os.symlink(os.path.join(live_root, "lib"), os.path.join(rs, "lib"))
            sib = os.path.join(os.path.dirname(live_root), "rogue_squadron64")  # ELF / ROM / symbol files, read only
            if os.path.isdir(sib): os.symlink(sib, os.path.join(sb, "rogue_squadron64"))
            for rel in ("src", "include", "build"):  # N64Recomp sources (symbol_lists.cpp), read only
                q = os.path.join(os.path.dirname(live_funcs), rel)
                if os.path.isdir(q): os.symlink(q, os.path.join(sb, "N64Recomp", rel))
        def run(name, arm, argv=()):
            rs = os.path.join(base, arm, "RS64")
            try:
                r = subprocess.run([sys.executable, os.path.join(rs, "tools", name)] + list(argv), cwd=rs, capture_output=True,
                                   text=True, errors="replace", timeout=timeout)
                txt = (r.stdout + r.stderr).replace(os.path.join(base, arm), "<SB>")
                return r.returncode, txt
            except subprocess.TimeoutExpired:
                return "timeout", ""
        with cf.ThreadPoolExecutor(jobs) as ex:
            futs = {(n, arm): ex.submit(run, n, arm) for n in names for arm in ("a", "b")}
            first = {k: f.result() for k, f in futs.items()}
            retry = [n for n in names if first[(n, "a")][0] != 0 and first[(n, "b")][0] != 0]  # needs the tree as argv[1]?
            futs2 = {(n, arm): ex.submit(run, n, arm, [os.path.join(base, arm, "N64Recomp", "RecompiledFuncs")])
                     for n in retry for arm in ("a", "b")}
            for k, f in futs2.items():
                r2 = f.result()
                if r2[0] == 0 or first[k][0] != 0: first[k] = r2 if r2[0] == 0 else first[k]
            for n in names:
                (ra, ta), (rb, tb) = first[(n, "a")], first[(n, "b")]
                la, lb = ta.splitlines(), tb.splitlines()
                nd = sum(1 for x, y in zip(la, lb) if x != y) + abs(len(la) - len(lb))
                out[n] = (ra, rb, ta == tb, nd, ([x for x in la if x not in set(lb)][:3] if ta != tb else la[-1:]), [y for y in lb if y not in set(la)][:3])
    finally:
        shutil.rmtree(base, ignore_errors=True)
    return out


def main():
    verbose = "--verbose" in sys.argv
    split = live_split()
    aff, wrows = affected(split)
    pre = chain_pre()
    print("reference split: %d functions, weak headers %d" % (len(split), sum(1 for x in split if x[1] in WEAK)))
    print("affected:", ", ".join("%s(%s)" % (k, v) for k, v in aff.items()))
    print("rows a blind whole-tree split mis-attributes:", wrows, "total", sum(wrows.values()))
    paths = sorted(glob.glob(os.path.join(ROOT, "tools", "*.py")))
    paths = [p for p in paths if os.path.basename(p) != "s7420_parser_census.py"]
    ptree, pweak = patches_tree_tools(), patches_tree_weak()
    print("patches tree (RecompiledPatches/patches.c) tools: %s; weak headers there: %d" % (",".join(sorted(ptree)) or "-", pweak))
    rows = audit(paths, split, aff, pre, verbose, ptree, pweak)
    from collections import Counter
    print("tools with a RECOMP_FUNC constant: %d; weak-blind: %d" % (len(rows), sum(1 for r in rows if r[5])))
    print("by phase x verdict:", dict(Counter((r[1], r[7]) for r in rows)))
    for r in rows:
        if r[7] not in ("ok", "BLIND-NOHIT") or verbose:
            print("  %-44s %-10s editor=%d consts=%d blind=%d hits=%s -> %s" % (r[0], r[1], r[2], r[4], len(r[5]), ",".join(r[6]) or "-", r[7]))
            if verbose:
                for b in r[5][:3]: print("      L%d %s %r" % b)
    nopen = sum(1 for r in rows if r[7] == "OPEN")
    if "--dynamic" in sys.argv:
        names = [r[0] for r in rows if r[5] and r[1] == "STANDALONE" and not r[2] and not r[0].startswith("apply_")]
        names += [r[0] for r in rows if r[5] and r[1] == "STANDALONE" and r[2] and not r[0].startswith(("apply_", "fixup_"))]
        names = sorted(set(names))
        res = dynamic(names)
        # rc != 0 in both arms with equal text is a tool that never got to the tree (missing input, needs args): not a null.
        unev = [n for n in names if res[n][2] and res[n][0] != 0 and res[n][1] != 0]
        neq = [n for n in names if not res[n][2]]
        print("DYNAMIC %d blind standalone tools, live vs de-weakened copy: %d equal (rc 0), %d differ, %d UNEVALUATED (same failure both arms)"
              % (len(names), len(names) - len(neq) - len(unev), len(neq), len(unev)))
        for n in names:
            ra, rb, eq, nd, xa, xb = res[n]
            if not eq or n in unev or verbose:
                print("  %-36s rc %s/%s %s ndiff=%d" % (n, ra, rb, "UNEVALUATED" if n in unev else "EQUAL" if eq else "DIFFER", nd))
                if n in unev: xa = xa or []; print("      tail : %s" % (res[n][4][-1][:200] if res[n][4] else "-"))
                for x in xa: print("      live : %s" % x[:200])
                for y in xb: print("      deweak: %s" % y[:200])
    ok = True
    if "--controls" in sys.argv:
        td = tempfile.mkdtemp(prefix="s7420_ctl_")
        try:
            a = os.path.join(td, "ctl_blind_editor.py")
            open(a, "w").write("import re,pathlib\np=pathlib.Path('x/funcs_1.c')\nt=p.read_text()\n"
                               "m=re.compile(r'^RECOMP_FUNC void setRngSeed\\(', re.M)\np.write_text(m.sub('X', t))\n")
            b = os.path.join(td, "ctl_aware_reader.py")
            open(b, "w").write("import re\nH=re.compile(r'^(?:__attribute__\\(\\(weak\\)\\) )?RECOMP_FUNC void (\\w+)\\(', re.M)\n"
                               "print(H.findall(open('RecompiledFuncs/funcs_1.c').read()))\n")
            ca = audit([a, b], split, aff, pre)
            c1 = ca[0][7] == "OPEN"
            c2 = not ca[1][5]
            f1 = os.path.join(FUNCS, "funcs_1.c")
            t = open(f1, errors="replace").read()
            hs = [m for m in HDR.finditer(t) if m.group(1) not in WEAK]
            victim = hs[len(hs) // 2]
            t2 = t[:victim.start()] + "__attribute__((weak)) " + t[victim.start():]
            blindre = re.compile(r'^RECOMP_FUNC void (\w+)\(')
            def split_rows(text, rx):
                cur, d = None, {}
                for l in text.splitlines():
                    m = rx.match(l)
                    if m: cur = m.group(1)
                    for _ in CMT.finditer(l): d[cur] = d.get(cur, 0) + 1
                return d
            r1, r2 = split_rows(t, blindre), split_rows(t2, blindre)
            c3 = victim.group(1) in r1 and victim.group(1) not in r2
            print("CONTROL planted blind editor -> %s (%s); weak-aware reader blind=%d (%s); planted weak header on %s moves %d rows (%s)"
                  % (ca[0][7], "PASS" if c1 else "FAIL", len(ca[1][5]), "PASS" if c2 else "FAIL", victim.group(1),
                     r1.get(victim.group(1), 0), "PASS" if c3 else "FAIL"))
            # (4) s7563: the IMMUNE-TREE verdict must reopen when the patches tree carries a weak header
            pt = open(PATCHES_C, errors="replace").read() if os.path.exists(PATCHES_C) else ""
            if not pt:  # s7806: tree absent -> plant into a synthetic one-function patches text so the control still fires
                pt = "RECOMP_FUNC void setRngSeed(uint8_t* rdram, recomp_context* ctx) {\n}\n"
                print("patches tree absent: control (4) uses a synthetic patches text")
            pw = patches_tree_weak(re.sub(r'^RECOMP_FUNC void ', '__attribute__((weak)) RECOMP_FUNC void ', pt, count=1, flags=re.M))
            fp = os.path.join(ROOT, "tools", "fixup_patches_host.py")
            cl = audit([fp], split, aff, pre, ptree=ptree, pweak=pw)
            cc = audit([fp], split, aff, pre, ptree=ptree, pweak=0)
            c4 = bool(pt) and pw == 1 and cl[0][7] == "OPEN" and cc[0][7] == "IMMUNE-TREE"
            print("CONTROL planted weak header in patches tree -> %s, clean -> %s (%s)" % (cl[0][7], cc[0][7], "PASS" if c4 else "FAIL"))
            # (5) s7806: an absent tree must never read as clean
            ca5 = audit([fp], split, aff, pre, ptree=ptree, pweak=-1)
            c5 = ca5[0][7] == "DEFER"
            print("CONTROL absent patches tree -> %s (%s)" % (ca5[0][7], "PASS" if c5 else "FAIL"))
            ok = c1 and c2 and c3 and c4 and c5
        finally:
            shutil.rmtree(td, ignore_errors=True)
    ndefer = sum(1 for r in rows if r[7] == "DEFER")
    req = "--require-tree" in sys.argv
    print("VERDICT", "H-split" if nopen else "H-clean", "OPEN", nopen,
          ("DEFER %d (patches tree absent; rerun with --require-tree after the CMake build)%s" % (ndefer, " -> FAIL" if req else "")) if ndefer else "")
    sys.exit(1 if nopen or not ok or (req and ndefer) else 0)


if __name__ == "__main__":
    main()
