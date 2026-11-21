#!/usr/bin/env python3
"""s7612 class RG: host static / thread_local / file-scope state holding a value taken from a guest REGISTER (ctx->rN/fN,
gpr[]/fpr[] handed to hooks, or a parameter of a host function some call site passes a register to) and used on a LATER
call, where it can be stale: the guest freed/reused the object, another caller (camera, thread) entered in between, or a
new stack frame landed at the same sp.

Candidates: tools/s7612_rg_scan.py (s7611 static-store detector, REG + one-hop PARM taint). Every candidate needs a ROW
(file basename or 'RF', static name) -> class + proof regex (scope fn = enclosing function window, file = whole file).
Classes: gated (default-off env/diag), edge (print-on-change key), stash (default-path write, every READER gated: checked
line by line, each reader must sit within 12 lines after the row's gate regex), stat, envflag, value (current scalar the
reader wants latest, no pointer deref), keyed (compared against the live value before use), event (reset on a named edge),
repair (used only when the live guest value already failed validation), fresh (set and consumed inside ONE guest call:
contract proves it).
Contracts (each failing one is OPEN):
 R1 s7103 camfix in applyPlayerVehicleStateUpdate: entry sets s7103_in=1 and NaN-resets h/d/mg; exit is `if (s7103_in)` and
    clears it; no goto/return leaves (entry, exit); f20 store reached from entry with no escape; so calls that skip the entry
    (4 gotos land at/before the exit) see s7103_in == 0. The function runs once per camera object (log: 3+ cams/frame).
 R2 s7108_s2: set and consumed (s7108_x) in applyPlayerVehicleStateUpdate with no escape / skip-in between, s7108_x has ONE
    call site and s7108_s2 no other reader (re-entrancy: another function reading it would be stale).
 R3 s7482 reserve in partitionFramebufferMemory: pend set with b/e, consumed under `if (rs64_s7482_pend)`, cleared there;
    no escape between.
 R4 s7101 chase clamp in updatePlayerVehicleByControlMode: the set is inside `if (f7101)` (ROGUESQ_S7101_CHASE), every
    path to the clamp passes the set (no skip-in), the clamp clears s7101_valid. (One escape leaves valid=1 to the next
    call; harmless because that call re-runs the set before any clamp: witness counts it.)
 R5 s7398_msg (pi.cpp, default on): thread_local; every non-zero assignment is followed by do_dma(...) and `s7398_msg = 0;`
    within 25 lines, no return in between.
 R6 s6892 walker guard (default on): check returns the live v unless it is non-zero AND invalid, and repairs only from a
    record whose s2 equals the live s2.
 R7 s_pending_task_guest_ptr: exactly one reader, inside the [m5-task-handoff] fprintf.
--controls: (1) planted static guest pointer from ctx->r4 dereferenced in a later call -> OPEN; (2) drop a row -> OPEN;
 (3) remove the s7103 exit clear -> R1 OPEN; (4) plant a second reader of s7108_s2 in another function -> R2 OPEN;
 (5) plant a goto escape between the s7482 set and its use -> R3 OPEN; (6) remove `s7398_msg = 0;` after a do_dma -> R5 OPEN;
 (7) corrupt a stash reader gate -> OPEN; (8) planted one-hop PARM taint (hook called with ctx->r5 parks its arg) -> OPEN.
--witness: >=2 of scratch/s7103|s7108|s7110/push_a.txt.zst (ROGUESQ_S7101_CHASE logs, L6 dd4; s7102 pre-fix = negative ctl):
 per applyPlayerVehicleStateUpdate call (segment ending at its 'pe' line): an 'rx' (s7103 exit body) only in segments that
 also carry a 'pu'/'pc' (body after the entry); skip-entry segments must exist; 'cl' (s7101 clamp) only after a 'ch' (set)
 since the previous 'cl'; planted copies (an rx moved into a skip segment; a cl duplicated) must FAIL.
"""
import importlib.util, os, re, subprocess, sys, tempfile, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_sp = importlib.util.spec_from_file_location("rg_scan", os.path.join(ROOT, "tools/s7612_rg_scan.py"))
rg = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(rg)
sn = rg.sn

R = []
def row(f, names, cls, proof, why, scope="fn"):
    for n in names.split():
        R.append((f, n, cls, proof, why, scope))

# ---- s7655: s7644 instrument (default off)
row("s7644_rspdma.cpp", "t_src_ra t_src_tid", "gated", r"rs64_s7646_pi_src\(uint32_t ra, uint32_t thread\) \{\s*if \(!g_gon\) return;",
    "s7655: s7646 PI DMA source (ra, OSThread) stash, set and read only under ROGUESQ_S7644_RSPDMA&2", scope="file")
# ---- src/main/main.cpp
row("main.cpp", "g_rs64_m5_object_entry", "gated", r"ROGUESQ_LOG_M5_OBJECT_ENTRY", "M5 object-entry breadcrumb, if (!enabled) return")
row("main.cpp", "last_a1", "edge", r"if \(\(a1 != last_a1 \|\| c != last_c\) && lines\+\+ < 400\)", "[glyph-entry] print-on-change")
row("main.cpp", "s_pending_task_guest_ptr", "stash", r"std::fprintf\(stderr,|if \(phase_rows\+\+ >= 256u\) return;",
    "audio task pointer: sole reader is the [m5-task-handoff] log (R7)", "file")
# ---- src/main/rt64_render_context.cpp
row("rt64_render_context.cpp", "s_menu_fifo", "event", r"if \(!s_menu_fifo\.empty\(\) && id <= s_menu_fifo\.back\(\)\.second\) s_menu_fifo\.clear\(\);",
    "menu-worker msg ptr (gpr[29]+0x10): cleared on a new worker instance, recv falls back to the live byte unless the front "
    "entry is the same message pointer (s7611 C6)", "file")
# ---- src/main/upstream_compat.cpp
row("upstream_compat.cpp", "s7030_F", "stat", r"s7030_frames\[s7030_ph\]\+\+", "per-phase accumulator, summary print only")
row("upstream_compat.cpp", "s7032_mn s7032_mx", "event", r"s7032_mn\[s\]\[c\] = 1e9f; s7032_mx\[s\]\[c\] = -1e9f;",
    "per-stream-call cell extents, reset every rs64_s7032 frame start", "file")
row("upstream_compat.cpp", "rows", "gated", r"ROGUESQ_LOG_VI_CALLERS", "VI caller census rows (log)")
row("upstream_compat.cpp", "seen", "gated", r"if \(fbw > 0\) \{", "ROGUESQ_FB_WIDTH swap census")
row("upstream_compat.cpp", "s_last_mode", "keyed", r"if \(mode_ptr != s_last_mode\)",
    "compared against the live mode pointer every osViSetMode; only bumps the VI epoch; targets are immutable osViModeTable entries")
row("upstream_compat.cpp", "pcs", "gated", r"rs64_s4222_on\(\)", "s4222 tripwire PCs")
row("upstream_compat.cpp", "g_s4572_t0 g_s4572_t1 g_s4572_cap g_s4572_cnt", "stash", r'getenv\("ROGUESQ_LOG_S457[25]"\)',
    "s4572 record-store watch window: readers return unless ROGUESQ_LOG_S4572 / ROGUESQ_LOG_S4575", "file")
row("upstream_compat.cpp", "s_s5041_freed", "gated", r"s5041_on\(\)", "free census (ROGUESQ_FREE_CENSUS)")
row("upstream_compat.cpp", "s_s7486_recent s_s7486_ctlblk s_s7486_ctlkind", "gated", r"if \(!g_rs64_s7486_on", "s7486 host-read watch, default off")
row("upstream_compat.cpp", "s_s7325_lastmalloc s_s7325_hmin s_s7325_hmax s_s7325_ord s_s7325_freed nb s_s7326_surv", "gated", r"s7317_on\(\)",
    "s7317 alloc map (ROGUESQ_S7317_ALLOCMAP)")
row("upstream_compat.cpp", "s_s6063_live s_s6063_bytes", "gated", r"if \(!s6063_on\(\)(?: \|\| !ptr)?\) return|s7317_on\(\)", "heap log (ROGUESQ_HEAPLOG)")
row("upstream_compat.cpp", "first minlen maxlen last", "gated", r"ROGUESQ_HEADWATCH", "headwatch")
row("upstream_compat.cpp", "s_s6287_on", "envflag", r'getenv\("ROGUESQ_PPLOG"\)', "env word, not a register")
row("upstream_compat.cpp", "s6893_base", "value", r"s6893_base = req / 25u; s6893_cap = s6893_base \* k;",
    "tile pool size recomputed from this call's request")
row("upstream_compat.cpp", "s6893_max", "stat", r"if \(count > s6893_max\)", "high-water mark for the [s6893] print")
row("upstream_compat.cpp", "lw lh", "edge", r"if \(lg && \(w != lw \|\| h != lh\)\)", "[s6911map] print-on-change")
row("upstream_compat.cpp", "g_rs64_m5_state_call_s0 g_rs64_m5_zcfree_edge g_rs64_m5_frequency_pending", "gated",
    r"ROGUESQ_LOG_M5_(STATE_POINTER|FREQUENCY_\w+)|if \(!enabled\) return", "M5 breadcrumbs")
row("upstream_compat.cpp", "ctl_q", "gated", r"ROGUESQ_S7399_CTL", "s7399 control arm")
row("upstream_compat.cpp", "g_s4913_last_tag", "gated", r'getenv\("ROGUESQ_S4913"\)', "s4913 marker")
row("upstream_compat.cpp", "r", "repair", r"if \(!s6892_on\(\)\) return;",
    "s6892 walker guard (default on): mesh keyed by s2, used only when the live *(s2+0x18) is already junk (R6)")
# ---- src/rsp, librecomp, ultramodern
row("dpc_bridge.cpp", "g_rs64_g1d_paused", "value", r"g_rs64_g1d_paused\.store\(v, std::memory_order_relaxed\);",
    "current pause flag, overwritten every mark; readers want the latest value")
row("ai.cpp", "cnt", "gated", r"if \(!on\) return", "s4245 tick census")
row("pi.cpp", "s7398_msg", "fresh", r"s7398_msg = ", "OSIoMesg pointer for this DMA's completion, set -> do_dma -> 0 (R5)", "file")
row("sp.cpp", "sites", "gated", r"ROGUESQ_SPAI_GUARD", "SP address guard sites")
row("events.cpp", "last_sec", "value", r"last_sec = sec;", "wall-clock second of the stats bucket (taint via param, not a register)")
# ---- generated (any funcs_*.c)
row("RF", "pcs", "gated", r"if \(pw_en\) \{", "s6481 poolwatch (ROGUESQ_POOLWATCH)")
row("RF", "seen_pc", "gated", r"if \(!enabled\) return;", "submit-gate store census")
row("RF", "rs64_s7482_b rs64_s7482_e", "fresh", r"rs64_s7482_pend = 1; rs64_s7482_b = base;", "reserve pool set -> consumed -> pend cleared, one call (R3)")
row("RF", "rs64_ef_col rs64_ef_row", "stash", r"if \(lg6315 &&", "s6317 cell stash, read only by [edgefade5] (lg6315)", "file")
row("RF", "s7108_s2", "fresh", r"s7108_s2 = \(uint32_t\)ctx->r18;", "camwide object for this call's s7108_x (R2)")
row("RF", "s7103_f20 s7103_h s7103_d s7103_mg s7103_yc", "fresh", r"/\* PATCH: s7103 camfix \*/", "camfix entry/exit within one call (R1)", "file")
row("RF", "s7101_dist", "gated", r"ROGUESQ_S7101_CHASE", "chase log/clamp; set only if (f7101) (R4)", "file")
row("RF", "ids", "gated", r"ROGUESQ_LOG_HUDBIT", "HUD-bit harness")
row("RF", "key", "gated", r"ROGUESQ_LOG_HITS|ROGUESQ_LOG_S4864", "hit logger / s4864 census")
row("RF", "hio ow objs", "gated", r"ROGUESQ_LOG_HITS|rs5834_en", "hit logger", "file")
row("RF", "lra", "gated", r"if \(!e\) return", "player dump")
row("RF", "rs6660_pending_id rs6666_dat value", "gated", r"rs6657_enabled\(\)|rs6657_level >= 1",
    "objective-response probe (G1 (d) parked): ROGUESQ_OBJECTIVE_RESPONSE", "file")
row("RF", "rs5835_minsdr2 m0 m1 rs5835_min rs5835_minr2 rs5839_obj", "gated", r"ROGUESQ_TELE_BOLT", "TELE bolt probe", "file")
row("RF", "rs64_s4542_prev_base", "gated", r"if \(!rs64_s4542_enabled\(\)\) return;", "s4542 alloc census")
row("RF", "rs64_s4579_asp", "gated", r"if \(!rs64_s4579_on\(\)\) return;", "s4579 alloc probe")
row("RF", "ras last_br ra_key", "gated", r"ROGUESQ_LOG_S4864", "s4864 census")
row("RF", "rs64_s5228_slot tuples rows", "gated", r"if \(!enabled\) return", "s5223/s5228 keyon census")
row("RF", "ctl_mask", "gated", r"if \(!on\) return", "s4533 devaddr census")
row("RF", "rs64_s4537_last_this rs64_s4537_last_phys", "gated", r"if \(!rs64_s4537_enabled\(\)\) return;", "s4537 voice init")
row("RF", "rs64_s4538_last_this", "gated", r"if \(!rs64_s4538_enabled\(\)\) return;", "s4538 voice init")
row("RF", "rs64_s4539_ras", "gated", r"if \(!rs64_s4539_enabled\(\)\) return;", "s4539 entry census")
row("RF", "bufptr_ok", "gated", r"ROGUESQ_LOG_M5_CMDLIST", "M5 cmdlist log")
row("RF", "ds lo", "event", r"if \(st == 2 && ps != 2\) \{", "s6907 hangar aim, reset per scroll start (s7611 C1 + witness)", "file")
row("RF", "s_hs_prev", "edge", r"st != s_hs_prev\)", "[hangar-state] print-on-change")
row("RF", "s_ship_active_prev", "edge", r"ret != s_ship_active_prev\)", "[ship-active] print-on-change")
row("RF", "avf_prev_s0", "edge", r"avf_gate_en", "advanceVideoFrame log")
row("RF", "vi_call_prev_width", "edge", r"vi_call_en && \(vi_call_n < 8 \|\| vi_call_width != vi_call_prev_width\)", "VI caller log", "file")
row("RF", "a5370_g3bad", "stat", r"a5370_p = \(a5370_g3 & \(a5370_g3 - 1u\)\) == 0", "guard counter, power-of-two print")
row("RF", "s_drain_mesh_ring", "stash", r"s_drain_mesh_tail_guard_enabled", "s353 ring, read only by the [drain-mesh-ring] log", "file")
row("RF", "s_dlp_tbl_content", "gated", r"if \(s_dlp_stale_enabled && s_dlp_valid\)", "DL payload stale log")
row("RF", "rs5813_mra", "gated", r"if \(rs5813_en\(\)\) rs5813_msg\(", "s5813 HUD-bit msg census (sole caller gated)", "file")
row("RF", "rs5813_fra", "gated", r"if \(!rs5813_en\(\)\) return;", "s5813")
row("RF", "spmin tab firstrev nmin nmax", "gated", r"if \(!en\) return", "s6555 traversal log")
row("RF", "s7134_cam", "keyed", r'getenv\("ROGUESQ_CULL_XFIX"\)',
    "camera key list, k re-stored on every post; consumers gated by s7134_on (CULL_XFIX default off)", "file")
# s7739: s6500/s6511/s6512 names dropped - not in RS64_REPLAY, absent from the adopted regen tree
row("RF", "s6499_first_addr "
    "s6499_first_val s6499_last_addr s6499_last_val", "stash", r'getenv\("ROGUESQ_FORFACE_LOG"\)',
    "table writer notes, read only by the FORFACE_LOG dumps", "file")
row("RF", "s6496_a0 s6497_first s6497_last", "stash", r'getenv\("ROGUESQ_FORFACE_LOG"\)', "[binin]/[streamdump] inputs", "file")
row("RF", "s7104_a s7104_b s7104_r3 s7104_r4", "gated", r"s7104_cur", "s7104 cell log: s7104_cur = -1 unless ROGUESQ_S7104_CELL", "file")
row("RF", "s7105_lod", "gated", r'getenv\("ROGUESQ_S7105_EMIT"\)', "s7105 emit census")

STASH_GATE_EXTRA = r"getenv\(|_en\b|_enabled|if \(!on\)|lg\d+|if \(on\)"

def rowkey(c):
    return ("RF" if c["file"].startswith("RF/") else os.path.basename(c["file"]), c["name"])

def src_path(rel):
    return os.path.join(sn.GEN, rel[3:]) if rel.startswith("RF/") else os.path.join(ROOT, rel)

_txt = {}
def lines_of(rel, override=None):
    if override and rel in override:
        return override[rel].split("\n")
    if rel not in _txt:
        _txt[rel] = open(src_path(rel), errors="replace").read().split("\n")
    return _txt[rel]

def window(rel, line, scope, override=None):
    L = lines_of(rel, override)
    if scope == "file":
        return "\n".join(L)
    i = line - 1; f0 = i
    while f0 > 0 and i - f0 < 600 and not sn.FUNC_START.match(sn.strip(L[f0])):
        f0 -= 1
    return "\n".join(L[f0:i + 1])

def stash_readers_ok(rel, name, gate, override=None):
    """every reference that is not a declaration or a store must sit within 12 lines after a gate match."""
    L = lines_of(rel, override); bad = []
    g = re.compile(gate)
    for i, l in enumerate(L):
        s = sn.strip(l)
        if not re.search(r"(?<![\w.])" + re.escape(name) + r"\b", s):
            continue
        if sn.SDECL.match(s) or re.match(r"\s*(?:static|extern)\b", s):
            continue
        rest = re.sub(r"(?<![\w.])" + re.escape(name) + r"\b\s*(?:\[[^\]]*\]\s*)*(?:[-+|&^]?=(?!=)|\.store\()", "", s)
        rest = re.sub(r"\bif \(!" + re.escape(name) + r"\b", "", rest)
        if not re.search(r"(?<![\w.])" + re.escape(name) + r"\b", rest):
            continue  # store only
        if re.search(r"^\s*extern \"C\" void rs64_s4572_(publish|setcount)", s):
            continue
        if re.search(r"(?<![\w.])" + re.escape(name) + r"\s*=\s*\(uint32_t\)ctx->r\d+;", s):
            continue  # set from the live register then read on the same line (fresh)
        if not any(g.search(L[j]) for j in range(max(0, i - 12), i + 1)):
            bad.append(i + 1)
    return bad

# ---- path analysis on generated functions
def func_bounds(L, name):
    for i, l in enumerate(L):
        if l.startswith("RECOMP_FUNC") and re.search(r"\b" + re.escape(name) + r"\(", l):
            j = i + 1
            while j < len(L) and not L[j].startswith("RECOMP_FUNC"):
                j += 1
            return i, j
    return None, None

def pair_paths(L, f0, f1, S, U):
    labels = {}
    for i in range(f0, f1):
        m = re.match(r"\s*(\w+)\s*:\s*$", L[i])
        if m:
            labels[m.group(1)] = i
    esc, skip = [], []
    for i in range(f0, f1):
        for m in re.finditer(r"goto\s+(\w+)\s*;", L[i]):
            t = labels.get(m.group(1))
            if S < i < U and (t is None or t > U or t < S):
                esc.append(i + 1)
            if i < S and t is not None and S < t <= U:
                skip.append((i + 1, t + 1))
        if S < i < U and re.search(r"\breturn\b", sn.strip(L[i])):
            esc.append(i + 1)
    return esc, skip

def find(L, f0, f1, pat):
    for i in range(f0, f1):
        if re.search(pat, L[i]):
            return i
    return None

def gen_text(pat, override=None):
    import glob
    if override and "RFKEY:" + pat in override:
        return override["RFKEY:" + pat]
    for p in sorted(glob.glob(os.path.join(sn.GEN, "*.c"))):
        t = open(p, errors="replace").read()
        if re.search(pat, t):
            return t
    return ""

K103 = r"RECOMP_FUNC void applyPlayerVehicleStateUpdate\("
K482 = r"RECOMP_FUNC void partitionFramebufferMemory\("
K101 = r"RECOMP_FUNC void updatePlayerVehicleByControlMode\("

def contracts(override=None, detail=False):
    bad = []; info = {}
    t = gen_text(K103, override); L = t.split("\n")
    f0, f1 = func_bounds(L, "applyPlayerVehicleStateUpdate")
    ok = False
    if f0 is not None:
        S = find(L, f0, f1, r"s7103_in = 1; s7103_yc = -1; s7103_h = s7103_d = s7103_mg = __builtin_nanf")
        U = find(L, f0, f1, r"if \(s7103_in\) \{ int fx = s7103_fix_on\(\); s7103_in = 0;")
        F = find(L, f0, f1, r"s7103_f20 = ctx->f20\.fl;")
        if None not in (S, U, F) and S < F < U:
            esc, skip = pair_paths(L, f0, f1, S, U)
            esc2, _ = pair_paths(L, f0, f1, S, F)
            # readers of s7103 values / helper calls outside the exit block (U-1 .. U+10) other than the entry line
            rd = []
            for i in range(f0, f1):
                s = sn.strip(L[i])
                if U - 1 <= i <= U + 10 or i == S:
                    continue
                x = re.sub(r"\bs7103_(f20|h|d|mg|yc)\s*=(?!=)", "", s)
                if re.search(r"\bs7103_(f20|h|d|mg|yc|p0)\b|\bs7103_mask\(|\bs7115_lift\(", x):
                    rd.append(i + 1)
            clear = "s7103_in = 0;" in L[U]
            ok = not esc and not esc2 and clear and not rd
            info["R1"] = dict(S=S + 1, U=U + 1, F=F + 1, esc=esc, skip_in=skip, outside_readers=rd, clear=clear)
    if not ok: bad.append("R1")
    ok = False
    if f0 is not None:
        S = find(L, f0, f1, r"s7108_s2 = \(uint32_t\)ctx->r18;")
        U = find(L, f0, f1, r"s7108_x\(rdram, ctx->f4\.fl\)")
        if S is not None and U is not None and S < U:
            esc, skip = pair_paths(L, f0, f1, S, U)
            refs = len(re.findall(r"\bs7108_s2\b", t)); calls = len(re.findall(r"\bs7108_x\(rdram", t))
            ok = not esc and not skip and refs == 3 and calls == 1
            info["R2"] = dict(S=S + 1, U=U + 1, esc=esc, skip_in=skip, refs=refs, calls=calls)
    if not ok: bad.append("R2")
    t = gen_text(K482, override); L = t.split("\n"); ok = False
    f0, f1 = func_bounds(L, "partitionFramebufferMemory")
    if f0 is not None:
        S = find(L, f0, f1, r"rs64_s7482_pend = 1; rs64_s7482_b = base; rs64_s7482_e = ec;")
        U = find(L, f0, f1, r"if \(rs64_s7482_pend\) \{")
        C = find(L, f0, f1, r"^\s*rs64_s7482_pend = 0; \}")
        if None not in (S, U, C) and S < U < C:
            esc, skip = pair_paths(L, f0, f1, S, U)
            ok = not esc and len(re.findall(r"rs64_s7482_pend = 1", t)) == 1
            info["R3"] = dict(S=S + 1, U=U + 1, esc=esc, skip_in=skip)
    if not ok: bad.append("R3")
    t = gen_text(K101, override); L = t.split("\n"); ok = False
    f0, f1 = func_bounds(L, "updatePlayerVehicleByControlMode")
    if f0 is not None:
        S = find(L, f0, f1, r"s7101_dist = ctx->f0\.fl; s7101_valid = 1;")
        U = find(L, f0, f1, r"if \(s7101_valid\) \{ int on = s7101_clamp_on\(\);")
        G = find(L, f0, f1, r'getenv\("ROGUESQ_S7101_CHASE"\); f7101 =')
        if None not in (S, U, G) and G < S < U:
            esc, skip = pair_paths(L, f0, f1, S, U)
            gated = any(re.search(r"^\s*if \(f7101\) \{", L[i]) for i in range(G, S))
            ok = not skip and gated and "s7101_valid = 0; } }" in L[U + 4] + L[U + 3] + L[U + 5]
            info["R4"] = dict(S=S + 1, U=U + 1, esc=esc, skip_in=skip, gated=gated)
    if not ok: bad.append("R4")
    pi = "\n".join(lines_of("lib/N64ModernRuntime/librecomp/src/pi.cpp", override)); P = pi.split("\n"); ok = "static thread_local uint32_t s7398_msg = 0;" in pi
    sets = [i for i, l in enumerate(P) if re.search(r"\bs7398_msg = (?!0;)", l)]
    for i in sets:
        seg = P[i:i + 25]; dd = [k for k, l in enumerate(seg) if "do_dma(" in l]; cl = [k for k, l in enumerate(seg) if re.search(r"^\s*s7398_msg = 0;", l)]
        if not (dd and cl and dd[0] < cl[0] and not any(re.search(r"\breturn\b", x) for x in seg[:cl[0]])):
            ok = False
    info["R5"] = dict(sets=len(sets))
    if not ok or not sets: bad.append("R5")
    uc = "\n".join(lines_of("src/main/upstream_compat.cpp", override))
    m = re.search(r'extern "C" uint32_t rs64_s6892_check\(uint8_t\* rdram, uint32_t s2, uint32_t v, uint32_t pc\) \{(.*?)\n\}', uc, re.S)
    if not (m and "if (v == 0 || s6892_valid(v)) return v;" in m.group(1)
            and "for (const S6892Rec& r : s6892_rec) if (r.s2 == s2) good = r.mesh;" in m.group(1)):
        bad.append("R6")
    mn = "\n".join(lines_of("src/main/main.cpp", override))
    rd = re.findall(r"s_pending_task_guest_ptr\.load\(", mn)
    if not (len(rd) == 1 and re.search(r'"\[m5-task-handoff\][^;]*s_pending_task_guest_ptr\.load\(', mn, re.S)):
        bad.append("R7")
    if detail:
        for k, v in info.items():
            print("  %s %s" % (k, v))
    return bad

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
        if cls == "stash":
            b = stash_readers_ok(c["file"], c["name"], proof, override)
            if b:
                res.append((c, "OPEN", "ungated reader at line(s) %s" % b[:4])); continue
        res.append((c, cls, why))
    stale = [k for k in rmap if k not in used]
    return res, stale

def report(res, stale, bad, quiet=False):
    cnt = collections.Counter(r[1] for r in res)
    if not quiet:
        uniq = len({rowkey(c) for c, _, _ in res})
        print("candidates", len(res), "unique", uniq, dict(sorted(cnt.items())))
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
        total += 1; ok += bool(cond); print("  control %-60s %s" % (name, "PASS" if cond else "FAIL"))
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "planted_rg.cpp")
        open(p, "w").write(
            "static uint32_t s_obj;\nextern \"C\" void rs64_planted_set(uint8_t* rdram, recomp_context* ctx) {\n"
            "    s_obj = (uint32_t)ctx->r4;\n}\nextern \"C\" uint32_t rs64_planted_use(uint8_t* rdram) {\n"
            "    return MEM_W(0, (int64_t)(int32_t)s_obj);\n}\n"
            "static uint32_t s_parm;\nextern \"C\" void rs64_planted_hook(uint32_t msg) {\n    s_parm = msg;\n}\n"
            "extern \"C\" void rs64_planted_caller(uint8_t* rdram, recomp_context* ctx) {\n    rs64_planted_hook((uint32_t)ctx->r5);\n}\n")
        hot = rg.hot_functions(list(sn.scope_files()) + [p])
        pc = sn.scan_file(p, "src/main/planted_rg.cpp", rg.REG, hot)
        _txt["src/main/planted_rg.cpp"] = open(p).read().split("\n")
        r, _ = classify(pc, R)
        expect("(1) static guest pointer from ctx->r4 used later -> OPEN", any(c["name"] == "s_obj" and k == "OPEN" for c, k, _ in r))
        expect("(8) one-hop PARM taint (hook(ctx->r5) parks arg) -> OPEN", any(c["name"] == "s_parm" and k == "OPEN" for c, k, _ in r))
    r, _ = classify(cands, [x for x in R if not (x[0] == "pi.cpp" and x[1] == "s7398_msg")])
    expect("(2) drop the pi.cpp s7398_msg row -> OPEN", any(c["name"] == "s7398_msg" and k == "OPEN" for c, k, _ in r))
    base = contracts()
    t = gen_text(K103)
    expect("(3) remove the s7103 exit clear -> R1 OPEN",
           "R1" not in base and "R1" in contracts({"RFKEY:" + K103: t.replace("s7103_in = 0; /* PATCH: s7103 camfix */", "/* PATCH: s7103 camfix */")}))
    t4 = t.replace("RECOMP_FUNC void applyPlayerVehicleStateUpdate(", "static uint32_t planted2(void) { return s7108_s2; }\nRECOMP_FUNC void applyPlayerVehicleStateUpdate(", 1)
    expect("(4) second reader of s7108_s2 in another function -> R2 OPEN", "R2" not in base and "R2" in contracts({"RFKEY:" + K103: t4}))
    t5 = gen_text(K482)
    t5p = t5.replace("rs64_s7482_pend = 1; rs64_s7482_b = base; rs64_s7482_e = ec;", "rs64_s7482_pend = 1; rs64_s7482_b = base; rs64_s7482_e = ec;\n    if (ctx->r4 == 7) return;", 1)
    expect("(5) return between the s7482 set and its use -> R3 OPEN", "R3" not in base and "R3" in contracts({"RFKEY:" + K482: t5p}))
    pi = "\n".join(lines_of("lib/N64ModernRuntime/librecomp/src/pi.cpp"))
    k = pi.rfind("    s7398_msg = 0;\n")
    expect("(6) remove s7398_msg = 0 after a do_dma -> R5 OPEN",
           "R5" not in base and "R5" in contracts({"lib/N64ModernRuntime/librecomp/src/pi.cpp": pi[:k] + pi[k + len("    s7398_msg = 0;\n"):]}))
    R7 = [(f, n, c, (r"ROGUESQ_NOT_A_GATE" if n == "s6496_a0" else p), w, s) for f, n, c, p, w, s in R]
    r, _ = classify(cands, R7)
    expect("(7) corrupt the s6496_a0 stash reader gate -> OPEN/DRIFT", any(c["name"] == "s6496_a0" and k in ("OPEN", "DRIFT") for c, k, _ in r))
    print("controls %d/%d" % (ok, total))
    return ok == total

def seg_eval(L, plant=False):
    """segments = applyPlayerVehicleStateUpdate calls (end at 'pe'). rx = s7103 exit body ran (s7103_in was 1). For each rx
    call: its p0 (entry snapshot of cam+0x10) must equal this call's first pu 'pre' (cam+0x10 before the push), i.e. the exit
    consumed THIS call's entry state, not another camera's. plant = give every rx call the previous rx call's p0."""
    segs, cur = [], []
    for l in L:
        cur.append(l)
        if l.startswith("pe"):
            segs.append(cur); cur = []
    def f(s, k, fld):
        for x in s:
            if x.startswith(k):
                m = re.search(" " + fld + r"=(\S+)", x); return m.group(1) if m else None
    rx = [s for s in segs if f(s, "rx", "p0")]
    noexit = [s for s in segs if not f(s, "rx", "p0")]
    noexit_pu = sum(1 for s in noexit if f(s, "pu", "pre"))
    p0s = [f(s, "rx", "p0") for s in rx]
    if plant:
        p0s = [p0s[0]] + p0s[:-1]
    match = sum(1 for s, p in zip(rx, p0s) if p == f(s, "pu", "pre"))
    cams = sum(1 for a, b in zip(segs, segs[1:]) if f(a[-1:], "pe", "cam") != f(b[-1:], "pe", "cam"))
    armed = False; clt = orphan = 0
    Lc = list(L)
    if plant:
        ic = next(i for i, l in enumerate(Lc) if l.startswith("cl")); Lc.insert(ic + 1, Lc[ic])
    for l in Lc:
        if l.startswith("ch"): armed = True
        elif l.startswith("cl"):
            clt += 1; orphan += not armed; armed = False
    return dict(calls=len(segs), rx=len(rx), noexit=len(noexit), noexit_with_body=noexit_pu, p0_match=match, cam_changes=cams,
                clamps=clt, cl_orphan=orphan)

def run_witness():
    # s7693: scratch/ is gitignored and the s7108 log was lost; any two post-s7103 S7101_CHASE L6 dd4 logs witness the same
    # invariants (s7110 is one). s7102 predates the s7103 exit clear: its rx must be 0, a natural negative control.
    allok = True; ctl = True; have = 0
    neg = os.path.join(ROOT, "scratch/s7102/push_a.txt.zst")
    if os.path.exists(neg):
        L = [l for l in subprocess.run(["zstd", "-dc", neg], capture_output=True, text=True).stdout.split("\n") if l]
        segs = [l for l in L if l.startswith("pe")]; rxn = sum(1 for l in L if l.startswith("rx"))
        nc = len(segs) > 0 and rxn == 0
        print("  witness negative control s7102 (pre-fix): pe %d rx %d -> %s" % (len(segs), rxn, "PASS" if nc else "FAIL"))
        ctl = ctl and nc
    for n in ("scratch/s7103/push_a.txt.zst", "scratch/s7108/push_a.txt.zst", "scratch/s7110/push_a.txt.zst"):
        p = os.path.join(ROOT, n)
        if not os.path.exists(p):
            print("  witness %s missing (skipped)" % n); continue
        have += 1
        L = [l for l in subprocess.run(["zstd", "-dc", p], capture_output=True, text=True).stdout.split("\n") if l]
        r = seg_eval(L); q = seg_eval(L, plant=True)
        ok = (r["rx"] > 0 and r["p0_match"] == r["rx"] and r["noexit"] > 0 and r["noexit_with_body"] == 0
              and r["cam_changes"] > 0 and r["clamps"] > 0 and r["cl_orphan"] == 0)
        cf = q["p0_match"] < q["rx"] and q["cl_orphan"] > 0
        ctl = ctl and cf
        print("  witness %s: %s -> %s | planted stale p0 match %d/%d, cl orphan %d -> control %s"
              % (os.path.basename(os.path.dirname(n)), r, "PASS" if ok else "FAIL", q["p0_match"], q["rx"], q["cl_orphan"], "PASS" if cf else "FAIL"))
        allok = allok and ok
    if have < 2:
        print("  witness: %d post-fix logs present, need 2" % have); allok = False
    print("witness", "PASS" if allok and ctl else "FAIL")
    return allok and ctl

def main():
    a = sys.argv[1:]
    cands, hot = rg.scan()
    res, stale = classify(cands, R)
    bad = contracts(detail=True)
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
