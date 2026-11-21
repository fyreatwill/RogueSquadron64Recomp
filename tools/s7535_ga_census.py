#!/usr/bin/env python3
"""s7535 class GA census: host code that READS a guest RDRAM byte/word and takes a DECISION on it (branch, size, skip,
index, loop bound) - the read side of classes FY (host copies of guest bytes, s7532) and FZ (host writes, s7533).
A decision read races the guest when it runs on a thread other than the guest CPU thread while the guest may store the
same bytes in the window (torn / stale decision).  lib/rt64 hle/gbi/render readers are the RDP-input domain of FX/FY and
are excluded (they consume the DPC ring the guest never stores into).

Read idioms (comments stripped; string literals blanked), source names guest memory or a local alias of it:
  guest[..] / alias[..] not followed by an assignment       MEM_W/H/B/D(..) not followed by an assignment
  *(T*)(guest + ..) / *reinterpret_cast<T*>(guest..) rvalue  __atomic_load_n(guest..)
A read is a DECISION read when its statement is a condition (if/while/for/switch/?:/&&/||/comparison), or the value
feeds an index / size / loop bound (assigned to a local that is later used in such a position is NOT tracked: the
census rules every read site by function, decision or not, so no data-flow is needed for the gate).  Reads inside a
log statement only (printf/fprintf/...) are auto-ruled "log-only" (a printed value takes no decision).

Per site the enclosing function (fz.func_spans) is looked up in RULES (file suffix, function, line regex|None) ->
class, thread, reason, checks (s7530 run_checks: verify / envoff / nocaller).
Classes: H-guest-thread (runs on the guest CPU thread: syscall replacement / recompiled-func splice / guest-called helper)
         H-pre-guest (before the guest thread starts)
         H-canon (non-guest thread, but the bytes are guest-quiescent in the window: the guest is blocked on the completion
                  the read precedes, or the read IS device semantics, e.g. RSP DMA / task header fetch before sp_complete)
         H-dead (value written once at init / never rewritten while the read can run)
         H-instrument-only (env-gated diagnostic, default off; or the read only selects what to log)
         H-latent-fix (non-guest thread, guest running, a torn/stale decision possible) -> must be fixed/instrumented
         H-latent-FIXED(opt-in) (an H-latent-fix whose fix exists behind an owner opt-in; default unchanged by owner rule)
         UNCLASSIFIED -> FAIL

  python3 tools/s7535_ga_census.py              # every row + summary, exit 1 on any FAIL
  python3 tools/s7535_ga_census.py --fn         # per-function table (rule authoring)
  python3 tools/s7535_ga_census.py --controls   # planted fixtures, mutation control, coverage control
"""
import bisect, os, re, sys, tempfile
from collections import Counter, defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import s7530_fw_census as fw
import s7533_fz_census as fz

ROOTS = ["lib/N64ModernRuntime/librecomp/src", "lib/N64ModernRuntime/librecomp/include",
         "lib/N64ModernRuntime/ultramodern/src", "src/main", "src/rsp"]
G = fz.G
IDX = re.compile(r'([A-Za-z_][\w.\->]*)\s*\[')
MEMM = re.compile(r'\bMEM_([WHBD])U?\s*\(')
CAST = re.compile(r'\*\s*(?:reinterpret_cast<[^>]*\*\s*>|\(\s*(?:const\s+)?(?:volatile\s+)?[\w:]+\s*(?:const\s*)?\*\s*\))\s*\(\s*')
ATOM = re.compile(r'\b__atomic_load_n\s*\(')
ASSIGN = re.compile(r'\s*(?:[+\-|&^*/]?=)(?!=)|\s*(?:\+\+|--)')
LOG = re.compile(r'\b(?:f?printf|snprintf|fputs|fputc|puts|fwrite|fflush|rs64_log\w*|LOG\w*)\s*\(|std::cerr|std::cout')
DECIDE = re.compile(r'\b(?:if|while|for|switch)\s*\(|\?|&&|\|\||[<>]=?|[!=]=|\breturn\b|\bbreak\b|\bcontinue\b')


def blank_strings(t):
    return re.sub(r'"(?:\\.|[^"\\\n])*"|\'(?:\\.|[^\'\\\n])\'', lambda m: '"' + ' ' * (len(m.group(0)) - 2) + '"', t)


def close_of(t, i, o="[", c="]"):
    d = 0
    for j in range(i, len(t)):
        if t[j] == o:
            d += 1
        elif t[j] == c:
            d -= 1
            if d == 0:
                return j
    return len(t) - 1


def sites(path):
    try:
        raw = open(path, errors="replace").read()
    except OSError:
        return None
    t = blank_strings(fw.strip_comments(raw))
    starts = [0]
    for ln in t.split("\n")[:-1]:
        starts.append(starts[-1] + len(ln) + 1)
    lno = lambda pos: bisect.bisect_right(starts, pos)
    spans = fz.func_spans(t)
    opens = [s[0] for s in spans]

    def enclosing(pos):
        k = bisect.bisect_right(opens, pos) - 1
        while k >= 0:
            if spans[k][0] <= pos <= spans[k][1]:
                return spans[k]
            k -= 1
        return (0, len(t), "<file>")

    alias_cache = {}

    def aliases(span):
        if span not in alias_cache:
            body = t[span[0]:span[1]]
            alias_cache[span] = {m.group(1) for m in fz.ALIAS.finditer(body) if m.group(1) not in ("rdram", "RDRAM")}
        return alias_cache[span]

    def is_guest(expr, pos):
        e = re.sub(r'^\s*(?:\(\s*[\w:\s\*]+\)\s*|reinterpret_cast<[^>]*>\s*\(|static_cast<[^>]*>\s*\()+', '',
                   expr.strip()).lstrip("&*( ")
        if re.match(r'(?:[\w]+(?:\.|->))*' + G + r'\b', e) or re.match(r'TO_PTR\s*\(', e):
            return True
        b = re.match(r'([A-Za-z_]\w*)', e)
        return bool(b) and b.group(1) in aliases(enclosing(pos))

    def stmt(pos):
        a = max(t.rfind(';', 0, pos), t.rfind('{', 0, pos), t.rfind('}', 0, pos)) + 1
        b = min(x for x in (t.find(';', pos), t.find('{', pos), len(t)) if x >= 0)
        return t[a:b]

    out = []

    def add(pos, end, kind, src):
        if ASSIGN.match(t, end + 1):
            return                      # a store (class FZ), not a read
        s = stmt(pos)
        if re.match(r'\s*&', t[max(0, pos - 2):pos][::-1]) or t[max(0, pos - 1):pos] == "&":
            return                      # address-of: no load here
        mode = "log" if LOG.search(s) else ("decide" if DECIDE.search(s) else "value")
        out.append((lno(pos), kind, src[:40], enclosing(pos)[2], mode))

    for m in IDX.finditer(t):
        base = m.group(1)
        if not (re.search(r'(?:^|\.|->)' + G + r'$', base) or is_guest(base, m.start())):
            continue
        end = close_of(t, m.end() - 1)
        add(m.start(), end, "index", base + "[..]")
    for m in MEMM.finditer(t):
        end = close_of(t, m.end() - 1, "(", ")")
        add(m.start(), end, "MEM", "MEM_" + m.group(1))
    for m in CAST.finditer(t):
        end = close_of(t, m.end() - 1, "(", ")")
        inner = t[m.end():end]
        if is_guest(inner, m.start()):
            add(m.start(), end, "cast", "*(" + inner.strip()[:30] + ")")
    for m in ATOM.finditer(t):
        args, end = fz.split_args(t, m.end())
        if args and is_guest(args[0], m.start()):
            add(m.start(), end, "atomic", args[0].strip()[:30])
    return sorted(set(out)), raw


# ---- rules -------------------------------------------------------------------------------------------------------------
GT, PRE, GFX, TASK, POLL, INP, PRES = "guest", "pre-guest", "gfx", "task", "poller", "input", "present"
L, LI, O = "librecomp/src/", "librecomp/include/", "overlays.cpp"
UC, MN, RC, B = "src/main/upstream_compat.cpp", "src/main/main.cpp", "src/main/rt64_render_context.cpp", "src/rsp/dpc_bridge.cpp"
EV = "ultramodern/src/events.cpp"
RSPI = "librecomp/rsp.hpp"
RING = ("reads RDP command bytes in the RSP-output ring [submit_lo, submit_hi) on the Gfx thread: the guest CPU never stores "
        "into the ring (RSP DMA output only; s7532 0 foreign bytes in 3.1 GB, s7489 host_wF=0), so the bytes are guest-quiescent")
DIAG = "env-gated diagnostic, default off; the read only selects what to log / count"
GUESTCB = "guest-thread callback (osRecvMesg / osSendMesg / recompiled-code hook), ordered with the guest's own stores"


def D(f, fn, env, lines=None, why=DIAG, thr="any"):
    """diagnostic rule: env (a ROGUESQ_* name) must appear in the file and be absent from the owner/loop config"""
    return (f, fn, lines, "H-instrument-only", thr, why + " (" + env + ")", {"verify": re.escape(env), "envoff": env})


def F(f, fn, flag, lines=None, why=DIAG, thr="any"):
    """diagnostic rule keyed on a runtime flag variable that only an env var sets (verify the flag exists)"""
    return (f, fn, lines, "H-instrument-only", thr, why + " [flag " + flag + "]", {"verify": r"\b" + re.escape(flag) + r"\b"})



def A(anchor, dlo, dhi):
    """s7651: a line range keyed to a text anchor, not to absolute line numbers (22 absolute ranges drifted by +4..+842 lines
    as files grew, s7651). The range is [anchor_line + dlo, anchor_line + dhi]; the anchor must occur exactly once in the
    file, else the rule reports FAIL-check (drift is loud, never a silent re-scope)."""
    return ("@", anchor, dlo, dhi)


_ANCH = {}


def resolve(path, raw, g):
    k = (path, hash(raw), g)
    if k not in _ANCH:
        hit = [i + 1 for i, l in enumerate(raw.split("\n")) if g[1] in l]
        _ANCH[k] = (hit[0] + g[2], hit[0] + g[3]) if len(hit) == 1 else ("anchor %r found %d times" % (g[1][:40], len(hit)))
    return _ANCH[k]

RULES = [
    # --- s7651 drift: functions added after s7535 closed, each gate read by hand ---
    D(RC, "job_end", "ROGUESQ_S7539_GB_CHK", why="s7539 GB snapshot diff, called only under gb::on", thr=GFX),
    D(RC, "rs64_s7541_span", "ROGUESQ_S7539_GB_CHK", why="s7541 span check, returns unless gb::on", thr=GFX),
    D(UC, "s7545_rdw", "ROGUESQ_S7545_THRWATCH", why="s7545 GE thread-watch value read, watch path under s7545_on()"),
    D("src/rsp/s7644_rspdma.cpp", "rb", "ROGUESQ_S7644_RSPDMA", why="s7644 TS-3 audio-task vs PI DMA instrument (g_mode)"),
    D("src/rsp/s7751_task_snap.cpp", "rs64_s7751_rdp", "ROGUESQ_S7751_SNAP", why="s7751 raw RDP byte capture for the cxd4 replay, returns on !dir()", thr=GFX),
    # --- the gfx/audio RSP DMA read: device semantics; gfx window measured by s7535 ROGUESQ_S7535_GA_CHK -----------------------
    (RSPI, "dma_rdram_to_dmem", A('dram_addr + rd_len <= g_rsp_dma_shadow2_addr + g_rsp_dma_shadow2_size)', 0, 20), "H-latent-FIXED(opt-in)", "task/gfx",
     "FIXED(opt-in) s7537: ROGUESQ_SP_LATE=1 (hardware-order sp_complete) is free at FPS60 wherever the game holds 60/s "
     "(s7537 L1/L4/L12 dd1/dd4: 60.0 vs 60.0) and within noise when CPU-bound (L12 dd4 on battery, 3v3 ABBA early 52.9-54.6 vs "
     "late 51.4-52.9); listed in docs/OWNER-OPT-INS.md, default early until the owner chooses. Was OPEN s7535: RSP SP_RD DMA. Audio tasks run before their sp_complete (canon). Gfx tasks get sp_complete EARLY (events.cpp, "
     "before send_dl), and the guest builds the next frame into the gfx pool 0x720000-0x75FFFF that the in-flight F5 LLE is still "
     "fetching: ROGUESQ_S7535_GA_CHK + LATE=alt same-run A/B, L4 flight diff bytes in that pool early 1.19 MB vs late 6.7 kB "
     "(0x100 vertex loads, shade bytes +-1). Fix candidate = hardware-order sp_complete (ROGUESQ_S7535_LATE=1); needs FPS60 "
     "frame-rate + spike/drop qualification before it can be default",
     {"verify": r"ROGUESQ_S7535_GA_CHK"}),
    D(RSPI, "dma_rdram_to_dmem", "ROGUESQ_DUMP_IMEM_DMA", A('const char* e = getenv("ROGUESQ_DUMP_IMEM_DMA");', -2, 77)),
    # --- librecomp -------------------------------------------------------------------------------------------------------------
    (L + "mods.cpp", "init_mod_code", None, "H-pre-guest", PRE, "mod relocation at load_mods (startup)", {}),
    (L + O, "s7_ramw", None, "H-instrument-only", "any", "s7520 code-word watch helper (ROGUESQ_S7520_*), compare/log only",
     {"verify": r"ROGUESQ_S7520", "envoff": "ROGUESQ_S7520_CTL"}),
    D(L + "pi.cpp", "do_rom_read", "ROGUESQ_LOG_S4298"),
    (L + "rsp.cpp", "audio_hash_rdram", None, "H-canon", TASK, "audio task header/hash read inside run_task before sp_complete "
     "(guest waits on the task) and only for logs", {}),
    (L + "rsp.cpp", "audio_read_rdram_word", None, "H-canon", TASK, "audio task word read inside run_task before sp_complete", {}),
    (L + "rsp.cpp", "rs64_s4209_read", None, "H-instrument-only", TASK, "s4209 audio read census", {"verify": r"rs64_s4209"}),
    (L + "rsp.cpp", "rs64_s4211_task", None, "H-instrument-only", TASK, "s4211 audio task census", {"verify": r"rs64_s4211"}),
    (L + "rsp.cpp", "rs64_s4214_scan", None, "H-instrument-only", TASK, "s4214 record scan", {"verify": r"rs64_s4214"}),
    D(L + "rsp.cpp", "rs64_s4215_dump", "ROGUESQ_LOG_S4213", thr=TASK),
    (L + "rsp.cpp", "rs64_probe_audio_dma_write", None, "H-instrument-only", TASK, "audio DMA write probe (log)", {}),
    (L + "rsp.cpp", "run_task", None, "H-instrument-only", TASK,
     "s5657 voice-census / s_vc_en / s_vf counters in run_task (env-gated), all before sp_complete", {"verify": r"s_vc_en"}),
    # --- ultramodern events.cpp: Gfx-thread VI levers --------------------------------------------------------------------------
    (EV, "apply", r"\blb\b", "H-latent-FIXED", GFX, "s7533 FPS60 clamp byte CAS (class FZ); the read is the CAS's own load",
     {"verify": r"__atomic_compare_exchange_n\(lb, &expect"}),
    (EV, "apply", A('// s6018 G1c draw-distance levers (default OFF = retail). ROGUESQ_DD_R', -1, 54), "H-instrument-only", GFX, "s6018 G1c DD_RADIUS/LOD/IMUL/DUMP levers: early return unless set",
     {"verify": r"if \(rm == 0\.0 && lm == 0\.0 && im0 == 0\.0 && !dump\) return;", "envoff": "ROGUESQ_DD_RADIUS"}),
    D(EV, "apply", "ROGUESQ_G1E_LIMIT", A('static const char* le = std::getenv("ROGUESQ_G1E_LIMIT"); static const', -11, 44), thr=GFX),
    D(EV, "apply", "ROGUESQ_G3C_LOG", A('static const bool on = [] { const char* e = std::getenv("ROGUESQ_G3C_L', -8, 16), thr=GFX),
    # --- src/main main.cpp -----------------------------------------------------------------------------------------------------
    (MN, "rs64_m5_audio_input_dma", None, "H-instrument-only", TASK, "M5 audio DMA census (s_pending_audio_generation, log)", {}),
    D(MN, "rs64_m5_exact_route_dma_write", "ROGUESQ_LOG_M5_EXACT_ROUTE", thr=TASK),
    D(MN, "s4578_poll", "ROGUESQ_LOG_S4578", thr=POLL),
    D(MN, "rs64_s6843_note", "ROGUESQ_STORE_WATCH_LINES"),
    D(MN, "rs64_m5_host_write_census", "ROGUESQ_LOG_M5_HOST_WRITE"),
    D(MN, "rs64_m5_audio_source_dma", "ROGUESQ_LOG_M5_RSP_SOURCE", thr=TASK),
    D(MN, "rs64_m5_source_range_dma_write", "ROGUESQ_LOG_M5_SOURCE_WRITER", thr=TASK),
    (MN, "rs64_audio_hash_rdram", None, "H-instrument-only", "rsp", "audio image stage hash (log)", {}),
    (MN, "<file>", None, "not-guest", "-", "struct field declaration (alias false positive)", {}),
    D(MN, "rs64_audio_source_objects", "ROGUESQ_LOG_AUDIO_OBJECTS"),
    (MN, "rdram_be32", None, "H-harness-lever", POLL, "BE word helper for the start_*_poller harness threads (see their rules)", {}),
    (MN, "start_level_poller", None, "H-harness-lever", POLL, "ROGUESQ_FORCE_SEL / FORCE_MISSION route poller (soak routing only)",
     {"envoff": "ROGUESQ_FORCE_SEL"}),
    D(MN, "start_state_poller", "ROGUESQ_LOG_STATE", thr=POLL),
    D(MN, "start_m5_exact_route_poller", "ROGUESQ_LOG_M5_EXACT_ROUTE", thr=POLL),
    D(MN, "start_b50_poller", "ROGUESQ_LOG_B50", thr=POLL),
    D(MN, "start_phase_poller", "ROGUESQ_LOG_PHASE", thr=POLL),
    D(MN, "start_m5_voice_slot_poller", "ROGUESQ_LOG_M5_VOICE_SLOTS", thr=POLL),
    D(MN, "start_fs_slot_poller", "ROGUESQ_FS_SLOT_ADDR", thr=POLL),
    D(MN, "start_fl_zero_poller", "ROGUESQ_FL_ZERO_ADDR", thr=POLL),
    D(MN, "s7504_fb", "ROGUESQ_S7504_FB"),
    D(MN, "get_n64_input", "ROGUESQ_MISSION_WIN", A('// s5604: ROGUESQ_MISSION_WIN=<n> is a TEST-ONLY lever for the mission', -1, 74), why="harness mission-window poke (soak routing)", thr=INP),
    D(MN, "get_n64_input", "ROGUESQ_S7671_FX_ON_KEY", A('// s7671 TEST-ONLY lever: ROGUESQ_S7671_FX_ON_KEY=1', 0, 42), why="s7671 rumble effect-slot lever (test only)", thr=INP),
    D(MN, "get_n64_input", "ROGUESQ_LOG_FL", A('// s6399: ROGUESQ_POSE_LOCK=1 is a TEST-ONLY no-input hover arm for G3', -13, 1), thr=INP),
    ("src/main/rs64_rdram_peek.h", "rs64_rdram_u8", None, "H-instrument-only", "any",
     "diagnostic peek helper ('Host-side diagnostic reads', header comment); callers are census/probe code", {"verify": r"Host-side diagnostic reads"}),
    ("src/main/rs64_rdram_peek.h", "rs64_rdram_u32", None, "H-instrument-only", "any", "see rs64_rdram_u8", {"verify": r"Host-side diagnostic reads"}),
    # --- src/main rt64_render_context.cpp (send_dl / update_screen lambdas, Gfx thread) -----------------------------------------
    D(RC, "?", "ROGUESQ_DUMP_UCODE", A('// ROGUESQ_DUMP_UCODE=path — dump task ucode (IMEM) + ucode_data', -3, 47), thr=GFX),
    D(RC, "?", "ROGUESQ_DUMP_VTXDATA", A('const char* dump_path = std::getenv("ROGUESQ_DUMP_VTXDATA");', -3, 26), thr=GFX),
    F(RC, "?", "s_op_hist", A('const char* v = std::getenv("ROGUESQ_LOG_OPCODE_HIST");', 0, 139), thr=GFX),
    F(RC, "?", "s_sd", A('const char* e = std::getenv("ROGUESQ_STALL_DUMP"); s_sd = !(e && *e ==', 0, 20), thr=GFX),
    D(RC, "?", "ROGUESQ_FORCE_BUFFER_PROGRESS", A('// update_screen pass. Gated by ROGUESQ_FORCE_BUFFER_PROGRESS=1.', -2, 38), thr=GFX),
    F(RC, "?", "s_log_gs", A('if (s_log_gs && app->core.RDRAM && (s_n & 63) == 0) {', -1, 48), thr=GFX),
    F(RC, "?", "s_bw", A('static const char* s_bw = std::getenv("ROGUESQ_BUF_WATCH");', -3, 14), thr=GFX),
    D(RC, "?", "ROGUESQ_EDGE_DUMP", A('s_snap_n, (int)s_n, pvi->VI_ORIGIN_REG & 0x00FFFFFFu, nz[0], nz[1], nz', 0, 17), thr=GFX),
    (RC, "?", A('(unsigned long long)(t1 - s_g1cf.rt0), (unsigned long long)(r1 - s_g1c', 0, 20), "H-instrument-only", GFX, "VI-origin nonzero probe for a periodic log line (s_n<=4 || every 64)", {}),
    F(RC, "submit_rdp_range", "s_route_rows", A('const char *e = std::getenv("ROGUESQ_LOG_G1D_CMD");', -39, 11), thr=GFX),
    F(RC, "submit_rdp_range", "s_cmd_rows", A('if (op == 0x35) { s_st_w0[(w1 >> 24) & 7] = w0; s_st_w1[(w1 >> 24) & 7', 0, 26), thr=GFX),
    F(RC, "submit_rdp_range", "s_dumped", A('static uint32_t s_dumped = 0;', 0, 14), thr=GFX),
    F(RC, "submit_rdp_range", "s_img", A("s_img = (e && *e && *e != '0') ? 1 : 0;", 0, 40), thr=GFX),
    (RC, "submit_rdp_range", A('// ROGUESQ_LOG_RDP_SUBMIT=1.', -116, 123), "H-instrument-only", GFX, "first-seen / s_ci / s_tc log and count rows (ring words)", {}),
    # --- src/main upstream_compat.cpp ------------------------------------------------------------------------------------------
    (UC, "<file>", None, "not-guest", "-", "struct field declarations (alias false positive)", {}),
    D(UC, "rs64_g1d_copy_to_ram_trace", "ROGUESQ_LOG_G1D_COPY"),
    (UC, "s7333_hdr", None, "H-instrument-only", "any", "s7333 heap-header census (ROGUESQ_S7333*)", {"verify": r"ROGUESQ_S7333"}),
    F(UC, "rs64_g1d_tb2", "rs64_g1d_blk_enabled"),
    F(UC, "rs64_g1d_blk_dma", "rs64_g1d_blk_enabled"),
    (UC, "floorWriterWord", None, "H-instrument-only", "any", "s6689 ROGUESQ_FLOOR_WATCH word reader (log)", {"verify": r"ROGUESQ_FLOOR_WATCH"}),
    (UC, "rec", None, "H-instrument-only", "any", "s4262/s4263 send-trace record (log ring)", {}),
    (UC, "?", None, "H-instrument-only", "any", "lambda inside a diagnostic block (log)", {}),
    (UC, "rs64_s7399_recv", None, "H-guest-thread", GT, "s7399 osRecvMesg hook (" + GUESTCB + "), s7399::on() gated", {"verify": r"if \(!s7399::on\(\)\) return;"}),
    D(UC, "rs64_s4913_mark", "ROGUESQ_S4913"),
    # --- src/rsp dpc_bridge.cpp (Gfx thread, inside the F5 LLE DPC submits) ----------------------------------------------------
    (B, "rsp_dpc_submit_impl", r"MEM_B\(\d+, (?:mips|mips_first|mp|e9_mips)\)|submit_lo|rdram\[\(from \+ i\)", "H-canon", GFX, RING, {}),
    F(B, "rsp_dpc_submit_impl", "uc_on", A('std::chrono::steady_clock::time_point uc_t0;', 0, 20), thr=GFX),
    (B, "rsp_dpc_submit_impl", r"s_last_timg|0x4B7800|base \+ col|tlut|off \+ \d\) \^ 3", "H-instrument-only", GFX,
     "texture / TLUT / fixed-address byte dumps inside log_dpc / early-dump blocks (fprintf only)", {}),
    F(B, "rs64_count_submitted_e9", "log_e9_unified", thr=GFX),
    F(B, "rs64_m4_norm_sample", "rs64_m4_norm_enabled", thr="rsp"),
    F(B, "rs64_m4_dma_probe", "m4_src_enabled", thr="rsp"),
    F(B, "rs64_f5_dump_join", "rs64_f5_shadow_on", thr="rsp"),
    F(B, "rs64_f5_host_write_begin", "rs64_f5_shadow_on"),
    F(B, "rs64_f5_host_write_after", "rs64_f5_shadow_on"),
    D(B, "rs64_f5_vtx_store_range", "ROGUESQ_LOG_F5_STORE_SHADOW", thr="rsp"),
    (B, "rs64_dlw_root", None, "H-instrument-only", "rsp", "DL-walk root probe (log)", {}),
    (B, "rs64_spike_scan", None, "H-canon", GFX, "CULL_SPIKE ring scan: " + RING, {}),
    (B, "rs64_s7324_rd8", None, "H-instrument-only", GFX, "s7324 RDP spill-address census reader (rs64_s7324_on)", {"verify": r"rs64_s7324_on"}),
    F(B, "rs64_dpc_record_submit_impl", "log_tri_writer", thr=GFX),
    (B, "rs64_s7486_rdp", None, "H-instrument-only", GFX, "s7486 RDP census (g_rs64_s7486_on)", {"verify": r"g_rs64_s7486_on"}),
    ("src/rsp/s7521_ucode_watch.cpp", "ramb", None, "H-instrument-only", TASK, "s7521 ucode watch", {"envoff": "ROGUESQ_S7521_UCODEWATCH"}),
    ("src/rsp/s7535_ga_chk.cpp", "rs64_s7535_dma", None, "H-instrument-only", GFX, "s7535 GA window check (fdiff/hist rows)",
     {"envoff": "ROGUESQ_S7535_GA_CHK"}),
    ("src/rsp/s7535_ga_chk.cpp", "count", None, "H-instrument-only", GFX, "s7535 GA window check itself",
     {"envoff": "ROGUESQ_S7535_GA_CHK"}),
    ("src/rsp/s7526_v2p_twin.cpp", "rs64_s7526_fwd", None, "H-instrument-only", GFX, "s7526 V2P twin digest (g_open)", {}),
]


UCODE_TOOLS = ("tools/fixup_factor5_ucode.py", "tools/apply_s4220_snap.py", "tools/apply_s4210_cmd_ring.py",
               "tools/apply_fixup24_ovl2cdrop.py", "tools/apply_s4805_ovl2c_mode.py")
THREAD_ROOTS = {"task_thread_func": "task", "gfx_thread_func": "gfx", "vi_thread_func": "vi", "main": "main"}
_CG = {}


def callgraph(files):
    """Name-based call graph over ROOTS + splice index of the regen tools.  reach(fn) -> set of root threads:
    'guest' = a recomp_context ABI function (recompiled code / syscall replacement) or a symbol spliced into recompiled game
    code by tools/apply_*.py|fixup_*.py; 'rsp' = spliced into the RSP ucode C (UCODE_TOOLS); task/gfx/vi/main = the
    ultramodern thread functions; 'unknown:<fn>' = no caller found (callback / function pointer) -> needs a manual rule."""
    key = tuple(files)
    if key in _CG:
        return _CG[key]
    defs, callers = {}, defaultdict(set)
    for p in files:
        try:
            t = blank_strings(fw.strip_comments(open(p, errors="replace").read()))
        except OSError:
            continue
        for o, c, n in fz.func_spans(t):
            a = max(t.rfind(';', 0, o), t.rfind('}', 0, o), t.rfind('{', 0, o)) + 1
            defs.setdefault(n, []).append((t[a:o], t[o:c]))
    names = {n for n in defs if len(n) > 2 and n not in ("?", "<file>", "if", "for", "while", "switch")}
    call = re.compile(r'\b([A-Za-z_]\w*)\s*\(')
    for n, ds in defs.items():
        for h, b in ds:
            for m in call.finditer(b):
                if m.group(1) in names and m.group(1) != n:
                    callers[m.group(1)].add(n)
    splice = {}
    tdir = "tools"
    for f in sorted(os.listdir(tdir)) if os.path.isdir(tdir) else []:
        if re.match(r'(apply|fixup)_.*\.py$', f):
            txt = open(os.path.join(tdir, f), errors="replace").read()
            if os.path.join(tdir, f) in UCODE_TOOLS:
                kind = "rsp"
            elif re.search(r'RecompiledFuncs|funcs_\d+\.c|funcs_\*', txt):
                kind = "guest"
            else:
                continue          # patches librecomp/src text, not generated code: thread comes from the call graph
            # only names the tool DECLARES extern in its C splice (the inserted call), not every name it mentions
            decl = set(re.findall(r'extern\b[^;]*?\b([A-Za-z_]\w*)\s*\([^;]*\)\s*;', txt))
            if kind == "rsp":
                decl |= set(re.findall(r'\b(rs64_\w+)\s*\(', txt))   # ucode splices call rs64_* hooks
            for n in decl & names:
                splice.setdefault(n, set()).add(kind)
    memo = {}

    def reach(n, stack=()):
        if n in memo:
            return memo[n]
        if n in stack:
            return set()
        out = set()
        if any('recomp_context' in h for h, _ in defs.get(n, [])):
            out.add("guest")
        out |= splice.get(n, set())
        if n in THREAD_ROOTS:
            out.add(THREAD_ROOTS[n])
        cs = callers.get(n, set()) if n in names else set()
        for c in cs:
            out |= reach(c, stack + (n,))
        if not out:
            out.add("unknown:" + n)
        if not stack:
            memo[n] = out
        return out
    _CG[key] = (reach, callers)
    return _CG[key]


def classify(path, fn, raw, rules, ln, mode, reach):
    line = raw.split("\n")[ln - 1]
    rule = None
    for r in rules:
        if not (path.endswith(r[0]) and r[1] == fn):
            continue
        g = r[2]
        if isinstance(g, tuple) and g[0] == "@":
            g = resolve(path, raw, g)
            if isinstance(g, str):
                return "FAIL-check", r[4], g
        if g is None or (isinstance(g, tuple) and g[0] <= ln <= g[1]) or (isinstance(g, str) and re.search(g, line)):
            rule = r
            break
    if not rule:
        if mode == "log":
            return "log-only", "?", "read appears only in a log statement"
        th = reach(fn) if fn not in ("?", "<file>") else {"unknown:" + fn}
        if th == {"guest"}:
            return "H-guest-thread", "guest", "auto: every caller chain reaches a recomp_context ABI function or a guest splice"
        return "UNCLASSIFIED", ",".join(sorted(th))[:40], "no rule for %s" % fn
    err = fw.run_checks(path, raw, rule[6], fw.BINARY)
    return ("FAIL-check", rule[4], err) if err else (rule[3], rule[4], rule[5])


def census(files, rules=None, cg_files=None):
    rules = RULES if rules is None else rules
    reach, _ = callgraph(cg_files or fw.files_under(ROOTS))
    rows, fails = [], 0
    for p in files:
        r = sites(p)
        if not r:
            continue
        ss, raw = r
        for ln, kind, src, fn, mode in ss:
            cls, thr, why = classify(p, fn, raw, rules, ln, mode, reach)
            fails += cls in ("UNCLASSIFIED", "FAIL-check", "H-latent-fix")
            rows.append((p, ln, kind, src, fn, mode, cls, thr, why))
    return rows, fails


def short(p):
    return p.replace("lib/N64ModernRuntime/", "")


def main():
    if "--controls" in sys.argv:
        sys.exit(controls())
    rows, fails = census(fw.files_under(ROOTS))
    if "--fn" in sys.argv:
        agg = defaultdict(Counter)
        for r in rows:
            agg[(short(r[0]), r[4], r[6])][r[5]] += 1
        for (f, fn, cls), c in sorted(agg.items()):
            if "--all" in sys.argv or cls in ("UNCLASSIFIED", "FAIL-check"):
                lines = sorted({r[1] for r in rows if short(r[0]) == f and r[4] == fn})
                th = next(r[7] for r in rows if short(r[0]) == f and r[4] == fn)
                print("%-40s %-32s %-13s %-18s %s %s" % (f[-40:], fn[:32], cls[:13], th[:18], dict(c), lines[:8]))
    else:
        for r in rows:
            print("%s\t%d\t%s\t%s\t%s\t%s\t%s\t%s\t%s" % (short(r[0]), r[1], r[2], r[3][:28], r[4][:30], r[5], r[6], r[7],
                  r[8][:90] if "--why" in sys.argv else ""))
    print("summary: sites=%d decide=%d %s fails=%d" % (len(rows), sum(1 for r in rows if r[5] == "decide"),
          dict(sorted(Counter(r[6] for r in rows).items())), fails))
    sys.exit(1 if fails else 0)


def controls():
    res = []
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "fixture_ga.cpp")
        open(p, "w").write(
            "static void gfx_hook(uint8_t* rdram) { if (rdram[0x1234 ^ 3] == 2) skip(); }\n"
            "static void alias(uint8_t* rdram) { const uint32_t* w = (const uint32_t*)(rdram + 0x40); if (w[2]) go(); }\n"
            "static void logonly(uint8_t* rdram) { fprintf(stderr, \"%d\\n\", rdram[7]); }\n"
            "static void store(uint8_t* rdram) { rdram[9] = 1; }\n"
            "static uint32_t helper(uint8_t* rdram) { return rdram[0x20 ^ 3]; }\n"
            "void game_fn(uint8_t* rdram, recomp_context* ctx) { if (helper(rdram) > 3) ctx->r2 = rdram[0x30 ^ 3]; }\n")
        rows, fails = census([p], cg_files=[p])
        by = {}
        for r in rows:
            by.setdefault(r[4], []).append(r[6])
        res.append(("planted gfx-thread decision read -> UNCLASSIFIED", by.get("gfx_hook") == ["UNCLASSIFIED"], rows))
        res.append(("alias read through local pointer -> caught", by.get("alias") == ["UNCLASSIFIED"], rows))
        res.append(("read only inside fprintf -> log-only", by.get("logonly") == ["log-only"], rows))
        res.append(("store is not a read row", "store" not in by, rows))
        res.append(("recomp_context ABI fn -> H-guest-thread(auto)", by.get("game_fn") == ["H-guest-thread"], rows))
        res.append(("helper reached only from ABI fn -> H-guest-thread(auto)", by.get("helper") == ["H-guest-thread"], rows))
        # mutation: drop the s7535 instrument from a copy of rsp.hpp -> the gfx RSP-DMA read rows must FAIL their verify
        src = "lib/N64ModernRuntime/librecomp/include/librecomp/rsp.hpp"
        mut = os.path.join(d, "librecomp", "rsp.hpp"); os.makedirs(os.path.dirname(mut))
        txt = open(src, errors="replace").read()
        open(mut, "w").write(re.sub(r'ROGUESQ_S7535_GA_CHK', 'ROGUESQ_GONE', txt))
        rows, fails = census([mut])
        bad = [r for r in rows if r[4] == "dma_rdram_to_dmem" and 380 <= r[1] <= 400]
        res.append(("mutation: GA instrument removed -> dma rows FAIL-check", bool(bad) and all(r[6] == "FAIL-check" for r in bad), bad[:2]))
        # s7651 anchor-drift: duplicate the MISSION_WIN anchor line in a copy of main.cpp -> its rule must FAIL-check (loud),
        # and shifting the file by 900 blank lines above must leave every row's class unchanged (anchors follow the code)
        mn = os.path.join(d, "src", "main", "main.cpp"); os.makedirs(os.path.dirname(mn))
        txt = open("src/main/main.cpp", errors="replace").read()
        anc = "// s5604: ROGUESQ_MISSION_WIN=<n> is a TEST-ONLY lever"
        base, _ = census(["src/main/main.cpp"])
        open(mn, "w").write("\n" * 900 + txt)
        sh, _ = census([mn])
        same = [(r[1], r[6]) for r in base] == [(r[1] - 900, r[6]) for r in sh]
        res.append(("anchor: +900-line shift leaves main.cpp classes unchanged", same, len(base)))
        line = next(l for l in txt.split("\n") if anc in l)
        open(mn, "w").write(txt.replace(line, line + "\n" + line, 1))
        rows, _ = census([mn])
        dup = [r for r in rows if r[4] == "get_n64_input" and r[6] == "FAIL-check" and "anchor" in r[8]]
        res.append(("anchor: duplicated anchor -> get_n64_input rows FAIL-check", bool(dup), len(dup)))
    rows, fails = census(fw.files_under(ROOTS), rules=[])
    res.append(("coverage: rule-less census sees >=250 UNCLASSIFIED", fails >= 250, "fails=%d" % fails))
    rows, fails = census(fw.files_under(ROOTS))
    open_ = [r for r in rows if r[6] == "H-latent-fix"]
    fixed = [r for r in rows if r[6] == "H-latent-FIXED(opt-in)"]
    res.append(("live census: 0 UNCLASSIFIED/FAIL-check", not [r for r in rows if r[6] in ("UNCLASSIFIED", "FAIL-check")],
                [r for r in rows if r[6] in ("UNCLASSIFIED", "FAIL-check")][:4]))
    res.append(("live census: 0 open H-latent-fix; FIXED(opt-in) = the s7535 gfx DMA", not open_ and fixed and all(r[4] == "dma_rdram_to_dmem" for r in fixed),
                (open_ or fixed)[:3]))
    ok = True
    for name, good, detail in res:
        print("control %-56s %s %s" % (name, "PASS" if good else "FAIL", "" if good else str(detail)[:300]))
        ok &= bool(good)
    print("controls: %d/%d PASS" % (sum(1 for r in res if r[1]), len(res)))
    return 0 if ok else 1


if __name__ == "__main__":
    main()
