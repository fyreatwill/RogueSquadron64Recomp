#!/usr/bin/env python3
"""s7613 class HP: HOST pointers held in static / thread_local / file-scope storage and dereferenced on a LATER call.
A host view into guest RAM (TO_PTR, rdram + off, OSThread*/OSTask* views) goes semantically stale when the guest frees or
reuses the object, a new level/overlay rewrites the region, or the guest address changes while the host keeps the old view.

Candidates (tools/s7613_hp_scan.py): (A) declaration census of every pointer-typed static-storage variable, (B) HP-token
store scan whose target is pointer-shaped but missing from (A) ('missed' = OPEN). Second source: tools/s7613_hp_ast.py
(clang -ast-dump over build/compile_commands.json): the two censuses must list the same (file, name) set; a difference is
OPEN unless it is a row in AST_ONLY_OK / REGEX_ONLY_OK with a reason.
Classes (every non-auto decl needs a ROW (file basename or 'RF', name) -> class + proof regex over the whole file):
  base     the rdram base (or base + constant physical offset, page-masked): rdram is allocated ONCE per process and freed
           after every game/event thread is joined (contract B). Every store into the name must be base-shaped (B1) and
           every function that receives the base as a parameter and parks it is called only with the base (B2).
  host     host-owned memory / handles / code: calloc/malloc/new/vector storage, SDL/RT64/pthread handles, function
           pointers, host return addresses, iterators into host containers, string-literal tags.
  gated    a guest view whose every store and reader sits behind a default-off env gate (proof = the gate).
  fresh    set and restored inside ONE call (contract F1).
  logonly  a guest view read later but only into logs / diagnostic joins, never written through, never steering
           guest-visible state (contract H1).
  dead     not compiled on macOS (#ifdef _WIN32) - the AST census, which is the macOS preprocessor's view, omits it.
Auto: fnptr (declared `T (*name)(...)`) = host code pointer.
Contracts:
 B  recomp.cpp: rdram assigned exactly twice (VirtualAlloc / mmap, #if branches), released only by munmap/VirtualFree in
    the shutdown block after game_thread.join() and join_event_threads().
 B1 every store into a base row's name has a base-shaped RHS.
 B2 call sites of rs64_s7097_begin / rs64_wbw_pre / rs64_s7096_end / rs64_s7523_end pass rdram / RDRAM / g_rdram_for_submit.
 F1 rsp.cpp run_task: `previous_audio_probe = g_audio_dma_probe` precedes `g_audio_dma_probe = &audio_dma_probe;`, and
    `g_audio_dma_probe = previous_audio_probe;` follows the ucode_func call with no return in between.
 H1 main.cpp s_pending_audio_task: one store (`= task;` in get_rsp_microcode's M_AUDTASK case); every reader is the
    `s_pending_audio_task == nullptr ? 0u : static_cast<uint32_t>(s_pending_audio_task->t.data_(ptr|size))` read form
    (no write through it, no other field); the resulting locals reach only fprintf / rs64_audio_join_* /
    g_rs64_m5_last_input_task_data_ptr (itself read only into fprintf / a join local); the join functions contain no
    MEM_ / rdram store.
--controls: (1) planted static OSMesgQueue* from TO_PTR used in a later call -> OPEN; (2) drop a row -> OPEN; (3) planted
 pointer declared with an initializer (static OSThread* p = TO_PTR(...)) -> OPEN via the declaration census; (4) remove the
 g_audio_dma_probe restore -> F1 OPEN; (5) plant a write through s_pending_audio_task -> H1 OPEN; (6) plant a second rdram
 allocation -> B OPEN; (7) plant a non-base store into a base row -> B1 OPEN; (8) drop one decl from the regex census ->
 census disagreement OPEN; (9) multi-declarator `static int a, *s_p2;` and `thread_local` after `;` -> found.
"""
import importlib.util, json, os, re, subprocess, sys, tempfile, collections, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import importlib.util as _ilu
_acs = _ilu.spec_from_file_location("ast_cache", os.path.join(ROOT, "tools/ast_cache.py")); ast_cache = _ilu.module_from_spec(_acs); _acs.loader.exec_module(ast_cache)
_sp = importlib.util.spec_from_file_location("hp_scan", os.path.join(ROOT, "tools/s7613_hp_scan.py"))
hp = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(hp)
sn = hp.sn
AST_JSON = os.path.join(ROOT, "scratch/s7613/ast.json")

R = []
def row(f, names, cls, proof, why):
    for n in names.split():
        R.append((f, n, cls, proof, why))

BASE_RHS = r"(?:rdram|rd|RDRAM|g_rdram_for_submit)"
# ---- base
row("main.cpp", "g_flz_fault_rdram g_m5_host_fault_rdram g_m5_task_fault_rdram g_vtx_fault_rdram", "base",
    r"while \(!\(rdram = \(uint8_t\*\)g_recomp_rdram_for_wp_raw\)\)", "write-fault watch threads: rdram from g_recomp_rdram_for_wp_raw")
row("main.cpp", "g_m5_host_fault_page g_m5_task_fault_page g_vtx_fault_pages", "base",
    r"\(\(uintptr_t\)rdram \+ 0x128C92u\)|uintptr_t host = \(uintptr_t\)rdram \+ ranges\[i\];",
    "page of rdram + fixed physical offset: an ADDRESS watch, not an object view")
row("main.cpp", "g_recomp_rdram_for_wp_raw", "base", r"g_recomp_rdram_for_wp_raw = rdram;", "published base")
row("main.cpp", "g_wbw_rd", "base", r"g_wbw_rd\.store\(rd\);", "s6938/wbw page watch base (B2: callers pass RDRAM)")
row("upstream_compat.cpp", "s7033_rd", "base", r"s7033_rd = rdram;", "base")
row("upstream_compat.cpp", "g_rs64_g1d_rdram", "base", r"g_rs64_g1d_rdram\.store\(rdram, std::memory_order_relaxed\);", "base")
row("upstream_compat.cpp", "g_s6127_rd", "base", r"g_s6127_rd = rdram;", "base")
row("dpc_bridge.cpp", "g_rdram_for_submit", "base", r"g_rdram_for_submit = rdram;", "base")
row("s7096_fwd_cover.cpp", "g_rd", "base", r"if \(rdram\) g_rd = rdram;", "base (B2)")
row("s7097_edit_census.cpp", "g_rd", "base", r"g_rd = rd; g_lo = lo;", "base (B2: sole caller passes g_rdram_for_submit)")
row("s7523_slow_rdp.cpp", "g_rd", "base", r"if \(rdram\) g_rd = rdram;", "base (B2)")
row("events.cpp", "rs64_vi_feat_rdram", "base", r"rs64_vi_feat_rdram = rdram;", "base")
row("RF", "rs5901_rdram", "base", r"rs5901_rdram = rdram;", "base")
row("RF", "s4279_rd", "base", r"s4279_rd = rdram;", "base")
row("RF", "s5781_ram", "base", r"s5781_ram = rdram;", "base")
# s7739: s6505_rdram row dropped - s6505 is not in RS64_REPLAY, absent from the adopted regen tree
# ---- host-owned
row("main.cpp", "g_s4457_tab", "host", r"g_s4457_tab = \(S4457W\*\)std::calloc\(", "calloc table")
row("main.cpp", "g_s5229_pc g_s5229_val g_s5229_w", "host", r"g_s5229_pc = \(uint32_t\*\)std::calloc\(", "calloc tables")
row("main.cpp", "g_rsp_dma_shadow2_data", "host", r"g_rsp_dma_shadow2_data = s_sh2_buf\.data\(\);", "host vector storage")
row("main.cpp", "controller j1 j2", "host", r"SDL_GameController\* controller|SDL_Joystick\* j1", "SDL handles")
row("main.cpp", "g_rs64_window g_rs64_nswin g_rs64_layer", "host", r"static SDL_Window\* g_rs64_window", "SDL / Cocoa window handles")
row("main.cpp", "g_rs64_s7355_prev_hook", "host", r"pthread_introspection_hook_t g_rs64_s7355_prev_hook", "host function pointer")
row("main.cpp", "by", "host", r"std::map<uintptr_t, uint64_t> by;", "key = host return address (atos offline), gated ROGUESQ_CAM_CALLER")
row("main.cpp", "s_pad s_hap", "host", r"static SDL_GameController\* s_pad = nullptr;\s*static SDL_Haptic\* s_hap = nullptr;", "s7655: G6a rumble path cache, SDL handles compared with `controller`")
row("main.cpp", "s_bind_vpad", "host", r"static SDL_Joystick\* s_bind_vpad = nullptr;", "s7655: G6b ROGUESQ_BIND_SELFTEST virtual SDL joystick handle")
row("rs64_controls_panel.cpp", "g_ctx", "host", r"ImGuiContext\* g_ctx = nullptr;", "s7655: G6b F6 panel ImGui context (host heap)")
row("s7702_fbread.cpp", "g_pend_hk", "host", r"Hk\* g_pend_hk = nullptr;", "s7707: host pointer into the s7702 g_hk[256] table (never a guest address); ROGUESQ_S7702_FBREAD only")
row("s7644_rspdma.cpp", "g_gtid", "host", r"pthread_t g_gtid;", "s7655: pthread_t handle (opaque pointer on macOS), only pthread_equal-compared; ROGUESQ_S7644_RSPDMA&2 only")
row("rs64_env_cache.cpp", "g_real_getenv f", "host", r"std::atomic<getenv_fn> g_real_getenv|static setenv_fn f", "libc function pointers")
row("rt64_render_context.cpp", "g_rt64_app", "host", r"std::atomic<RT64::Application\*> g_rt64_app", "RT64 application object")
row("rt64_render_context.cpp", "snap", "host", r"snap\[0\] = \(uint8_t \*\)std::malloc\(SZ\);", "malloc snapshot buffers")
row("upstream_compat.cpp", "s_ra", "host", r"s_ra\[s_n\] = ra_host;", "host return addresses")
row("upstream_compat.cpp", "s_s7325_ord", "host", r"s_s7325_ord\.push_back\(s_s7325_freed\.emplace\(", "iterators into a host multimap, erased together")
row("upstream_compat.cpp", "g_s4913_last_tag", "host", r'g_s4913_last_tag\{"none"\}', "string-literal tag")
row("upstream_compat.cpp", "s", "host", r"static S7064\* s = \[\] \{ auto\* x = new S7064;", "new'd host state")
row("upstream_compat.cpp", "g_rs64_s7475_bm", "host", r"g_rs64_s7475_bm = \(unsigned char\*\)std::calloc\(", "calloc bitmap")
row("dpc_bridge.cpp", "g_bf2_thr", "host", r"g_bf2_thr = pthread_self\(\);", "pthread handle")
row("dpc_bridge.cpp", "shV", "host", r"shV\[i\] = &e;", "pointers into the host g_s4272_sh vector, rebuilt per lookup table build")
row("s7331_reset_writer.cpp", "g_act g_fin", "host", r"std::vector<Blk\*> g_act, g_fin;", "host Blk records")
row("s7535_ga_chk.cpp", "g_gfx", "host", r"g_gfx = pthread_self\(\);", "pthread handle")
row("overlays.cpp", "patch_code_sections", "host", r"patch_code_sections = sections;", "host section table (static data)")
row("overlays.cpp", "func_map base_exports ext_base_exports manual_patch_symbols_by_vram", "host",
    r"std::unordered_map<int32_t, recomp_func_t\*> func_map", "host code pointers keyed by guest address (class OV, s7610)")
row("overlays.cpp", "section_addresses", "host", r"int32_t\* section_addresses = nullptr;", "host array (make_unique in mods.cpp) of guest load addresses")
row("mesgqueue.cpp", "g_s4911_host_ra", "host", r"thread_local void\* g_s4911_host_ra", "host return address (dladdr)")
row("threads.cpp", "g_live_ctx deleted_threads", "host", r"std::unordered_set<UltraThreadContext\*> g_live_ctx", "host thread contexts")
row("RF", "s_ra", "host", r"static uintptr_t s_ra\[64\];", "host return addresses (s5910 postra census)")
# ---- guest views
row("scheduling.cpp", "g_s4583_t3", "gated", r'getenv\("ROGUESQ_LOG_S4583"\); en = .*\n    if \(!en\) return;',
    "OSThread* view, stored and read only after `if (!en) return` (ROGUESQ_LOG_S4583)")
row("threads.cpp", "cur_thr", "gated", r"if \(s4586::enabled\(\)\) \{ s4586::cur_thr\.store\(t\);",
    "OSThread* view for the s4587 sampler; stored only when s4586::enabled() (env), sampler started in the same branch")
row("rsp.cpp", "g_audio_dma_probe", "fresh", r"g_audio_dma_probe = previous_audio_probe;", "points at run_task's local probe; restored after the ucode (F1)")
row("main.cpp", "s_pending_audio_task", "logonly", r"s_pending_audio_task = task;", "OSTask* view, readers log-only (H1)")
row("main.cpp", "g_wp_addr", "dead", r"#ifdef _WIN32\nstatic volatile uintptr_t g_wp_addr", "Windows hardware-breakpoint watch")

AST_ONLY_OK = {}
REGEX_ONLY_OK = {("src/main/main.cpp", "g_wp_addr"): "inside #ifdef _WIN32: absent from the macOS AST"}

def src_path(rel):
    return os.path.join(sn.GEN, rel[3:]) if rel.startswith("RF/") else os.path.join(ROOT, rel)

def rowkey(c):
    return ("RF" if c["file"].startswith("RF/") else os.path.basename(c["file"]), c["name"])

_txt = {}
def text(rel, ov=None):
    if ov and rel in ov:
        return ov[rel]
    if rel not in _txt:
        _txt[rel] = open(src_path(rel), errors="replace").read()
    return _txt[rel]

def b1_bad(rel, name, ov=None):
    """stores into a base name whose RHS is not base-shaped."""
    bad = []
    pat = re.compile(r"(?<![\w.>])" + re.escape(name) + r"\s*(?:\[[^\]]*\]\s*)?(?:=(?!=)\s*([^;]*)|\.store\(\s*([^,;)]*))")
    for i, l in enumerate(text(rel, ov).split("\n")):
        s = sn.strip(l)
        for m in pat.finditer(s):
            pre = s[:m.start()]
            if re.search(r"(?:static|thread_local|extern)\b[^;]*$", pre) or re.search(r"[\w>]\s*[\*&]?\s*$", pre) and not re.search(r"[;{(]\s*$|^\s*$|\bif \([^)]*\)\s*$|\)\s*$", pre):
                continue  # declaration
            rhs = (m.group(1) if m.group(1) is not None else m.group(2)).strip()
            if re.fullmatch(r"(nullptr|0|NULL)", rhs) and re.search(r"static|thread_local", s):
                continue
            ok = (re.fullmatch(BASE_RHS, rhs) or re.fullmatch(r"\(\(uintptr_t\)rdram \+ 0x[0-9A-Fa-f]+u\) &", rhs)
                  or re.fullmatch(r"host & ~\(uintptr_t\)\(g_vtx_fault_page - 1\)", rhs))
            if not ok:
                bad.append((i + 1, rhs[:60]))
    return bad

def contracts(ov=None, detail=False):
    bad = []; info = {}
    rc = text("lib/N64ModernRuntime/librecomp/src/recomp.cpp", ov)
    allocs = re.findall(r"^\s*rdram = [^;]*;", rc, re.M)
    jm = re.search(r"game_thread\.join\(\);\s*\n\s*ultramodern::join_event_threads\(\);", rc)
    frees = [m.start() for m in re.finditer(r"VirtualFree\(rdram, 0, MEM_RELEASE\) == 0|munmap\(rdram, allocation_size\) == -1", rc)]
    info["B"] = dict(allocs=len(allocs), frees=len(frees), joined=bool(jm))
    if not (len(allocs) == 2 and jm and len(frees) == 2 and all(f > jm.end() for f in frees)):
        bad.append("B")
    b1 = {}
    for f, n, c, p, w in R:
        if c != "base":
            continue
        for rel in files_for(f, n):
            x = b1_bad(rel, n, ov)
            if x:
                b1[(rel, n)] = x
    info["B1"] = b1
    if b1:
        bad.append("B1")
    calls = []
    for p in ([src_path(r) for r in ("src/rsp/dpc_bridge.cpp",)] + glob.glob(os.path.join(ROOT, "src/*/*.cpp")) +
              glob.glob(os.path.join(ROOT, "lib/rt64/src/*/*.cpp")) + glob.glob(os.path.join(ROOT, "lib/N64ModernRuntime/*/src/*.cpp"))):
        t = ov.get(os.path.relpath(p, ROOT)) if ov and os.path.relpath(p, ROOT) in ov else open(p, errors="replace").read()
        for m in re.finditer(r"\b(rs64_s7097_begin|rs64_wbw_pre|rs64_s7096_end|rs64_s7523_end)\(([^;]*)\)\s*;", t):
            if re.search(r"extern \"C\"[^\n]*$", t[max(0, m.start() - 80):m.start()]) or "uint8_t" in m.group(2):
                continue
            args = [a.strip() for a in m.group(2).split(",")]
            calls.append((os.path.relpath(p, ROOT), m.group(1), args))
    info["B2"] = [(f, n, a[-1] if n != "rs64_wbw_pre" else a[0]) for f, n, a in calls]
    want = {"rs64_s7097_begin": -1, "rs64_s7096_end": -1, "rs64_s7523_end": -1, "rs64_wbw_pre": 0}
    if not calls or any(not re.fullmatch(BASE_RHS, a[want[n]]) for f, n, a in calls):
        bad.append("B2")
    rs = text("lib/N64ModernRuntime/librecomp/src/rsp.cpp", ov)
    m = re.search(r"bool recomp::rsp::run_task\(uint8_t\* rdram, const OSTask\* task\) \{(.*?)\n\}", rs, re.S)
    ok = False
    if m:
        b = m.group(1)
        p0 = b.find("previous_audio_probe = g_audio_dma_probe"); s0 = b.find("g_audio_dma_probe = &audio_dma_probe;")
        u0 = b.find("ucode_func(rdram, task->t.ucode);"); r0 = b.find("g_audio_dma_probe = previous_audio_probe;")
        sets = len(re.findall(r"^(?!static)\s*g_audio_dma_probe = ", rs, re.M))
        ok = 0 <= p0 < s0 < u0 < r0 and not re.search(r"\breturn\b", b[s0:r0]) and sets == 2
        info["F1"] = dict(prev=p0, set=s0, ucode=u0, restore=r0, sets=sets)
    if not ok:
        bad.append("F1")
    mn = text("src/main/main.cpp", ov)
    stores = re.findall(r"^(?!static)\s*s_pending_audio_task\s*=(?!=)\s*([^;]*);", mn, re.M)
    # statements (joined across lines) that mention the pointer or the locals read from it
    body = "\n".join(sn.strip(l) for l in mn.split("\n"))
    stmts = [s.strip() for s in re.split(r";|\{|\}", body)]
    READ = r"s_pending_audio_task == nullptr \?\s*0u : static_cast<uint32_t>\(s_pending_audio_task->t\.data_(?:ptr|size)\)"
    HELPERS = ("rs64_m5_task_handoff", "rs64_audio_source_objects")
    odd, flows = [], []
    for s in stmts:
        if re.search(r"\bs_pending_audio_task\b", s):
            x = re.sub(READ, "", s)
            x = re.sub(r"^static thread_local const OSTask\* s_pending_audio_task = nullptr$|^s_pending_audio_task = task$", "", x)
            x = re.sub(r"\b(%s)\((?:rdram, )?s_pending_audio_task\)" % "|".join(HELPERS), "", x)
            if re.search(r"\bs_pending_audio_task\b", x):
                odd.append(s[:90])
        for nm in ("task_data_ptr", "task_data_size", "g_rs64_m5_last_input_task_data_ptr", "input_task_data_ptr"):
            if not re.search(r"\b" + nm + r"\b", s):
                continue
            if re.search(r"^(?:const uint32_t |static thread_local uint32_t )?(?:input_task_data_ptr|task_data_(?:ptr|size)|g_rs64_m5_last_input_task_data_ptr)\s*=", s) and \
               (re.search(READ, s) or re.search(r"=\s*(0|g_rs64_m5_last_input_task_data_ptr)$", s)):
                continue  # definition from the pointer read / from the log global
            if re.search(r"^(?:std::)?fprintf\(|^rs64_audio_join_image_(stage|source)\(", s):
                continue  # sink: log line / diagnostic join
            if re.search(r"^(?:extern \"\" )?(?:static )?void rs64_audio_join_image_(stage|source)\(", s):
                continue  # the join function's own signature
            flows.append(s[:90])
    gates = {}
    for h in HELPERS:
        hm = re.search(r"static void " + h + r"\((?:uint8_t\* rdram, )?const OSTask\* task\) \{(.*?)\n\}", mn, re.S)
        gates[h] = bool(hm and re.search(r'getenv\("ROGUESQ_LOG_[A-Z0-9_]+"\)', hm.group(1)) and
                        re.search(r"if \(!enabled \|\|[^)]*task[^)]*\) return;", hm.group(1)) and
                        not re.search(r"MEM_[WHBD]\s*\([^)]*\)\s*=|rdram\[[^\]]*\]\s*=(?!=)|task->[\w.]+\s*=(?!=)", hm.group(1)))
    joins_write = []
    for jn in ("rs64_audio_join_image_stage", "rs64_audio_join_image_source"):
        for tt in [mn] + [open(q, errors="replace").read() for q in glob.glob(os.path.join(ROOT, "src/*/*.cpp")) if not q.endswith("main.cpp")]:
            jm2 = re.search(r"(?:extern \"C\" )?(?:static )?void " + jn + r"\([^)]*\)\s*\{(.*?)\n\}", tt, re.S)
            if jm2 and re.search(r"MEM_[WHBD]\s*\([^)]*\)\s*=|rdram\[[^\]]*\]\s*=(?!=)|TO_PTR\(", jm2.group(1)):
                joins_write.append(jn)
    info["H1"] = dict(stores=stores, odd=odd[:4], flows=flows[:4], helpers_gated=gates, joins_write=joins_write)
    if not (stores == ["task"] and not odd and not flows and all(gates.values()) and not joins_write):
        bad.append("H1")
    if detail:
        for k, v in info.items():
            print("  %s %s" % (k, v if k != "B2" else "%d calls %s" % (len(v), sorted(set(x[2] for x in v)))))
    return bad

_decl_files = {}
def files_for(f, n):
    return _decl_files.get((f, n), [])

def classify(decl, store, rows, ov=None):
    rmap = {(f, n): (c, p, w) for f, n, c, p, w in rows}
    used = set(); res = []
    for c in decl:
        if c["auto"]:
            res.append((c, c["auto"], "")); continue
        k = rowkey(c)
        if k not in rmap:
            res.append((c, "OPEN", "no row")); continue
        used.add(k)
        cls, proof, why = rmap[k]
        if not re.search(proof, text(c["file"], ov)):
            res.append((c, "DRIFT", "proof missing: " + proof)); continue
        res.append((c, cls, why))
    for c in store:
        if c["kind"] == "missed":
            res.append((c, "OPEN", "pointer-shaped store target missing from the declaration census"))
        elif rowkey(c) not in rmap:
            res.append((c, "OPEN", "store into an unclassified pointer"))
    stale = [k for k in rmap if k not in used]
    return res, stale

def census_diff(decl, ast):
    A = {(v["file"], v["name"]) for v in ast["vars"]}
    S = {(v["file"], v["name"]) for v in decl}
    a_only = sorted(k for k in A - S if k not in AST_ONLY_OK)
    s_only = sorted(k for k in S - A if k not in REGEX_ONLY_OK)
    return a_only, s_only, len(A), len(S)

def report(res, stale, bad, diff, quiet=False):
    cnt = collections.Counter(r[1] for r in res)
    a_only, s_only, na, ns = diff
    if not quiet:
        print("decl candidates %d (regex) vs %d (clang AST) | classes %s" % (ns, na, dict(sorted(cnt.items()))))
        for c, cls, why in res:
            if cls in ("OPEN", "DRIFT"):
                print("  %s %s:%d %s | %s" % (cls, c["file"], c["line"], c["name"], why))
        for k in stale:
            print("  STALE row", k)
        print("census disagreement: AST-only %s regex-only %s" % (a_only or "none", s_only or "none"))
        print("contracts failing:", bad or "none")
    return cnt["OPEN"] + cnt["DRIFT"] + len(stale) + len(bad) + len(a_only) + len(s_only)

def load(extra=()):
    s = hp.scan(extra)
    _decl_files.clear()
    for c in s["decl"]:
        _decl_files.setdefault(rowkey(c), []).append(c["file"])
    return s

def run_controls(scan, ast):
    ok = 0; total = 0
    def expect(name, cond):
        nonlocal ok, total
        total += 1; ok += bool(cond); print("  control %-66s %s" % (name, "PASS" if cond else "FAIL"))
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "planted_hp.cpp")
        open(p, "w").write(
            "static OSMesgQueue* s_q;\nextern \"C\" void rs64_planted_set(uint8_t* rdram, recomp_context* ctx) {\n"
            "    s_q = TO_PTR(OSMesgQueue, ctx->r4);\n}\nextern \"C\" int rs64_planted_use() { return s_q->validCount; }\n"
            "static OSThread* s_t = TO_PTR(OSThread, 0x80100000);\n"
            "static int s_a, *s_p2;\nthread_local uint32_t s_g = 0; thread_local void* s_h = nullptr;\n")
        s2 = hp.scan([p])
        names = {c["name"] for c in s2["decl"] if c["file"].endswith("planted_hp.cpp")}
        _txt[p] = open(p).read()
        r, _ = classify([c for c in s2["decl"] if c["file"].endswith("planted_hp.cpp")], [], R)
        expect("(1) planted static OSMesgQueue* from TO_PTR used later -> OPEN", any(c["name"] == "s_q" and k == "OPEN" for c, k, _ in r))
        expect("(3) planted `static OSThread* s_t = TO_PTR(...)` initializer -> OPEN", any(c["name"] == "s_t" and k == "OPEN" for c, k, _ in r))
        expect("(9) multi-declarator *s_p2 and thread_local s_h after ';' found", {"s_p2", "s_h"} <= names and "s_a" not in names and "s_g" not in names)
    r, _ = classify(scan["decl"], scan["store"], [x for x in R if x[1] != "g_s4583_t3"])
    expect("(2) drop the g_s4583_t3 row -> OPEN", any(c["name"] == "g_s4583_t3" and k == "OPEN" for c, k, _ in r))
    base = contracts()
    rs = text("lib/N64ModernRuntime/librecomp/src/rsp.cpp")
    expect("(4) remove the g_audio_dma_probe restore -> F1 OPEN", "F1" not in base and "F1" in contracts(
        {"lib/N64ModernRuntime/librecomp/src/rsp.cpp": rs.replace("    g_audio_dma_probe = previous_audio_probe;\n", "", 1)}))
    mn = text("src/main/main.cpp")
    expect("(5) plant a write through s_pending_audio_task -> H1 OPEN", "H1" not in base and "H1" in contracts(
        {"src/main/main.cpp": mn.replace("        s_pending_audio_task = task;\n", "        s_pending_audio_task = task;\n        ((OSTask*)s_pending_audio_task)->t.data_size = 0;\n", 1)}))
    rc = text("lib/N64ModernRuntime/librecomp/src/recomp.cpp")
    k = rc.find("    rdram = (uint8_t*)mmap(")
    expect("(6) plant a second rdram allocation -> B OPEN", "B" not in base and "B" in contracts(
        {"lib/N64ModernRuntime/librecomp/src/recomp.cpp": rc[:k] + "    rdram = (uint8_t*)malloc(64);\n" + rc[k:]}))
    uc = text("src/main/upstream_compat.cpp")
    expect("(7) plant a non-base store into g_s6127_rd -> B1 OPEN", "B1" not in base and "B1" in contracts(
        {"src/main/upstream_compat.cpp": uc.replace("g_s6127_rd = rdram;", "g_s6127_rd = rdram; g_s6127_rd = TO_PTR(uint8_t, 0x80100000);", 1)}))
    dropped = [c for c in scan["decl"] if c["name"] != "g_rs64_window"]
    expect("(8) drop g_rs64_window from the regex census -> disagreement OPEN", census_diff(dropped, ast)[0] == [("src/main/main.cpp", "g_rs64_window")])
    print("controls %d/%d" % (ok, total))
    return ok == total

def main():
    a = sys.argv[1:]
    if "--ast" in a or not os.path.exists(AST_JSON):
        subprocess.run([sys.executable, os.path.join(ROOT, "tools/s7613_hp_ast.py"), "--out", AST_JSON], check=True)
    else:
        ast_cache.ensure(AST_JSON, "tools/s7613_hp_ast.py")  # s7655: regenerate when any source is newer than the cache
    ast = json.load(open(AST_JSON))
    if ast.get("failed"):
        print("AST translation units failed:", ast["failed"])
    scan = load()
    res, stale = classify(scan["decl"], scan["store"], R)
    bad = contracts(detail=True)
    diff = census_diff(scan["decl"], ast)
    n = report(res, stale, bad, diff) + len(ast.get("failed", []))
    rc = 0 if n == 0 else 1
    if "--controls" in a and not run_controls(scan, ast):
        rc = 1
    print("RESULT", "PASS" if rc == 0 else "FAIL")
    sys.exit(rc)

if __name__ == "__main__":
    main()
