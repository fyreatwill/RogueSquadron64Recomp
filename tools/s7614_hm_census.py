#!/usr/bin/env python3
"""s7614 class HM: pointer MEMBERS of static aggregates (a static / thread_local / file-scope object of record type, an array or
std container of such records, or an unnamed `static struct {...} x;`) whose member is a pointer-like value (T*, T*[N],
atomic<T*>, uintptr_t, iterator, a container whose ELEMENT is a pointer) held across calls. Class HP (s7613) covered static
variables whose own type is a pointer; a pointer to a record is still HP (its pointee's members are not static storage).

Sources (must agree on (file, var) AND on each var's top-level pointer-member set):
  regex  tools/s7614_hm_scan.py  (record bodies + static declarations + HP-token member-store scan)
  clang  tools/s7614_hm_ast.py -> tools/s7614_hm_join.py  (RecordDecl/FieldDecl/VarDecl over build/compile_commands.json,
         qualified-name join, typedef'd anonymous structs, function-type typedefs, recursion depth 4)
Auto (no row): fnptr (function pointer / callback typedef / std::function), str (char* tags), file (FILE*), queue (moodycamel
internals whose element is not a pointer).
Classes (ROW = (file basename, var, top member) -> class + proof regex over that file):
  base    the rdram base (contract B: every store into the member is `= rdram` / arm(rdram,...)), rdram never reallocated (s7613 B)
  retail  a guest-RAM view with libultra's own lifetime (contract V1: ViState.mode = TO_PTR(OSViMode, mode_) paired with
          mode_guest = mode_, or &dummy_mode; libultra's __osViNext->modep holds the same pointer across retraces)
  retailq a guest OSTask* parked in a host queue between submit and consume (contract Q1 + runtime witness W)
  fresh   pushed and popped inside one call (contract HF)
  hpvar   the static is an atomic/container of pointers to GUEST objects already classified by s7613 (gated)
  host    host-owned: static tables from generated code, mod code buffers, host return addresses for symbolisation, &host vector
  dead    declared, never referenced
Contracts:
 B   events.cpp `events_context.rdram = rdram;` sole store; overlays.cpp every `s7.rdram =` is `= rdram;`; dpc_bridge.cpp
     g_bf_guard.rd set only by arm(r, ...) and every `g_bf_guard.arm(` passes rdram.
 V1  events.cpp: stores to `->mode =` / `.mode =` (ViState) are only `mode` (after `OSViMode* mode = TO_PTR(OSViMode, mode_);`,
     followed by `next_state->mode_guest = mode_;`) or `&dummy_mode`.
 Q1  events.cpp: sp_task_queue.enqueue( only `task` in submit_rsp_task (task = TO_PTR(OSTask, task_)) and `nullptr` (shutdown);
     wait_dequeue only in task_thread_func.
 HF  mod_hooks.cpp run_hook: emplace_back(*ctx) < `*ctx = hook_contexts.back();` < pop_back(), no return between; every
     other use is a value read hook_contexts.back().r2/r3/f0 (the return-value helpers), never f_odd.
 U1  events.cpp: deleted_threads appears only in its declaration.
 W   (--witness LOG, ROGUESQ_LOG_M5_TASK_LIFETIME): every FIFO enqueue/consume pair of full-word rows carries identical 16 OSTask
     words, edges strictly alternate (one task outstanding); control: consume vs the NEXT enqueue must mismatch (>0).
--controls: (1) planted static struct with an OSMesgQueue* member set from TO_PTR -> regex lists it, no row -> OPEN, and the
 member-store scan flags it; (2) drop a row -> OPEN; (3) planted static std::vector<S> (S has T*) through the real clang AST
 path -> listed; (4) drop one var from the regex census -> disagreement OPEN; (5) plant `next_state->mode = TO_PTR(...)` -> V1
 OPEN; (6) plant a second sp_task_queue.enqueue -> Q1 OPEN; (7) remove the hook_contexts pop_back -> HF OPEN; (8) plant
 `s7.rdram = TO_PTR(...)` -> B OPEN; (9) witness control: off-by-one pairing mismatches.
"""
import collections, importlib.util, json, os, re, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import importlib.util as _ilu
_acs = _ilu.spec_from_file_location("ast_cache", os.path.join(ROOT, "tools/ast_cache.py")); ast_cache = _ilu.module_from_spec(_acs); _acs.loader.exec_module(ast_cache)
def _load(n, p):
    sp = importlib.util.spec_from_file_location(n, os.path.join(ROOT, p)); m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m); return m
jn = _load("hm_join", "tools/s7614_hm_join.py")
sc = _load("hm_scan", "tools/s7614_hm_scan.py")
AST_JSON = os.path.join(ROOT, "scratch/s7614/ast.json")
EV = "lib/N64ModernRuntime/ultramodern/src/events.cpp"
OV = "lib/N64ModernRuntime/librecomp/src/overlays.cpp"
MH = "lib/N64ModernRuntime/librecomp/src/mod_hooks.cpp"
DB = "src/rsp/dpc_bridge.cpp"

R = []
def row(f, vars_, fields, cls, proof, why):
    for var in vars_.split():
        for fl in fields.split():
            R.append((f, var, fl, cls, proof, why))

RA = r"__builtin_return_address\(|backtrace\("
row("events.cpp", "events_context", "rdram", "base", r"events_context\.rdram = rdram;", "rdram base (B)")
row("overlays.cpp", "s7", "rdram", "base", r"s7\.rdram = rdram;", "rdram base (B)")
row("dpc_bridge.cpp", "g_bf_guard", "rd", "base", r"void arm\(uint8_t \*r, uint32_t l, bool c\) \{ on = true; ctl = c; hit = false; rd = r;",
    "rdram base set by arm() (B: callers pass rdram)")
row("events.cpp", "events_context", "vi", "retail", r"next_state->mode = mode;\n    next_state->mode_guest = mode_;",
    "ViState.mode: TO_PTR of the osViSetMode argument, kept like libultra __osViNext->modep (V1)")
row("events.cpp", "events_context", "sp_task_queue", "retailq", r"events_context\.sp_task_queue\.enqueue\(task\);",
    "audio OSTask* view parked submit->consume; the guest keeps one task outstanding (Q1 + witness W)")
row("events.cpp", "events_context", "deleted_threads", "dead", r"moodycamel::ConcurrentQueue<OSThread\*> deleted_threads\{\};",
    "never referenced (U1)")
row("mod_hooks.cpp", "hook_contexts", "f_odd", "fresh", r"hook_contexts\.emplace_back\(\*ctx\);",
    "recomp_context copy pushed/restored/popped inside run_hook (HF); f_odd copied back into the ctx it came from")
row("threads.cpp", "cur_thr", "context", "hpvar", r"if \(s4586::enabled\(\)\) \{ s4586::cur_thr\.store\(t\);",
    "atomic<OSThread*> already class HP gated (s7613); context is a member of the guest OSThread, not static storage")
row("overlays.cpp", "sections_info", "code_sections", "host", r"sections_info = sections;",
    "copy of the generated section table descriptor (static host arrays from RecompiledFuncs)")
row("overlays.cpp", "overlays_info", "table", "host", r"overlays_info = overlays;", "generated overlay index table (static host data)")
row("recomp.cpp", "mod_context", "base_patched_code_handle regenerated_code_handle shim_functions", "host",
    r"std::unique_ptr<recomp::mods::ModContext> mod_context = std::make_unique", "mod loader host code buffers (no mods loaded)")
row("rs64_env_cache.cpp", "g_trace", "ra", "host", RA, "host return address (getenv trace)")
row("upstream_compat.cpp", "g_rs64_cf0 g_rs64_waittab", "ra", "host", RA, "host return address rings")
row("upstream_compat.cpp", "rows", "host_ra", "host", r"const uintptr_t host_ra = reinterpret_cast<uintptr_t>\(__builtin_return_address\(0\)\);",
    "host return address (VI caller table)")
row("upstream_compat.cpp", "s_s7317_live s_s7326_surv", "pc", "host", RA, "host return addresses (s7317/s7326 diag)")
row("upstream_compat.cpp", "s_s7325_freed s_s7325_ord", "fpc apc", "host", r"fpc\[0\] = __builtin_return_address\(0\);", "host return addresses")
row("upstream_compat.cpp", "s_s7475_live", "hpc bt", "host", RA, "host return addresses / backtrace")
row("upstream_compat.cpp", "s_s7475_wpc", "hpc", "host", RA, "host return address")
row("upstream_compat.cpp", "s_s7480_freed", "bt", "host", RA, "host backtrace")
row("s7096_fwd_cover.cpp", "g_m", "ex", "host", r"g_m\.ex = &g_ex;", "points at the host vector g_ex / g_cex")
row("s7324_rcp_spill.cpp", "g_dg", "o", "host", r"rs64_s7324_sym\(g\.o\.lopc\[j\]", "host return addresses (symbolised)")
row("s7324_rcp_spill.cpp", "g_ex", "pc", "host", r"rs64_s7324_sym\(e\.pc\[j\]", "host return addresses (symbolised)")
row("rs64_settings.cpp", "p", "vars", "host", r"static const std::vector<Preset> p = \{",
    "s7663 preset table: function-local static const vector of string-literal (name, value) pairs; no rdram/TO_PTR in the TU")
row("s7331_reset_writer.cpp", "g_act g_fin", "own rown", "host", r"b->own = own;", "host return address from upstream_compat (b.pc[1])")

def src(rel):
    if rel.startswith("RF/"):
        return os.path.join(sc.sn.GEN, rel[3:])
    return os.path.join(ROOT, rel)

_txt = {}
def text(rel, ov=None):
    if ov and rel in ov:
        return ov[rel]
    if rel not in _txt:
        _txt[rel] = open(src(rel), errors="replace").read()
    return _txt[rel]

def contracts(ov=None, detail=False):
    bad, info = [], {}
    ev, ovl, mh, db = text(EV, ov), text(OV, ov), text(MH, ov), text(DB, ov)
    st = re.findall(r"events_context\.rdram\s*=(?!=)\s*([^;]*);", ev)
    s7 = re.findall(r"\bs7\.rdram\s*=(?!=)\s*([^;]*);", ovl)
    bfa = re.findall(r"g_bf_guard\.arm\(([^,]*),", db)
    bfrd = re.findall(r"(?<![\w.])rd\s*=(?!=)\s*([^;]*);", db[db.find("struct Rs64BfGuard"):db.find("static Rs64BfGuard g_bf_guard;")])
    info["B"] = dict(ev=st, s7=s7, bf_arm=bfa, bf_rd=bfrd)
    if not (st == ["rdram"] and s7 and all(x == "rdram" for x in s7) and bfa and all(x.strip() == "rdram" for x in bfa) and sorted(bfrd) == ["nullptr", "r"]):
        bad.append("B")
    ms = re.findall(r"(?:->|\.)mode\s*=(?!=)\s*([^;]*);", ev)
    pair = re.search(r"OSViMode\* mode = TO_PTR\(OSViMode, mode_\);\n(?:.*\n){0,2}?\s*next_state->mode = mode;\n\s*next_state->mode_guest = mode_;", ev)
    info["V1"] = dict(stores=ms, paired=bool(pair))
    if not (pair and ms and all(x.strip() in ("mode", "&dummy_mode") for x in ms) and ms.count("mode") == 1):
        bad.append("V1")
    enq = re.findall(r"events_context\.sp_task_queue\.enqueue\(([^;]*)\);", ev)
    deq = [m.start() for m in re.finditer(r"sp_task_queue\.wait_dequeue\(", ev)]
    tf = re.search(r"void task_thread_func\([^)]*\) \{", ev)
    sub = re.search(r"void ultramodern::submit_rsp_task\(RDRAM_ARG PTR\(OSTask\) task_\) \{\n(.*?)\n\}", ev, re.S)
    nxt = ev.find("\n}\n", tf.end()) if tf else -1
    q_ok = (sorted(enq) == ["nullptr", "task"] and sub and "OSTask* task = TO_PTR(OSTask, task_);" in sub.group(1)
            and "sp_task_queue.enqueue(task);" in sub.group(1) and len(deq) == 1 and tf and tf.end() < deq[0] < nxt)
    info["Q1"] = dict(enqueue=enq, dequeues=len(deq))
    if not q_ok:
        bad.append("Q1")
    rh = re.search(r"void recomp::mods::run_hook\([^)]*\) \{(.*?)\n\}", mh, re.S)
    hf = False
    if rh:
        b = rh.group(1)
        a0, r0, p0 = b.find("hook_contexts.emplace_back(*ctx);"), b.find("*ctx = hook_contexts.back();"), b.find("hook_contexts.pop_back();")
        hf = 0 <= a0 < r0 < p0 and not re.search(r"\breturn\b", b[a0:p0])
        uses = len(re.findall(r"\bhook_contexts\b", mh))
        # every other use is a VALUE read of the saved return registers (never the f_odd pointer member)
        reads = len(re.findall(r"\bhook_contexts\.back\(\)\.(?:r2|r3|f0\.fl|f0\.d)\b", mh))
        hf = hf and uses == 4 + reads and not re.search(r"^(?!\s*//).*\bf_odd\b", mh, re.M)
        info["HF"] = dict(push=a0, restore=r0, pop=p0, uses=uses, value_reads=reads)
    if not hf:
        bad.append("HF")
    u = len(re.findall(r"\bdeleted_threads\b", ev))
    info["U1"] = dict(refs=u)
    if u != 1:
        bad.append("U1")
    if detail:
        for k, v in info.items():
            print("  %s %s" % (k, v))
    return bad

def rowkey(f, var):
    return ("RF" if f.startswith("RF/") else os.path.basename(f), var)

def classify(members, rows, ov=None):
    rmap = {(f, v, fl): (c, p, w) for f, v, fl, c, p, w in rows}
    used, res = set(), []
    per = collections.defaultdict(set)
    for x in members:
        if x["kind"] == "ptr":
            per[(x["file"], x["var"])].add(x["field"].split(".")[0])
    for (f, v), fls in sorted(per.items()):
        for fl in sorted(fls):
            k = rowkey(f, v) + (fl,)
            if k not in rmap:
                res.append((f, v, fl, "OPEN", "no row")); continue
            used.add(k)
            c, p, w = rmap[k]
            if not re.search(p, text(f, ov)):
                res.append((f, v, fl, "DRIFT", "proof missing: " + p)); continue
            res.append((f, v, fl, c, w))
    stale = [k for k in rmap if k not in used]
    return res, stale

def census_diff(members, scan):
    A = collections.defaultdict(set)
    for x in members:
        if x["kind"] == "ptr":
            A[(x["file"], x["var"])].add(x["field"].split(".")[0])
    S = {(v["file"], v["var"]): {f.split(".")[0] for f in v["fields"]} for v in scan["vars"]}
    a_only = sorted(k for k in set(A) - set(S)); s_only = sorted(k for k in set(S) - set(A))
    fdiff = sorted((k, sorted(A[k] ^ S[k])) for k in set(A) & set(S) if A[k] != S[k])
    return a_only, s_only, fdiff, len(A), len(S)

def stores_open(scan, rows):
    """HP-token member stores whose field is not a classified member of some row."""
    fields = {fl for _, _, fl, _, _, _ in rows} | {"rdram", "mode"}
    return [s for s in scan["stores"] if s["field"] not in fields]

def witness(path):
    rows = []
    for l in open(path, errors="replace"):
        if not l.startswith("[m5-task-lifetime]"):
            continue
        m0 = re.search(r"edge=(\w+) .*?seq=(\d+)", l)
        m = re.search(r"words=((?:[0-9A-F]{8},){15}[0-9A-F]{8})", l)
        if m0:
            rows.append((int(m0.group(2)), m0.group(1), m.group(1) if m else None))
    rows.sort()
    enq = [r for r in rows if r[1] == "enqueue"]; con = [r for r in rows if r[1] == "consume"]
    n = min(len(enq), len(con))
    alt = n > 0 and all(enq[i][0] < con[i][0] for i in range(n)) and all(con[i][0] < enq[i + 1][0] for i in range(n - 1))
    cmp = [(enq[i][2], con[i][2]) for i in range(n) if enq[i][2] and con[i][2]]
    eq = sum(a == b for a, b in cmp)
    ctl = [(enq[i + 1][2], con[i][2]) for i in range(n - 1) if enq[i + 1][2] and con[i][2]]
    mism = sum(a != b for a, b in ctl)
    ok = bool(cmp) and eq == len(cmp) and alt and mism > 0
    print("witness %s: rows %d pairs %d full-word %d equal %d torn %d alternation %s | control off-by-one mismatches %d/%d -> %s"
          % (os.path.relpath(path, ROOT), len(rows), n, len(cmp), eq, n - len(cmp), alt, mism, len(ctl), "PASS" if ok else "FAIL"))
    return ok

def run_controls(members, scan, ast):
    ok = total = 0
    def expect(name, cond):
        nonlocal ok, total
        total += 1; ok += bool(cond); print("  control %-72s %s" % (name, "PASS" if cond else "FAIL"))
    planted = ("#include <vector>\n#include <cstdint>\ntypedef struct { int validCount; } OSMesgQueue;\n"
               "struct S7614P { OSMesgQueue* q; uint32_t n; };\nstatic S7614P s_pl;\n"
               "struct S7614V { int* p; };\nstatic std::vector<S7614V> s_plv;\n"
               "extern \"C\" void rs64_planted_set(unsigned char* rdram, unsigned a) { s_pl.q = (OSMesgQueue*)(rdram + (a & 0xFFFFFF)); }\n"
               "extern \"C\" int rs64_planted_use() { return s_pl.q->validCount + (int)s_plv.size(); }\n")
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "planted_hm.cpp"); open(p, "w").write(planted)
        s2 = sc.scan([p])
        pv = {v["var"] for v in s2["vars"] if v["file"].endswith("planted_hm.cpp")}
        st = [x for x in s2["stores"] if x["file"].endswith("planted_hm.cpp")]
        fake = [dict(file=os.path.relpath(p, ROOT), var="s_pl", field="q", kind="ptr")]
        _txt[os.path.relpath(p, ROOT)] = planted
        r, _ = classify(fake, R)
        expect("(1) planted static struct {OSMesgQueue* q} from rdram+: listed, no row -> OPEN, store flagged",
               "s_pl" in pv and any(x[3] == "OPEN" for x in r) and any(x["field"] == "q" for x in stores_open(s2, R)))
        # (3) through the real clang AST path: compile the planted TU with an existing src TU's flags
        cc = json.load(open(os.path.join(ROOT, "build/compile_commands.json")))
        e = next(x for x in cc if x["file"].endswith("src/rsp/s7331_reset_writer.cpp"))
        e = dict(e); e["command"] = e["command"].replace(e["file"], p); e["file"] = p
        hpa = jn  # noqa
        astmod = _load("hm_ast", "tools/s7614_hm_ast.py")
        astmod.hpa.in_scope = lambda f, _o=astmod.hpa.in_scope: _o(f) or os.path.normpath(f) == os.path.normpath(p)
        astmod.rec_scope = lambda f, _o=astmod.rec_scope: _o(f) or os.path.normpath(f) == os.path.normpath(p)
        _, rc, recs, vs, ft = astmod.run_one(e)
        m2 = jn.members(dict(records=recs, vars=vs, fn_typedefs=ft))
        got = {(x["var"], x["field"]) for x in m2 if x["kind"] == "ptr"}
        expect("(3) planted static std::vector<S7614V{int* p}> + S7614P via clang AST -> listed", rc == 0 and {("s_plv", "p"), ("s_pl", "q")} <= got)
    r, _ = classify(members, [x for x in R if x[1] != "events_context" or x[2] != "sp_task_queue"])
    expect("(2) drop the events_context.sp_task_queue row -> OPEN", any(x[1] == "events_context" and x[2] == "sp_task_queue" and x[3] == "OPEN" for x in r))
    sc2 = dict(scan); sc2["vars"] = [v for v in scan["vars"] if v["var"] != "hook_contexts"]
    a_only = census_diff(members, sc2)[0]
    expect("(4) drop hook_contexts from the regex census -> disagreement OPEN", [k[1] for k in a_only] == ["hook_contexts"])
    base = contracts()
    ev = text(EV)
    expect("(5) plant `next_state->mode = TO_PTR(OSViMode, 0x80001000)` -> V1 OPEN", "V1" not in base and "V1" in contracts(
        {EV: ev.replace("    next_state->mode = &dummy_mode;\n", "    next_state->mode = TO_PTR(OSViMode, 0x80001000);\n", 1)}))
    expect("(6) plant a second sp_task_queue.enqueue -> Q1 OPEN", "Q1" not in base and "Q1" in contracts(
        {EV: ev.replace("events_context.sp_task_queue.enqueue(task);", "events_context.sp_task_queue.enqueue(task); events_context.sp_task_queue.enqueue(TO_PTR(OSTask, 0x80149470));", 1)}))
    mh = text(MH)
    expect("(7) remove the hook_contexts pop_back -> HF OPEN", "HF" not in base and "HF" in contracts({MH: mh.replace("    hook_contexts.pop_back();\n", "", 1)}))
    ovl = text(OV)
    expect("(8) plant `s7.rdram = TO_PTR(uint8_t, 0x80000000)` -> B OPEN", "B" not in base and "B" in contracts(
        {OV: ovl.replace("s7.rdram = rdram;", "s7.rdram = TO_PTR(uint8_t, 0x80000000);", 1)}))
    print("controls %d/%d" % (ok, total))
    return ok == total

def main():
    a = sys.argv[1:]
    if "--ast" in a or not os.path.exists(AST_JSON):
        subprocess.run([sys.executable, os.path.join(ROOT, "tools/s7614_hm_ast.py"), "--out", AST_JSON], check=True)
    else:
        ast_cache.ensure(AST_JSON, "tools/s7614_hm_ast.py")  # s7655: regenerate when any source is newer than the cache
    ast = json.load(open(AST_JSON))
    members = jn.members(ast)
    scan = sc.scan()
    res, stale = classify(members, R)
    cnt = collections.Counter(x[3] for x in res)
    kinds = collections.Counter(x["kind"] for x in members)
    a_only, s_only, fdiff, na, ns = census_diff(members, scan)
    so = stores_open(scan, R)
    print("AST: %d TUs failed=%s, %d member rows %s | vars with pointer members: clang %d, regex %d"
          % (ast["tu"], ast["failed"], len(members), dict(kinds), na, ns))
    print("rows (var, member): %d -> %s" % (len(res), dict(sorted(cnt.items()))))
    for f, v, fl, c, w in res:
        if c in ("OPEN", "DRIFT"):
            print("  %s %s %s.%s | %s" % (c, f, v, fl, w))
    for k in stale:
        print("  STALE row", k)
    print("census disagreement: AST-only %s regex-only %s member-set %s" % (a_only or "none", s_only or "none", fdiff or "none"))
    print("HP-token member stores %d, unclassified %s" % (len(scan["stores"]), so or "none"))
    bad = contracts(detail=True)
    print("contracts failing:", bad or "none")
    n = cnt["OPEN"] + cnt["DRIFT"] + len(stale) + len(a_only) + len(s_only) + len(fdiff) + len(so) + len(bad) + len(ast["failed"])
    rc = 0 if n == 0 else 1
    if "--witness" in a and not witness(a[a.index("--witness") + 1]):
        rc = 1
    if "--controls" in a and not run_controls(members, scan, ast):
        rc = 1
    print("RESULT", "PASS" if rc == 0 else "FAIL")
    sys.exit(rc)

if __name__ == "__main__":
    main()
