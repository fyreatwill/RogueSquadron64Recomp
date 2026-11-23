#!/usr/bin/env python3
"""s7632 class HD census: join tools/s7632_dd_scan.py (regex) and tools/s7632_dd_ast.py (clang AST) over the lib/rt64
per-list / per-command hot files, propagate gates through call sites, classify every default-reached row.

  python3 tools/s7632_dd_census.py SCAN.json AST.json [--plant-scan P.json --plant-ast P.json] [--drop-control]

Propagation (per source, fixpoint): entry(F) = weakest effective gate over F's in-hot call sites (ALWAYS when F has
none: reached via the GBI map table, an exported extern "C" entry, or a caller outside the hot files), with manual
entries below for HLE-only and signature-only functions; eff(row) = stronger(row gate, entry(fn)).
Strength: ALWAYS < SIG < BUDGET < ENV < ONCE < HLE.  Rows whose effective gate is ALWAYS are the default-on work.
Join key: (file, kind, name) with |line diff| <= 3 (print names normalised).  The joint ALWAYS rows are classified:
  functional   feeds rendering / a default-on feature (memo, fast path, pending-command state, provenance used by the hash)
  scalar       a diagnostic counter / ring slot / last-value store: O(1) per event, no allocation, no copy
  copy         copies or allocates per event  -> the only kind worth a timed A/B
  OPEN         anything unclassified -> must be classified before the class closes"""
import json, re, sys
from collections import defaultdict

ORD = {"ALWAYS": 0, "SIG": 1, "BUDGET": 2, "ENV": 3, "ONCE": 4, "HLE": 5}
ENTRY = {  # manual entry gates (call sites outside the hot files or not visible as calls)
    "processDisplayLists": ("HLE", "HLE interpreter only; default LLE_FORCE=UNGATED=SOLO=1 returns before it (s7631)"),
}
CLASS = {
    # name -> (class, reason); checked for every joint default-on non-call row
    "g_s4271_ring": ("scalar", "64-slot ring of {pre,post,w0,w1} per RDP command: 4 stores, fixed static array"),
    "g_s4271_head": ("scalar", "ring cursor ++"),
    "g_s4271_lists": ("scalar", "32-slot per-list ring {start,end,pend,pendCur}"),
    "g_s4271_lhead": ("scalar", "list ring cursor ++"),
    "g_s4271_start": ("scalar", "last list bounds (pointer store)"),
    "g_s4271_end": ("scalar", "last list bounds (pointer store)"),
    "g_s4271_dl": ("scalar", "set/clear around setColorImage (s7631 fresh)"),
    "g_s4271_src": ("scalar", "set/clear around setColorImage"),
    "g_s4282_prev": ("copy", "vector swap per >=64 KB list (O(1) pointer swap, but feeds the next assign's reallocation)"),
    "g_s4282_prevbase": ("scalar", "pointer store per >=64 KB list"),
    "g_s4281_snap": ("copy", "vector::assign copies min(list, 256 KB) per >=64 KB RDP list; read only by s4282Probe / s4271DumpRing"),
    "g_s4281_base": ("scalar", "pointer store per >=64 KB list"),
    "s_rs64_pending_start_address": ("functional", "pending split-command bookkeeping (s_rs64_pending_* feed the split command's provenance and the RDP pending path)"),
    "s_rs64_pending_submit_serial": ("functional", "pending split-command bookkeeping"),
    "s_rs64_pending_submit_lo": ("functional", "pending split-command bookkeeping"),
    "s_rs64_pending_submit_hi": ("functional", "pending split-command bookkeeping"),
    "s_rs64_pending_task": ("functional", "pending split-command bookkeeping"),
    "s_rs64_tri_prev_address": ("scalar", "last-triangle record (4 scalar stores per tri command)"),
    "s_rs64_tri_prev_raw": ("scalar", "last-triangle record"),
    "s_rs64_tri_prev_length": ("scalar", "last-triangle record"),
    "s_rs64_tri_prev_valid": ("scalar", "last-triangle record"),
    "g_rs64_tmem_gen": ("functional", "s6942 TMEM generation: invalidates the default-on hash memo"),
    "g_rs64_lbf_fast": ("scalar", "s6957 LoadBlock fast-path hit counter"),
    "g_rs64_lbf_fall": ("scalar", "s6957 LoadBlock fallback counter"),
    "g_rs64_pc_arm": ("functional", "s6959 pcache arm latch read by the hash path (g_rs64_g1e_pcache, default 0 -> one compare)"),
    "rs64Memo": ("functional", "s6942 default-on TMEM hash memo"),
    "rs64TmemHashNeonCI4": ("functional", "hash dispatch counter/selector (s69xx NEON CI4 path)"),
    "rs64TmemHashGather": ("functional", "hash path selector / counters of the default-on gather hash"),
    "rs64TmemHashGatherStat": ("scalar", "gather hash stat counter"),
    "rs64TmemHashByteLoop": ("scalar", "byte-loop hash counter"),
    "rs64HgCalls": ("scalar", "hash-gather call counter"),
    "rs64HGS": ("scalar", "hash-gather stat struct counter"),
    "s_rs64_ff_w0": ("scalar", "s4531 image-word ring (fixed static arrays)"), "s_rs64_ff_w1": ("scalar", "s4531 ring"),
    "s_rs64_ff_n": ("scalar", "s4531 ring cursor"), "s_rs64_fe_w0": ("scalar", "s4531 ring"),
    "s_rs64_fe_w1": ("scalar", "s4531 ring"), "s_rs64_fe_n": ("scalar", "s4531 ring cursor"),
    "s_rdp_advance_ring": ("scalar", "s_rdp_advance ring slot"),
    "s_s7632": ("gated", "s7632 instrument accumulator: every store is under s_s7632Stats / the RAII `on`"),
    "g_s4280_n": ("scalar", "s4280 event ring count, bounded at 256 per process (g_s4280_n < 256)"),
    "g_s4280_ev": ("scalar", "s4280 event ring slot (<= 256 per process)"),
    "s7598_clamped": ("functional", "s7598 AZ-1 SETTILE mask clamp counter (the clamp itself is functional)"),
    "g_rs64_lbf_ctl": ("gated", "inside `if (rs64Chk)`, true only in ROGUESQ_G1E_LBFAST=c (g_rs64_g1e_lbfast == 3) check mode"),
    "g_rs64_lbf_chk": ("gated", "inside `if (rs64Chk)` (LBFAST=c check mode)"), "g_rs64_lbf_bad": ("gated", "inside `if (rs64Chk)`"),
    "g_rs64LoadSeq": ("scalar", "load sequence ++ per texture load"),
    "dumpedSet": ("gated", "upstream texture dump: callers test !state->dumpingTexturesDirectory.empty()"),
}

FNCLASS = {  # (fn, kind) -> class for the non-store rows the two extractors leave ALWAYS; each read by hand (s7632)
    ("setScissor", "getenv"): ("once", "static initialiser s_lsc"),
    ("setScissor", "print"): ("gated", "prints only when `fresh`, set only inside `if (s_lsc && ...)` (ROGUESQ_LOG_DEPTH_PAIR)"),
    ("rs64_note_image_word", "print"): ("once", "`if (!s_ctrl) { s_ctrl = 1; ... }`: one control line per process"),
    ("rs64DropGarbageCimg", "getenv"): ("once", "`static int s = -1; if (s < 0)` cache"),
    ("rs64DropGarbageCimg", "print"): ("gated", "inside the s<0 cache AND `if (s)` (ROGUESQ_DROP_GARBAGE_CIMG=1)"),
    ("rs64LogCimgRaw", "getenv"): ("once", "`static int s = -1; if (s < 0)` cache"),
    ("processRDPLists", "getenv"): ("once", "static initialiser (s6698 s_triDispatchLog / s7632 toggles)"),
    ("rs64SkipDrawSlow", "getenv"): ("once", "static initialiser; the caller is __builtin_expect(g_rs64SkipDrawArmed, 0) (s7441)"),
    ("rs64LogLoad", "getenv"): ("once", "static const char *s_dir initialiser"),
    ("setColorImage", "getenv"): ("once", "static initialiser s4271"),
    ("rs64_stage_count", "print"): ("gated", "after `if (!on) return;` (ROGUESQ_LOG_STAGES; AST source agrees)"),
    ("rs64_stage_add", "print"): ("gated", "after `if (!on) return;` (ROGUESQ_LOG_STAGES; AST source agrees)"),
    ("setTile", "print"): ("budget", "s7598 AZ-1 clamp: prints at n==1 and every 100000th clamp; s7599 measured 0 clamps in flight"),
    ("S7632Call", "print"): ("gated", "s7632 instrument: destructor returns unless on (= ROGUESQ_S7632_STATS)"),
    ("loadBlockOperation", "print"): ("budget", "first 12 RGBA32 loads per process (atomic n, i <= 12)"),
    ("drawRect", "print"): ("gated", "rs64RtPairRel() returns -1 unless ROGUESQ_LOG_RTPAIR_EPOCH (rt64_state.cpp:111)"),
    ("?", "getenv"): ("once", "file-scope static initialiser (runs at load)"),
    ("rs64_rdp_advance_report", "getenv"): ("once", "static initialiser"),
    ("loadToTMEMCommon", "print"): ("gated", "inside `if (rs64Chk)` (ROGUESQ_G1E_LBFAST=c check mode)"),
    ("uploadTexture", "getenv"): ("once", "FIXED s7632: were per-call getenv (TMEM_ZERO on w/h==0, UPSPAN on every new texture upload); now static initialisers"),
    ("uploadTMEM", "print"): ("budget", "s7343 TLUT clamp: prints when the clamp count is a power of two"),
}

def load(p): return json.load(open(p))["rows"]

def norm(r):
    r = dict(r)
    if r["kind"] == "print": r["name"] = "print"
    if r["kind"] == "getenv-static": r["kind"] = "getenv"
    return r

def propagate(rows, envfns):
    rows = [norm(r) for r in rows if not (r["kind"] == "call" and r["name"] in envfns)]
    fns = set(r["fn"] for r in rows)
    calls = defaultdict(list)
    for r in rows:
        if r["kind"] == "call": calls[r["name"]].append(r)
    entry = {f: "ALWAYS" for f in fns}
    for f, (g, _) in ENTRY.items(): entry[f] = g
    def eff(r):
        a, b = r["gate"], entry.get(r["fn"], "ALWAYS")
        return a if ORD[a] >= ORD[b] else b
    for _ in range(20):
        ch = False
        for f in list(entry):
            if f in ENTRY or not calls.get(f): continue
            g = min((eff(c) for c in calls[f]), key=lambda x: ORD[x])
            if g != entry[f]: entry[f] = g; ch = True
        if not ch: break
    for r in rows: r["eff"] = eff(r)
    return rows, entry

def join(A, B):
    used, both, aonly = set(), [], []
    idx = defaultdict(list)
    for j, b in enumerate(B): idx[(b["file"], b["kind"], b["name"])].append(j)
    for a in A:
        m = [j for j in idx[(a["file"], a["kind"], a["name"])] if j not in used and abs(B[j]["line"] - a["line"]) <= 3]
        if m:
            j = min(m, key=lambda j: abs(B[j]["line"] - a["line"])); used.add(j); both.append((a, B[j]))
        else: aonly.append(a)
    bonly = [B[j] for j in range(len(B)) if j not in used]
    return both, aonly, bonly

def envfns_of(*paths):
    s = set()
    for p in paths: s |= set(json.load(open(p)).get("envtok", []))
    return s

def census(scan_p, ast_p, drop=False, quiet=False):
    ef = envfns_of(scan_p, ast_p)
    S, es = propagate(load(scan_p), ef)
    A, ea = propagate(load(ast_p), ef)
    S = [r for r in S if r["kind"] != "call"]; A = [r for r in A if r["kind"] != "call"]
    if drop:  # control: delete one default-on row from each source; the join must report both as one-source-only
        # s7865: only rows both sources call ALWAYS (a scan-ALWAYS / ast-SIG row such as rs64_s7858_tick re-pairs the
        # dropped row's partner as a non-ALWAYS one-source row and the control reads a false FAIL)
        agree = [(a, b) for a, b in join(S, A)[0] if a["eff"] == "ALWAYS" and b["eff"] == "ALWAYS" and a["kind"] == "store"]
        sid, aid = {id(a) for a, _ in agree}, {id(b) for _, b in agree}
        ks = [i for i, r in enumerate(S) if id(r) in sid]
        ka = [i for i, r in enumerate(A) if id(r) in aid]
        S.pop(ks[0]); A.pop(ka[-1])  # different rows: the first from the regex source, the last from the AST source
    both, so, ao = join(S, A)
    agree = sum(1 for a, b in both if a["eff"] == b["eff"])
    out = dict(scan=len(S), ast=len(A), joint=len(both), gate_agree=agree, scan_only=so, ast_only=ao,
               gate_disagree=[(a, b) for a, b in both if a["eff"] != b["eff"]], always=[], entry_s=es, entry_a=ea)
    out["one_source"] = []
    for r in so + ao:
        if r["eff"] != "ALWAYS": continue
        c = (CLASS.get(r["name"]) if r["kind"] in ("store", "copy") else None) or FNCLASS.get((r["fn"], r["kind"])) or ("OPEN", "")
        out["one_source"].append(dict(r, cls=c[0], why=c[1], src="scan" if r in so else "ast"))
    for a, b in both:
        if a["eff"] == "ALWAYS" or b["eff"] == "ALWAYS":
            c = CLASS.get(a["name"]) if a["kind"] in ("store", "copy") else None
            c = c or FNCLASS.get((a["fn"], a["kind"])) or ("OPEN", "default-on " + a["kind"])
            out["always"].append(dict(a, cls=c[0], why=c[1], eff_ast=b["eff"]))
    return out

def show(o, label):
    print("== %s: scan=%d ast=%d joint=%d gate-agree=%d disagree=%d scan-only=%d ast-only=%d" % (
        label, o["scan"], o["ast"], o["joint"], o["gate_agree"], len(o["gate_disagree"]), len(o["scan_only"]), len(o["ast_only"])))
    for a, b in o["gate_disagree"]: print("  DISAGREE %s:%d %s %s %s scan=%s ast=%s" % (a["file"].split("/")[-1], a["line"], a["fn"], a["kind"], a["name"], a["eff"], b["eff"]))
    for lab, X in (("SCAN-ONLY", o["scan_only"]), ("AST-ONLY", o["ast_only"])):
        for r in X:
            if r["eff"] == "ALWAYS": print("  %s %s:%d %s %s %s eff=%s" % (lab, r["file"].split("/")[-1], r["line"], r["fn"], r["kind"], r["name"], r["eff"]))
    cnt = defaultdict(int)
    for r in o["always"]: cnt[r["cls"]] += 1
    print("  default-on joint rows by class:", dict(cnt))
    for r in o["always"]:
        print("  ALWAYS %-10s %s:%d %s %s %s%s" % (r["cls"], r["file"].split("/")[-1], r["line"], r["fn"], r["kind"], r["name"],
              "" if r["eff_ast"] == r["eff"] else " (ast=%s)" % r["eff_ast"]))

FRESH = dict(d="scratch/s7632", gen_args=(), scope=("lib/rt64/",))  # s7633 overrides: bridge files, scratch/s7633


def main():
    a = sys.argv[1:]
    if not a or a[0].startswith("--"):  # s7657: no inputs -> regenerate from the live tree (sweep gate), plants + drop-one
        import importlib.util as _ilu, os as _os
        _sp = _ilu.spec_from_file_location("ast_cache", _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "ast_cache.py"))
        _ac = _ilu.module_from_spec(_sp); _sp.loader.exec_module(_ac)
        a = _ac.fresh_census_args(FRESH["d"], "tools/s7632_dd_scan.py", "tools/s7632_dd_ast.py", "scratch/s7632/plant_hd.cpp",
                                  FRESH["gen_args"], FRESH["scope"]) + (a or ["--drop-control"])
    o = census(a[0], a[1]); show(o, "lib/rt64 hot files")
    ok = True
    if "--plant-scan" in a:
        p = census(a[a.index("--plant-scan") + 1], a[a.index("--plant-ast") + 1])
        pl = {(r["name"], r["kind"]): r["eff"] for r in p["always"] if r["file"].startswith("PLANT")}
        want_always = {("g_s9999_ring", "store"), ("g_s9999_snap", "copy")}
        ctl1 = want_always <= set(pl)
        # env-gated store (line 23) and SIG-only dump print must NOT be default-on in either source
        allp = [r for r in p["always"] if r["file"].startswith("PLANT")]
        ctl2 = not any(r["kind"] == "print" for r in allp)
        neg = [x for x in json.load(open(a[a.index("--plant-scan") + 1]))["rows"] if x["file"].startswith("PLANT") and x["gate"] in ("ENV", "SIG")]
        print("CONTROL plant: always rows %s -> %s; env/sig rows kept off default %s (%d gated rows) -> %s" % (
            sorted(pl), "PASS" if ctl1 else "FAIL", "yes" if ctl2 else "no", len(neg), "PASS" if ctl2 and neg else "FAIL"))
        ok &= ctl1 and ctl2 and bool(neg)
    if "--drop-control" in a:
        d = census(a[0], a[1], drop=True)
        n1 = sum(1 for r in d["scan_only"] if r["eff"] == "ALWAYS") - sum(1 for r in o["scan_only"] if r["eff"] == "ALWAYS")
        n2 = sum(1 for r in d["ast_only"] if r["eff"] == "ALWAYS") - sum(1 for r in o["ast_only"] if r["eff"] == "ALWAYS")
        print("CONTROL drop-one: extra one-source ALWAYS rows scan-only +%d ast-only +%d -> %s" % (n1, n2, "PASS" if n1 >= 1 and n2 >= 1 else "FAIL"))
        ok &= n1 >= 1 and n2 >= 1
    for r in o["one_source"]:
        print("  ONE-SOURCE(%s) %-10s %s:%d %s %s %s" % (r["src"], r["cls"], r["file"].split("/")[-1], r["line"], r["fn"], r["kind"], r["name"]))
    opn = [r for r in o["always"] + o["one_source"] if r["cls"] == "OPEN"]
    print("OPEN default-on rows: %d; copy rows: %s" % (len(opn), sorted(set(r["name"] for r in o["always"] if r["cls"] == "copy"))))
    print("CONTROLS", "PASS" if ok else "FAIL")
    sys.exit(0 if ok and not opn else 1)  # s7657: was always 0, so a FAIL / OPEN row never gated anything

if __name__ == "__main__":
    main()
