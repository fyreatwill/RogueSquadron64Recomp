#!/usr/bin/env python3
"""s7611 class SN: host-side SNAPSHOTS of guest DATA held in static / thread_local / file-scope state and reused after the
guest may have rewritten the source bytes (level change, overlay data swap, heap reuse, PI DMA, hangar re-entry).

Candidates come from tools/s7611_sn_scan.py (every store of a guest-derived value into static storage, or into a
member/element of a static object, in src/,
librecomp, ultramodern and the generated RecompiledFuncs; 'base' = the rdram host pointer itself, auto-classified).
Every other candidate needs a ROW (file basename or 'RF' for any generated funcs_*.c, static name) -> class + proof regex.
The proof regex must match the raw source between the enclosing function start (cap 600 lines) and the candidate line
(scope 'fn') or anywhere in the file (scope 'file'); otherwise the candidate is DRIFT.
Classes:
  gated     the store runs only under a default-off env gate / diag flag (proof = the gate);
  edge      last-seen value kept only to decide whether a diagnostic line prints (proof = the gated print condition);
  stash     written on a default path, but every reader is a gated diagnostic (proof = the gated reader);
  stat      accumulator / hash that only feeds a log;
  envflag   taint false positive: the stored value is an env/option word, not guest bytes;
  local     scanner false positive: a function-local of the same name;
  refresh   re-read from guest RAM on every call before use (contract proves the re-read sits in the per-call path);
  event     snapshot reset on a guest event (contract + --witness: s6907 hangar aim, reset on each scroll start);
  swap      s4272 deferred-submit shadow: bytes as of submit, swapped in for RT64 and live bytes restored, cleared
            every flush (contract; class GC s7542 + s7532 undo check);
  thread    guest thread identity (class TK, s7608: incarnation token);
  immutable source bytes never rewritten after load.
Contracts (each failing one is OPEN): C1 s6907 aim resets ds/t0/act on the scroll-start edge (st==2 && ps!=2) and tracks
ps on the early-return path; C2 g_s4272_shadow cleared every flush and live bytes captured (wm_live) before the swap;
C3 rs64_s7030_begin re-reads map dims + gCurrentLevel per call and is called per streamTerrainGridCellsByDistance;
C4 rs6663_refresh re-reads the table word and is invoked at each use site (3 calls); C5 the events.cpp draw-distance
originals snapshot (got/igot, once per run) stays behind its env gate and DRAW_DISTANCE never setenv()s those knobs;
C6 s_menu_fifo clears on a non-increasing request id (new worker instance), caps at 64, and recv returns the guest value
unless the front entry is the same message pointer.
--controls: (1) plant a once-read static snapshot of a guest table on a default path -> OPEN; (2) drop a row -> OPEN;
(3) remove the s6907 scroll-start ds reset -> OPEN (C1); (4) plant an address-keyed map of guest bytes, no hash -> OPEN;
(5) remove g_s4272_shadow.clear() -> OPEN (C2); (6) corrupt a row's gate proof -> DRIFT; (7) remove the
s_menu_fifo new-instance clear -> OPEN (C6); (8) plant a member store into a static object -> OPEN. Control (4) found a real scanner blind spot in-session (template commas hid
std::deque/unordered_map statics); the fix surfaced s_menu_fifo.
--witness: scratch/s6995/{r1,d1..d4}.g5g.txt.zst (ROGUESQ_G5G_CAM aim log, s6995 first entry + re-entry after a mission):
every scroll's first row must have output == raw view (ds reset ran; stale ds would differ), mid-scroll rows must diverge
(the comparator can fail), r1 must contain a >60 s gap (mission between entries) with scrolls on both sides, and a planted
copy (each scroll's first output replaced by the previous scroll's START view = what a stale ds would emit) must FAIL.
Exit 0 only if 0 open, 0 drift, 0 stale rows, controls all pass, witness PASS when asked.
"""
import importlib.util, os, re, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_sp = importlib.util.spec_from_file_location("sn_scan", os.path.join(ROOT, "tools/s7611_sn_scan.py"))
scan = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(scan)

R = []
def row(f, names, cls, proof, why, scope="fn"):
    for n in names.split():
        R.append((f, n, cls, proof, why, scope))

# ---- s7655: G6c stand-ins (ROGUESQ_STANDINS=1 and dd>1, else mode()==0 returns before any state) + s7644 instrument
row("rs64_standins.cpp", "s_level s_frame", "refresh", r"const int m = mode\(\);\s*if \(!m\) return;[\s\S]*if \(dat != s_dat \|\| level != s_level \|\| frame < s_frame\) \{ s_level = level; rebuild",
    "s7655: rebuild key (level number, frame counter); a new level or a frame-counter reset rebuilds the stand-in table; opt-in", scope="file")
row("rs64_standins.cpp", "s_linked", "refresh", r"const int m = mode\(\);\s*if \(!m\) return;[\s\S]*s_linked\.clear\(\);",
    "s7655: spawned-object list rebuilt from the guest grid every submit call (clear then refill); opt-in", scope="file")
row("rs64_standins.cpp", "s_cut_prev", "edge", r"if \(\(int\)cut_now != s_cut_prev\) \{[\s\S]*s_cut_prev = \(int\)cut_now;",
    "s7707: cutscene-flag edge detector (-1 initial, then the last 0/1); feeds the [standins-cut] log + dump window only; opt-in STANDINS", scope="file")
row("s7702_fbread.cpp", "s_carry", "gated", r"rs64_s7702_on",
    "s7707: s7702 command-carry across DPC chunks, ROGUESQ_S7702_FBREAD (default off); reset after each use", scope="file")
row("s7644_rspdma.cpp", "last_h", "gated", r"if \(!g_on\) return;", "s7655: s7644 audio image FNV, ROGUESQ_S7644_RSPDMA&1 (default off)")
row("s7644_rspdma.cpp", "t_snap", "gated", r"const bool g_on = \(g_mode & 1\) != 0;[\s\S]*if \(!g_on \|\| g_tasks\.load\(\) == 0\) return;", "s7655: s7644 PI pre/post byte snapshot, ROGUESQ_S7644_RSPDMA&1", scope="file")
row("s7644_rspdma.cpp", "t_g", "gated", r"t_g\.any = false;\s*if \(!g_gon\) return;", "s7655: s7645 gfx PI snapshot, ROGUESQ_S7644_RSPDMA&2", scope="file")
# ---- src/main/main.cpp
row("main.cpp", "g_rs64_m5_last_input_fnv", "gated", r"ROGUESQ_LOG_M5_(INPUT_WRITER|SOURCE_PRODUCER)", "M5 audio source-producer hash, log only")
row("main.cpp", "g_rs64_m5_last_source_dma_fnv g_rs64_m5_last_source_dma_nonzero g_rs64_m5_last_source_dma3_fnv "
    "g_rs64_m5_last_source_dma3_nonzero", "gated", r"ROGUESQ_LOG_M5_(HOST_WRITE|RSP_SOURCE)", "M5 source DMA hash, log only")
row("main.cpp", "s_sh2_buf", "gated", r'getenv\("ROGUESQ_SHADOW2"\)', "ucode shadow2 buffer, ROGUESQ_SHADOW2 default off (s7548)")
row("main.cpp", "prev_a0f50 prev_c1ad0 prev_array_base prev_flags", "edge", r'if \(!std::getenv\("ROGUESQ_LOG_STATE"\)\) return;',
    "state poller thread exits unless ROGUESQ_LOG_STATE")
row("main.cpp", "g_vtx_fault_pages", "gated", r"start_vtx_write_fault_watch", "host page address of rdram (watch armed only by its env)")
row("main.cpp", "g_flz_last_in_hdr", "gated", r"if \(!g_flz_fault_enabled\.load", "fault handler returns unless the FL_ZERO watch is armed")
row("main.cpp", "g_wp_addr", "gated", r'getenv\("ROGUESQ_HWBP_ADDR"\)', "hardware-watchpoint address, env only")
row("main.cpp", "pend s_sum_act s_sum_ctl s_turn s_prev s_tanks s_win s_pg s_pb14 s_prev_fl s_ref", "gated",
    r"ROGUESQ_(LOG_GRIDSPAWN|AIM_TARGETS|LOG_MTM|MISSION_WIN|PLAYER_DUMP|POSE_REF|PLPOS)",
    "get_n64_input soak-harness branches (autopilot aim, mission-win poke, pose lock, player dump): each block opens on its env")
# ---- src/main/rt64_render_context.cpp
row("rt64_render_context.cpp", "s_last_level s_last_craft s_last_cineState s_last_cineStage s_last_cutscene s_last_u20 s_last_u21 "
    "s_last_u22 s_last_width", "edge", r"ROGUESQ_LOG_GAMESTATE", "[gamestate] print-on-change keys")
row("rt64_render_context.cpp", "pend", "gated", r"if \(!rs64_rdp_async_on \|\| !in_task",
    "ROGUESQ_RDP_ASYNC command-byte batch (copy at submit, = what the RDP reads at submit; not in the owner recipe)")
row("rt64_render_context.cpp", "s_menu_fifo", "event", r"if \(!rs64_menu_fifo_on\(\) \|\| \(uint32_t\)gpr\[2\] == 0\) return;",
    "menu-worker completion ids (default on, s6781 fix) keyed by guest message pointer: cleared when a new worker instance "
    "restarts the id counter, capped 64, recv falls back to the live guest byte on any mismatch (C6)")
row("rt64_render_context.cpp", "snap", "gated", r"ROGUESQ_S7539_GB_CHK", "s7539/s7541 whole-RDRAM snapshot for the GB check, seq-tagged")
row("rt64_render_context.cpp", "s_ti_w0 s_ti_w1 s_st_w0 s_st_w1 s_lb_w0 s_lb_w1 s_lb_op g_rs64_g1d_join_ci_w g_rs64_g1d_join_ci_a "
    "g_rs64_g1d_ci_frame s_last_ci s_last_ti s_ti_min s_ti_max s_ti_set s_ti_extra", "gated", r"ROGUESQ_LOG_(G1D_CMD|RDP_WORDS|G1D_TASK)",
    "RDP command logger state (s_cmd_log)")
row("rt64_render_context.cpp", "s_cw s_bin_vi s_g1cf_sc", "gated", r"ROGUESQ_LOG_RDP_SUBMIT", "RDP submit dump (s_log)")
# ---- src/main/s7391_spwm.cpp
row("s7391_spwm.cpp", "t_bot t_top t_snap", "gated", r"ROGUESQ_SP_WATCH", "only the -DROGUESQ_SP_WATCH=ON build calls rs64_spwm_new", "file")
# ---- src/main/upstream_compat.cpp
row("upstream_compat.cpp", "s7033_sc s7033_eb", "refresh", r"const float H = rf\(0x80136DD0u\); s7033_sc =",
    "height scale + eye height re-read from guest every rs64_s7033_frame call (per terrain stream call)")
row("upstream_compat.cpp", "s7056_last", "edge", r'fprintf\(stderr, "\[s7056\] level=', "level print-on-change; k is recomputed from lv every call")
row("upstream_compat.cpp", "s7031_w s7031_hgt", "refresh", r"s7031_w = \(int\)\(uint16_t\)\(MEM_W\(0, \(int64_t\)\(int32_t\)0x80136DF8\)",
    "terrain map dims re-read every rs64_s7030_begin call (C3)")
row("upstream_compat.cpp", "s7030_F", "stat", r"s7030_frames\[s7030_ph\]\+\+", "per-phase forward-distance accumulator, summary print only")
row("upstream_compat.cpp", "snap", "gated", r"ROGUESQ_LOG_S4727_IMG_WATCH", "s4727 image-watch poller (poll_on)")
row("upstream_compat.cpp", "s_redirect s_dump_fb s_fb_hash s_watch", "envflag", r"\(v && \*v && v\[0\] != '0'\) \? 1 : 0;",
    "the value is getenv() text, not guest bytes (v tainted by an earlier local named v)")
row("upstream_compat.cpp", "prev", "gated", r"rs64_s4222_on\(\)", "s4222/s4230 volume-byte tripwires return unless rs64_s4222_on()")
row("upstream_compat.cpp", "g_s4307_last_writer", "gated", r'getenv\("ROGUESQ_LOG_S4299"\)', "s4299 store watch, if (!on) return")
row("upstream_compat.cpp", "s_s6560_tracked", "gated", r"ROGUESQ_HEADWATCH", "headwatch freelist-head tracker")
row("upstream_compat.cpp", "pend", "gated", r"armed\.exchange", "rs64_g1d_fillpc_note: sole caller is behind ROGUESQ_LOG_G1D_FILLPC (default off)")
row("upstream_compat.cpp", "owner xtids", "thread", r"s7394-win", "s7394 heap-mutex window stats: thread ids for the window log (class TK s7608)", "file")
row("upstream_compat.cpp", "g_s4913_last_tid", "gated", r'getenv\("ROGUESQ_S4913"\)', "s4913 marker, if (!on) return")
row("upstream_compat.cpp", "holder", "thread", r"s7394fix::me\(rdram\)", "s7394fix holder: incarnation token, not an OSId (class TK s7608)")
row("upstream_compat.cpp", "n", "local", r"static unsigned nslots\(const uint8_t\* r\) \{ unsigned n =", "local n of nslots()")
# ---- src/rsp/dpc_bridge.cpp
row("dpc_bridge.cpp", "g_f5_hosttgt_pending g_f5_host_order_pending", "gated", r"if \(!rs64_f5_shadow_on\(\)",
    "F5 store-shadow before[] bytes for a diff log, ROGUESQ_LOG_F5_STORE_SHADOW")
row("dpc_bridge.cpp", "g_e9prov", "stat", r"rs64_m4_norm_enabled\(\) \|\| log_e9_provenance\(\)", "ucode-image FNV for the M4 norm / e9prov logs only (s7068)")
row("dpc_bridge.cpp", "g_task_combine", "stat", r"g_task_combine_total\+\+", "combine-mode histogram, printed only", "file")
row("dpc_bridge.cpp", "tw tsiz", "gated", r"if \(!g_rs64_s7486_on", "s7486 host-read UAF watch, default off")
row("dpc_bridge.cpp", "wm_chk cc_pre cc_exp", "gated", r"s_wm_chk|s_coal_chk", "write-merge / coalesce self-checks (ROGUESQ_G1E_RSTAT family)")
row("dpc_bridge.cpp", "uc_post", "gated", r"ROGUESQ_S7532_UNDO_CHK", "s7532 undo check (uc_on)")
row("dpc_bridge.cpp", "wm_live", "swap", r"wm_live\.insert\(wm_live\.end\(\), g_rdram_for_submit \+ r\.first",
    "live bytes saved before the shadow swap-in and restored after RT64 consumed the range (C2)")
row("dpc_bridge.cpp", "s_last_timg", "gated", r"ROGUESQ_LOG_DPC", "DPC logger texture-image key")
row("dpc_bridge.cpp", "s_seq_fillcolor", "gated", r"ROGUESQ_LOG_SEQ", "sequence logger")
row("dpc_bridge.cpp", "s_in_64tri", "edge", r"if \(now_64tri && !s_in_64tri && log_dpc\(\)\)", "edge for the log_dpc() 64-tri print")
row("dpc_bridge.cpp", "g_s4272_shadow g_bc_shadow", "swap", r"g_s4272_shadow\.clear\(\)",
    "s4272 deferred-submit shadow (default on, s4549): bytes as of submit; cleared every flush (C2); g_bc_shadow is its "
    "ROGUESQ_G1E_BATCH cross-check twin", "file")
# ---- src/rsp/s7324_rcp_spill.cpp, librecomp, ultramodern
row("s7324_rcp_spill.cpp", "s_carry", "gated", r"rs64_s7324_on", "s7324 spill watch; sole call site (dpc_bridge.cpp) is if (rs64_s7324_on)", "file")
row("rsp.cpp", "s_nh", "edge", r'getenv\("ROGUESQ_LOG_HUDBIT"\); s_vc_en', "[vsnap] narrow-hash print-on-change, s_vc_en")
row("events.cpp", "orig_r orig_l io", "gated", r"if \(rm == 0\.0 && lm == 0\.0 && im0 == 0\.0 && !dump\) return;",
    "draw-distance retail originals, captured once (C5): ROGUESQ_DD_RADIUS/LOD/IMUL/DUMP, never set by ROGUESQ_DRAW_DISTANCE; "
    "default addresses are main-segment rodata (0x8009ECB0) = immutable")
row("events.cpp", "last", "gated", r'getenv\("ROGUESQ_S7533_FZ_CHK"\)', "s7533 freeze-clamp check (if (chk))")
row("events.cpp", "retail spd dt", "gated", r'getenv\("ROGUESQ_G1E_LIMIT"\)', "G1E limit experiment")
# ---- generated (any funcs_*.c)
row("RF", "rs64_ef_col rs64_ef_row", "stash", r"if \(lg6315 &&", "s6317 cell stash: read only by the [edgefade5] log (lg6315)", "file")
row("RF", "ids n lf", "gated", r'getenv\("ROGUESQ_LOG_HUDBIT"\)', "HUD-bit harness logs")
row("RF", "hio ow rs5834_pt rs5834_dir rs5834_sh key", "gated", r'getenv\("ROGUESQ_LOG_HITS"\)', "hit logger (e[0]=='1')")
row("RF", "rs6663_table", "refresh", r"rs6663_valid = 0;\s*\n\s*rs6663_table = rs6657_word\(rdram, 0x80130BB0u\);", "objective node table re-read per refresh (C4)")
row("RF", "rs6673_address rs6673_request", "gated", r"if \(!rs6673_active|ROGUESQ_OBJECTIVE_RESPONSE_LETHAL",
    "objective-response probe (G1 (d), parked): rs6673_active set only under ROGUESQ_OBJECTIVE_RESPONSE_LETHAL")
row("RF", "rs5839_obj rs5901_c1f rs5835_minsdr2 m0 m1 rs5835_min rs5835_minr2", "gated", r'getenv\("ROGUESQ_TELE_BOLT"\)', "TELE bolt probe (e[0]=='1')")
row("RF", "rs64_s4542_prev_count rs64_s4542_fold_count", "gated", r"if \(!rs64_s4542_enabled\(\)\) return;", "s4542 alloc census")
row("RF", "bufptr_ok", "gated", r"ROGUESQ_LOG_M5_CMDLIST", "M5 cmdlist log")
row("RF", "rs64_s4571_prew", "gated", r"if \(!rs64_s4571_on\(\)\) return;", "s4571 pre-write log")
row("RF", "ps ds lo", "event", r"if \(st == 2 && ps != 2\) \{", "s6907 hangar aim (default on): ds = camera dir at scroll start, reset on "
    "every scroll-start edge of state byte 0x800CC3E4; ps tracks the byte every call (C1, witness)", "file")
row("RF", "avf_prev_byte", "edge", r"if \(avf_gate_en", "advanceVideoFrame swap-gate print-on-change (ROGUESQ_LOG_VI_CALLERS)")
row("RF", "vi_call_prev_width", "edge", r"if \(vi_call_en && \(vi_call_n < 8 \|\| vi_call_width != vi_call_prev_width\)\)",
    "VI caller print-on-change (vi_call_en = ROGUESQ_LOG_VI_CALLERS)", "file")
# s7739: s6501_post_tid row dropped - s6501 is not in RS64_REPLAY, so the adopted regen tree has no such static
row("RF", "s6497_x0 s6497_x1 s6497_z0 s6497_z1", "stash", r'getenv\("ROGUESQ_FORFACE_LOG"\)',
    "s7739: s6497 rasterizer bounds (adopted regen tree), read only by the FORFACE_LOG [streamdump] fprintf", "file")
row("RF", "s6499_post_tbl", "gated", r'if \(getenv\("ROGUESQ_FORFACE_LOG"\)\) \{\s*s6499_post_seq', "s7739: s6499 [raspost] table, written inside if (getenv(FORFACE_LOG))", "file")
row("RF", "s7104_b s7104_r3 s7104_r4", "gated", r"s7104_cur", "s7104 cell visit log: s7104_cur = -1 unless ROGUESQ_S7104_CELL", "file")
row("RF", "s7105_lod", "gated", r'getenv\("ROGUESQ_S7105_EMIT"\)', "s7105 emit census")

def rowkey(c):
    b = os.path.basename(c["file"])
    return ("RF" if c["file"].startswith("RF/") else b, c["name"])

def src_path(rel):
    return os.path.join(scan.GEN, rel[3:]) if rel.startswith("RF/") else os.path.join(ROOT, rel)

_txt = {}
def lines_of(rel, override=None):
    if override and rel in override:
        return override[rel]
    if rel not in _txt:
        _txt[rel] = open(src_path(rel), errors="replace").read().split("\n")
    return _txt[rel]

def window(rel, line, scope, override=None):
    L = lines_of(rel, override)
    if scope == "file":
        return "\n".join(L)
    i = line - 1; f0 = i
    while f0 > 0 and i - f0 < 600 and not scan.FUNC_START.match(scan.strip(L[f0])):
        f0 -= 1
    return "\n".join(L[f0:i + 1])

def contracts(read):
    """read(relpath_or_glob_key) -> text. Returns list of failing contract names."""
    bad = []
    aim = read("AIM")
    if not (re.search(r"if \(st == 2 && ps != 2\) \{[^}]*t0 = now;[^}]*act = 0;[^}]*ds\[i\] = raw\[i\];", aim)
            and re.search(r"if \(rl < 1e-4f\) \{ ps = st; return; \}", aim) and re.search(r"\n\s*ps = st;\n", aim)):
        bad.append("C1")
    dpc = read("src/rsp/dpc_bridge.cpp")
    if not (re.search(r"g_deferred_ranges\.clear\(\); g_s4272_sh\.clear\(\); g_s4272_shadow\.clear\(\);", dpc)
            and re.search(r"wm_live\.insert\(wm_live\.end\(\), g_rdram_for_submit \+ r\.first", dpc)
            and re.search(r"memcpy\(g_rdram_for_submit \+ r\.first, &g_s4272_shadow\[shp->off\]", dpc)):
        bad.append("C2")
    uc = read("src/main/upstream_compat.cpp"); f9 = read("STREAM")
    m = re.search(r'extern "C" void rs64_s7030_begin\(uint8_t \*rdram, uint32_t a0\) \{(.*?)\n\}', uc, re.S)
    if not (m and "0x80136DF8" in m.group(1) and "0x80130B70" in m.group(1) and "rs64_s7033_frame(rdram, a0)" in m.group(1)
            and re.search(r"if \(g_rs64_s7030\) rs64_s7030_begin\(rdram, U32\(ctx->r4\)\);", f9)):
        bad.append("C3")
    obj = read("OBJ")
    if not (len(re.findall(r"rs6663_refresh\(rdram\)", obj)) >= 3 and re.search(r"rs6663_valid = 0;\s*\n\s*rs6663_table = rs6657_word", obj)):
        bad.append("C4")
    ev = read("lib/N64ModernRuntime/ultramodern/src/events.cpp"); mn = read("src/main/main.cpp")
    if not (re.search(r"if \(rm == 0\.0 && lm == 0\.0 && im0 == 0\.0 && !dump\) return;", ev)
            and not re.search(r'setenv\("ROGUESQ_DD_(RADIUS|LOD|IMUL|ADDRS|IADDRS|DUMP)"', mn + uc + ev)):
        bad.append("C5")
    rt = read("src/main/rt64_render_context.cpp")
    if not (re.search(r"if \(!s_menu_fifo\.empty\(\) && id <= s_menu_fifo\.back\(\)\.second\) s_menu_fifo\.clear\(\);", rt)
            and re.search(r"if \(s_menu_fifo\.size\(\) >= 64\) s_menu_fifo\.pop_front\(\);", rt)
            and re.search(r"if \(s_menu_fifo\.empty\(\) \|\| s_menu_fifo\.front\(\)\.first != msg\) return v0;", rt)):
        bad.append("C6")
    return bad

def gen_file_with(pat):
    import glob
    for p in sorted(glob.glob(os.path.join(scan.GEN, "*.c"))):
        t = open(p, errors="replace").read()
        if re.search(pat, t):
            return "RF/" + os.path.basename(p), t
    return None, ""

def default_reader(override=None):
    keys = {"AIM": r"static void rs64_s6907_aim\(", "STREAM": r"RECOMP_FUNC void streamTerrainGridCellsByDistance\(",
            "OBJ": r"static int rs6663_refresh\("}
    cache = {}
    def read(k):
        if override and k in override:
            return override[k]
        if k in cache:
            return cache[k]
        if k in keys:
            _, t = gen_file_with(keys[k])
        else:
            t = open(os.path.join(ROOT, k), errors="replace").read()
        cache[k] = t
        return t
    return read

def classify(cands, rows, override=None):
    rmap = {(f, n): (c, p, w, s) for f, n, c, p, w, s in rows}
    used = set(); res = []
    for c in cands:
        if c["auto"]:
            res.append((c, c["auto"], "")); continue
        k = rowkey(c)
        if k not in rmap:
            res.append((c, "OPEN", "no row")); continue
        used.add(k)
        cls, proof, why, scope = rmap[k]
        if not re.search(proof, window(c["file"], c["line"], scope, override)):
            res.append((c, "DRIFT", "proof missing: " + proof)); continue
        res.append((c, cls, why))
    stale = [k for k in rmap if k not in used]
    return res, stale

def report(res, stale, bad, quiet=False):
    import collections
    cnt = collections.Counter(r[1] for r in res)
    if not quiet:
        print("candidates", len(res), dict(sorted(cnt.items())))
        for c, cls, why in res:
            if cls in ("OPEN", "DRIFT"):
                print("  %s %s:%d %s | %s" % (cls, c["file"], c["line"], c["name"], why))
        for k in stale:
            print("  STALE row", k)
        print("contracts failing:", bad or "none")
    return cnt["OPEN"] + cnt["DRIFT"] + len(stale) + len(bad)

def run_controls(cands):
    ok = 0; total = 0
    def expect(name, cond):
        nonlocal ok, total
        total += 1; ok += bool(cond); print("  control %-58s %s" % (name, "PASS" if cond else "FAIL"))
    # (1) planted once-read snapshot on a default path
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "planted_sn.cpp")
        open(p, "w").write("static uint32_t s_tbl;\nstatic bool s_done;\nextern \"C\" void rs64_planted(uint8_t* rdram) {\n"
                           "    if (!s_done) { s_tbl = MEM_W(0, (int64_t)(int32_t)0x80130BB0u); s_done = true; }\n}\n"
                           "static std::unordered_map<uint32_t, uint32_t> s_cache;\nextern \"C\" uint32_t rs64_planted2(uint8_t* rdram, uint32_t a) {\n"
                           "    uint32_t v = MEM_W(0, (int64_t)(int32_t)a);\n    s_cache[a] = v;\n    return s_cache[a];\n}\n"
                           "struct Lvl { uint32_t dims; };\nstatic Lvl s_lvl;\nextern \"C\" void rs64_planted3(uint8_t* rdram) {\n"
                           "    s_lvl.dims = MEM_W(0, (int64_t)(int32_t)0x80136DF8u);\n}\n")
        pc = scan.scan_file(p, "src/main/planted_sn.cpp")
        _txt["src/main/planted_sn.cpp"] = open(p).read().split("\n")
        r, _ = classify(pc, R)
        expect("(1) once-read static snapshot s_tbl -> OPEN", any(c["name"] == "s_tbl" and k == "OPEN" for c, k, _ in r))
        expect("(4) address-keyed map of guest bytes s_cache -> OPEN", any(c["name"] == "s_cache" and k == "OPEN" for c, k, _ in r))
        expect("(8) member store into a static object s_lvl.dims -> OPEN", any(c["name"] == "s_lvl" and k == "OPEN" for c, k, _ in r))
    # (2) drop a row
    r, _ = classify(cands, [x for x in R if not (x[0] == "RF" and x[1] == "ds")])
    expect("(2) drop the s6907 ds row -> OPEN", any(c["name"] == "ds" and k == "OPEN" for c, k, _ in r))
    # (3) remove the scroll-start ds reset
    rd = default_reader(); aim = rd("AIM")
    rd3 = default_reader({"AIM": aim.replace("for (i = 0; i < 3; i++) ds[i] = raw[i]; }", "}")})
    expect("(3) remove s6907 scroll-start ds reset -> C1 OPEN", "C1" in contracts(rd3) and "C1" not in contracts(rd))
    # (5) remove the shadow clear
    dpc = rd("src/rsp/dpc_bridge.cpp")
    rd5 = default_reader({"src/rsp/dpc_bridge.cpp": dpc.replace("g_s4272_shadow.clear();", "")})
    expect("(5) remove g_s4272_shadow.clear() -> C2 OPEN", "C2" in contracts(rd5))
    # (6) corrupt a gate proof
    R6 = [(f, n, c, (p + "_CORRUPT") if (f == "events.cpp" and n == "orig_r") else p, w, s) for f, n, c, p, w, s in R]
    r, _ = classify(cands, R6)
    expect("(6) corrupt events.cpp orig_r gate proof -> DRIFT", any(c["name"] == "orig_r" and k == "DRIFT" for c, k, _ in r))
    rt = rd("src/main/rt64_render_context.cpp")
    rd7 = default_reader({"src/main/rt64_render_context.cpp": rt.replace("s_menu_fifo.clear();", ";")})
    expect("(7) remove the s_menu_fifo new-instance clear -> C6 OPEN", "C6" in contracts(rd7))
    print("controls %d/%d" % (ok, total))
    return ok == total

def aim_rows(path):
    out = subprocess.run(["zstd", "-dc", path], capture_output=True, text=True).stdout
    rows = []
    for l in out.split("\n"):
        f = l.split()
        if len(f) >= 17:
            try: rows.append([float(x) for x in f[:17]])
            except ValueError: pass
    return rows

def witness_eval(rows):
    """per scroll: first row output o (cols 13-15) == raw (cols 10-12); mid rows diverge somewhere."""
    starts = eq = mid = 0; prev = None; times = []
    for r in rows:
        d = sum((r[10 + k] - r[13 + k]) ** 2 for k in range(3))
        if prev is None or r[1] != prev:
            starts += 1; eq += d < 1e-6; times.append(r[0]); prev = r[1]
        elif d > 1e-4:
            mid += 1
    gaps = [b - a for a, b in zip(times, times[1:])]
    return starts, eq, mid, gaps

def run_witness():
    wd = os.path.join(ROOT, "scratch/s6995")
    allok = True; ctl = True
    for n in ("r1", "d1", "d2", "d3", "d4"):
        p = os.path.join(wd, n + ".g5g.txt.zst")
        if not os.path.exists(p):
            print("  witness %s missing" % n); allok = False; continue
        rows = aim_rows(p)
        s, e, m, gaps = witness_eval(rows)
        ok = s > 0 and e == s and m > 0
        if n == "r1":
            big = [i for i, g in enumerate(gaps) if g > 60]
            ok = ok and bool(big) and big[0] >= 1 and big[0] < len(gaps)
            print("  witness r1 re-entry gap(s) >60 s at scroll index", [b + 1 for b in big])
        # planted control: a stale ds = the PREVIOUS scroll's start view; at s=0 the output would equal it, not raw
        pl = [list(r) for r in rows]; first = None; prev = None
        for i, r in enumerate(pl):
            if r[1] != prev:
                if first is not None:
                    r[13:16] = first
                first = rows[i][10:13]
            prev = r[1]
        ps, pe, _, _ = witness_eval(pl)
        cfail = pe < ps
        ctl = ctl and cfail
        print("  witness %s scrolls=%d start_eq=%d mid_diverge=%d -> %s | planted stale-ds start_eq=%d/%d -> control %s"
              % (n, s, e, m, "PASS" if ok else "FAIL", pe, ps, "PASS" if cfail else "FAIL"))
        allok = allok and ok
    print("witness", "PASS" if allok and ctl else "FAIL")
    return allok and ctl

def main():
    a = sys.argv[1:]
    cands = scan.scan()
    res, stale = classify(cands, R)
    bad = contracts(default_reader())
    n = report(res, stale, bad)
    rc = 0 if n == 0 else 1
    if "--controls" in a and not run_controls(cands):
        rc = 1
    if "--witness" in a and not run_witness():
        rc = 1
    print("RESULT", "PASS" if rc == 0 else "FAIL")
    sys.exit(rc)

if __name__ == "__main__":
    main()
