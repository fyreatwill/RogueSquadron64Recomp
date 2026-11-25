#!/usr/bin/env python3
"""s7530 class FW census: file-scope / function-static SCALAR latches holding a guest address or
guest-derived position (names containing addr|ptr|base|last|cur|first|start|prev|origin|src|dst|zimg|cimg|fb|seg), the scalar twin of class FV
(tools/s7529_fv_census.py, containers).  A latch is set when guest state appears and read later; if
the guest reuses the address between set and read, the host acts on stale state.

Per site the tool finds every FUNCTIONAL read: an occurrence that is not the declaration, not a pure
write (=, ++, +=, .store), and not inside a statement that logs (printf/fputs/fwrite/...).
  instr-only(auto)  no functional read: the latch only feeds logs                       -> closed
  rule              explicit row in RULES (class + reason).  Optional checks, each must hold:
                      verify=<regex>   must match in the file (re-set / gate / reset site present)
                      nocaller=<sym>   the linked binary must contain NO `bl <sym>` and no
                                       page+offset address-take of it (dead entry point)
                      envoff=<VAR>     the gating env var must be absent from the owner/loop config
  group             identifier matches a GROUPS regex (diagnostic family) + its gate regex is in file
  UNCLASSIFIED      functional read and no rule -> FAIL (census incomplete)

  python3 tools/s7530_fw_census.py              # table of non-auto rows, exit 1 on any FAIL
  python3 tools/s7530_fw_census.py --controls   # planted fixtures + binary positive control
"""
import os, re, subprocess, sys, tempfile

ROOTS = ["lib/N64ModernRuntime/librecomp/src", "lib/N64ModernRuntime/ultramodern/src", "src/main", "src/rsp"]
BINARY = "build/RogueSquadron64Recomp"
CONFIG_FILES = ["tools/agent/runner.sh", "docs/OWNER-OPT-INS.md"]
DECL = re.compile(r'^\s*((?:static\s+|thread_local\s+|extern\s+)*)(?:std::atomic<\s*)?'
                  r'(u?int(?:32|64)_t|uintptr_t|gpr|PTR\(\w+\)|unsigned)\s*>?\s+(.*?);')
NAME = re.compile(r'(addr|ptr|base|last|cur|first|start|prev|origin|src|dst|zimg|cimg|fb\b|_fb|seg)', re.I)
LOG = re.compile(r'printf|fputs|fputc|std::cerr|fwrite|\bputs\b|fflush|o\[i\+\+\]')

# (file suffix, identifier, class, reason, checks dict)
RULES = [
    # --- functional latches on guest addresses -------------------------------------------------
    ("src/main/main.cpp", "s_pending_task_data_ptr", "H-canon",
     "thread_local; re-set from task->t.data_ptr in get_rsp_microcode immediately before the runner on the same thread",
     {"verify": r"s_pending_task_data_ptr\s*=\s*\(uint32_t\)task->t\.data_ptr"}),
    ("src/main/main.cpp", "g_rs64_pcm_task_data_ptr", "H-canon",
     "re-set every audio task (rs64_m5_pcm_task_data_set in get_rsp_microcode M_AUDTASK); accessor feeds logs only",
     {"verify": r"rs64_m5_pcm_task_data_set\(s_pending_task_data_ptr\)"}),
    ("src/main/main.cpp", "g_rs64_pcm_last_dma_phys", "H-instrument-only",
     "PCM writer provenance note (rs64_pcm_writer_note) - diagnostic", {}),
    ("src/main/main.cpp", "g_rsp_dma_shadow2_addr", "H-dead",
     "captured once from the ucode image (immutable: s7521 FR RSP code bytes == images); read only by the s_diff_logs<24 compare",
     {"verify": r"s_diff_logs < 24"}),
    ("src/main/main.cpp", "g_rs64_m5_descriptor_yield_ptr", "H-instrument-only",
     "ROGUESQ_LOG_M5_DESCRIPTOR compare-for-log", {"verify": r"ROGUESQ_LOG_M5_DESCRIPTOR"}),
    ("src/main/main.cpp", "g_vld_addr", "H-instrument-only",
     "spike DMEM provenance (g_spike_dmem_on / ROGUESQ_SPIKE_DMEM) - diagnostic", {"verify": r"g_spike_dmem_on"}),
    ("src/main/main.cpp", "root_base", "H-instrument-only", "first-root anchor for relative offsets in a log row", {}),
    ("src/main/main.cpp", "s_fs_last_post_w0", "H-instrument-only", "[fs-slot] inter-task delta detector (log gate)", {}),
    ("src/main/main.cpp", "last_unknown", "H-canon", "task-type edge detector, re-set on change (log once per type)", {}),
    ("librecomp/src/ultra_translation.cpp", "last", "H-canon",
     "s7913 ROGUESQ_DET_CLOCK=1 thread_local monotonic clamp of the synthetic Count value, not a guest address; re-set every call",
     {"verify": r"last = v; return v;"}),
    ("src/main/main.cpp", "last_after", "H-canon", "audio queue size (host), not a guest address; re-set every call", {}),
    ("src/main/main.cpp", "prev_array_base", "H-instrument-only", "change detector for a log row", {}),
    ("src/main/main.cpp", "s_cur", "H-dead", "autopilot target index (ROGUESQ_AIM harness), not a guest address", {}),
    ("src/main/main.cpp", "s_cur_polls", "H-dead", "autopilot poll counter, not a guest address", {}),
    ("src/main/main.cpp", "s_last_fs", "H-canon",
     "s7907 autopilot f<N> anchor: host RDP fullsync count, not a guest address; re-set at every fire",
     {"verify": r"s_last_fs\s*=\s*\(uint32_t\)rs64_dpc_get_cumulative_fullsyncs\(\)"}),
    ("src/main/main.cpp", "g_rs64_audio_last_prepare_seq", "H-instrument-only", "M5 identity edge sequence number (log)", {}),
    ("src/main/main.cpp", "last_phase", "H-instrument-only", "phase-ordinal change detector for a log budget", {}),
    ("src/rsp/dpc_bridge.cpp", "g_last_fullsync_addr", "H-dead",
     "two functional readers: rsp_force_fullsync re-submits the 8 bytes at the latched address WITHOUT re-checking they are "
     "still E9 (stale-able), but it has no caller in the linked binary; ROGUESQ_FS_PIPE_INJECT (default off) re-reads the "
     "cell op before injecting from host scratch",
     {"nocaller": "_rsp_force_fullsync", "envoff": "ROGUESQ_FS_PIPE_INJECT"}),
    ("src/rsp/dpc_bridge.cpp", "g_last_wrap_start", "H-dead",
     "should_drop_wrap_rdp drops submits inside a sticky past-wrap window (stale-able) but only under ROGUESQ_DROP_WRAP_RDP "
     "(default off); otherwise read by RT64 WILD-SETCIMG dumps", {"envoff": "ROGUESQ_DROP_WRAP_RDP"}),
    ("src/rsp/dpc_bridge.cpp", "g_last_wrap_seen", "H-dead", "see g_last_wrap_start", {"envoff": "ROGUESQ_DROP_WRAP_RDP"}),
    ("src/rsp/dpc_bridge.cpp", "g_last_wrap_end", "H-instrument-only", "accessor for RT64 WILD-SETCIMG dumps", {}),
    ("src/rsp/dpc_bridge.cpp", "g_last_wrap_n", "H-instrument-only", "accessor for RT64 WILD-SETCIMG dumps", {}),
    ("src/rsp/dpc_bridge.cpp", "g_last_submit_lo", "H-instrument-only", "accessor for RT64 shade/WILD dumps", {}),
    ("src/rsp/dpc_bridge.cpp", "g_last_submit_hi", "H-instrument-only", "accessor for RT64 shade/WILD dumps", {}),
    ("src/rsp/dpc_bridge.cpp", "s_task_last_lo", "H-canon", "zeroed at task reset; accessor rs64_dpc_get_task_range (logs)",
     {"verify": r"s_task_last_lo = 0;"}),
    ("src/rsp/dpc_bridge.cpp", "s_task_last_hi", "H-canon", "zeroed at task reset with s_task_last_lo", {"verify": r"s_task_last_hi = 0;"}),
    ("src/rsp/dpc_bridge.cpp", "s_submit_dl_base", "H-canon",
     "forward window: re-set on every DPC_START change and zeroed in rs64_dpc_reset per task (s7096/s7523 forwarding exact)",
     {"verify": r"s_submit_dl_base = 0;"}),
    ("src/rsp/dpc_bridge.cpp", "s_submit_last_end", "H-canon", "see s_submit_dl_base", {"verify": r"s_submit_last_end = 0;"}),
    ("src/rsp/dpc_bridge.cpp", "g_rsp_dpc_current", "H-canon", "DPC_CURRENT register model, zeroed in rs64_dpc_reset (s7095 model)",
     {"verify": r"g_rsp_dpc_current = 0;"}),
    ("src/rsp/dpc_bridge.cpp", "s_dpc_poll_last", "H-canon", "DPC poll repeat detector, reset in rs64_dpc_reset",
     {"verify": r"s_dpc_poll_last = 0xFFFFFFFFu;"}),
    ("src/rsp/dpc_bridge.cpp", "s_last", "H-instrument-only", "10 s timing-window anchor (host ticks) / alias of s_dpc_poll_last", {}),
    ("src/rsp/dpc_bridge.cpp", "g_pak_last_tlut_addr", "H-instrument-only",
     "[dpc-pak] TLUT dump inside the logging branch only", {"verify": r"\[dpc-pak\] TLUT @"}),
    ("src/rsp/dpc_bridge.cpp", "g_cine_last_cimg_addr", "H-instrument-only",
     "OOB-CIMG log + g_cine_fb_owner_slot (write-only, FV s7529 H-dead)", {}),
    ("src/rsp/dpc_bridge.cpp", "s_clast", "H-canon",
     "G1d region colour-image edge detector, re-set on every SETCIMG (ci != s_clast -> s_clast = ci)", {"verify": r"s_clast = ci;"}),
    ("src/rsp/dpc_bridge.cpp", "s_last_timg", "H-instrument-only", "texture-source dump in a logging walk", {}),
    ("src/main/upstream_compat.cpp", "s_last_mode", "H-canon",
     "osViSetMode pointer edge detector (G1d epoch), re-set on change; keys are ROM-static osViModeTable entries",
     {"verify": r"s_last_mode = mode_ptr;"}),
    ("src/main/upstream_compat.cpp", "g_m5_host_current_seq", "H-instrument-only", "M5 host sequence number for log joins", {}),
    ("src/main/upstream_compat.cpp", "g_cine_last_ms", "H-instrument-only", "[cine-progress] idle age (host ms)", {}),
    ("src/main/upstream_compat.cpp", "s_last_log_ms", "H-instrument-only", "log cadence (host ms)", {}),
    ("src/main/upstream_compat.cpp", "s_last_log_iter", "H-instrument-only", "log cadence", {}),
    ("src/main/upstream_compat.cpp", "s_last_ms", "H-instrument-only", "log cadence (host ms)", {}),
    ("src/main/upstream_compat.cpp", "last_phase", "H-instrument-only", "phase-ordinal change detector for a log budget", {}),
    ("src/main/upstream_compat.cpp", "last", "H-instrument-only", "log cadence (host ticks)", {}),
    ("src/main/main.cpp", "last", "H-instrument-only",
     "s4459 loadCharTextureSet fill-table log (function-local static; other `last` hits are unrelated identifiers)",
     {"verify": r"s4459: loadCharTextureSet"}),
    ("src/main/upstream_compat.cpp", "last_b40_stored", "H-instrument-only", "ROGUESQ_LOG_M5_B40_ROUTE change log (early return when off)",
     {"verify": r"ROGUESQ_LOG_M5_B40_ROUTE"}),
    ("src/main/main.cpp", "last_h", "H-instrument-only",
     "s7779 FB-arena census epoch detector in rs64_s7779_note (early return unless ROGUESQ_S7779_ARENA=1; feeds log rows/counters only)",
     {"verify": r"if \(!s_s7779_on\) return;"}),
    ("src/main/upstream_compat.cpp", "last_b40_return", "H-instrument-only", "see last_b40_stored", {"verify": r"ROGUESQ_LOG_M5_B40_ROUTE"}),
    # --- widened-name sites (first/start/prev/origin/src/zimg/cimg) ---
    ("src/rsp/dpc_bridge.cpp", "s_zimg", "H-canon",
     "G1d region gate RDP-register mirror: re-set by every SET_Z_IMAGE (op 0x3E) in the same stream walk",
     {"verify": r"op == 0x3E\) s_zimg = w1 & 0xFFFFFFu"}),
    ("src/rsp/dpc_bridge.cpp", "cimg", "H-instrument-only", "rs64_floor_scan (ROGUESQ_LOG_FLOOR) RDP-state mirror for keyed log rows",
     {"verify": r"ROGUESQ_LOG_FLOOR"}),
    ("src/rsp/dpc_bridge.cpp", "cimg_w", "H-instrument-only", "see cimg", {"verify": r"ROGUESQ_LOG_FLOOR"}),
    ("src/rsp/dpc_bridge.cpp", "zimg", "H-instrument-only", "see cimg", {"verify": r"ROGUESQ_LOG_FLOOR"}),
    ("src/rsp/dpc_bridge.cpp", "s_task_first_lo", "H-canon", "per-task range, zeroed at task reset (first submit re-latches); accessor feeds logs", {"verify": r"s_task_first_hi = 0;"}),
    ("src/rsp/dpc_bridge.cpp", "s_task_first_hi", "H-canon", "per-task range, zeroed at task reset (first submit re-latches); accessor feeds logs", {"verify": r"s_task_first_hi = 0;"}),
    ("src/rsp/dpc_bridge.cpp", "g_dlw_zero_src", "H-canon", "dlw zero-source dedupe, memset when the task changes",
     {"verify": r"memset\(g_dlw_zero_src, 0"}),
    ("src/rsp/dpc_bridge.cpp", "s_ring_prev", "H-instrument-only", "[spike-dma] ring cursor for a log row", {}),
    ("src/rsp/dpc_bridge.cpp", "s_cov_origin", "H-instrument-only", "coverage accumulator frame key (log)", {}),
    ("src/rsp/dpc_bridge.cpp", "prevOrigin", "H-instrument-only", "per-frame ordinal for a log row", {}),
    ("src/rsp/dpc_bridge.cpp", "prevWidth", "H-instrument-only", "per-frame ordinal for a log row", {}),
    ("src/rsp/dpc_bridge.cpp", "s_first", "H-instrument-only", "first-N log budgets (function-local statics share the name)", {}),
    ("ultramodern/src/events.cpp", "vis_origin", "H-instrument-only", "[vi-feat-commit] luma of the previously shown image", {}),
    ("ultramodern/src/events.cpp", "vi_previous_game_total_vis", "H-instrument-only", "VI callback delta for logs (host count)", {}),
    ("ultramodern/src/mesgqueue.cpp", "prev", "H-instrument-only", "per-VI enqueue counters for a log row (host)", {}),
    ("src/main/main.cpp", "previous_queue", "H-instrument-only", "audio queue delta log rows (host)", {}),
    ("src/main/main.cpp", "s_prev_fl", "H-instrument-only", "change detector for a 64-row log", {}),
    ("src/main/upstream_compat.cpp", "prev", "H-instrument-only", "function-local change detectors / counters for logs", {}),
    ("src/main/rt64_render_context.cpp", "s_last_width", "H-instrument-only", "[phase] vi_width transition log", {}),
    ("src/main/rt64_render_context.cpp", "s_last_ucode", "H-instrument-only", "ucode-change log gate", {}),
    ("src/main/rt64_render_context.cpp", "s_last_data", "H-instrument-only", "ucode-change log gate", {}),
    ("src/main/rt64_render_context.cpp", "s_last_cineState", "H-instrument-only", "game-state change log gate", {}),
    ("src/main/rt64_render_context.cpp", "s_last_cutscene", "H-instrument-only", "game-state change log gate", {}),
    ("src/main/rt64_render_context.cpp", "wk_last_bytes", "H-instrument-only", "G1e timing accumulator", {}),
    ("src/main/rt64_render_context.cpp", "last_phase", "H-instrument-only", "phase-ordinal change detector for a log budget", {}),
    ("ultramodern/src/events.cpp", "last_phase", "H-instrument-only", "phase-ordinal change detector for a log budget", {}),
    ("ultramodern/src/events.cpp", "last", "H-instrument-only", "[vi-shape] register-tuple change log (rs64_vi_shape_log)", {}),
    ("ultramodern/src/events.cpp", "last_ctrl", "H-instrument-only", "VI control change log", {}),
    ("ultramodern/src/events.cpp", "last_vs", "H-instrument-only", "VI control change log", {}),
    ("ultramodern/src/events.cpp", "last_ctl", "H-instrument-only", "VI control change log", {}),
    ("librecomp/src/cont.cpp", "last", "H-instrument-only", "ROGUESQ_PAD_LOG pad-transition log", {"verify": r"ROGUESQ_PAD_LOG"}),
    ("librecomp/src/rsp.cpp", "lastv", "H-instrument-only", "DMEM word change log", {}),
]
# Diagnostic families: identifier regex, gate regex that must be in the file, reason.
GROUPS = [
    (r"^g_rs64_m5_", r"ROGUESQ_LOG_M5|rs64_m5_", "M5 audio route-fingerprint diagnostics (sequence/fnv/dram joins for logs)"),
    (r"^g_flz_last_", r"g_flz_", "fault-log-zone watchdog breadcrumbs (printed at fault/exit)"),
    (r"^g_last_(othermode|settimg|setcimg|settile|fogcolor|primcolor|envcolor|blendcolor)", r"now_64tri && !s_in_64tri && log_dpc\(\)",
     "RDP state snapshot printed by the log_dpc() 64-tri mux log"),
    (r"^g_cine_last_settimg_", r"g_cine_last_settimg_addr", "cinematic SETTIMG snapshot for logs"),
]
DIAG_FILE = re.compile(r'/s\d{4}\w*\.(cpp|c|h)$')


def strip_comments(t):
    keep_nl = lambda m: re.sub(r'[^\n]', ' ', m.group(0))
    t = re.sub(r'/\*.*?\*/', keep_nl, t, flags=re.S)
    return re.sub(r'//[^\n]*', keep_nl, t)


def sites(path):
    """Yield (line, name, functional_read_lines) for every scalar latch declared in path."""
    try:
        raw = open(path, errors="replace").read()
    except OSError:
        return
    t = strip_comments(raw)
    lines = t.split("\n")
    starts = [0]
    for ln in lines[:-1]:
        starts.append(starts[-1] + len(ln) + 1)
    import bisect
    for i, l in enumerate(lines):
        m = DECL.match(l)
        if not m:
            continue
        quals = m.group(1)
        indented = len(l) - len(l.lstrip()) > 0
        if "extern" in quals or (indented and "static" not in quals and "thread_local" not in quals):
            continue
        if "(" in m.group(3).split("=")[0]:
            continue
        for part in m.group(3).split(","):
            nm = re.match(r'\s*\**\s*(\w+)', part)
            if not nm:
                continue
            n = nm.group(1)
            if not NAME.search(n) or re.search(r's\d{4}', n):
                continue
            fr = []
            for mm in re.finditer(r'\b' + re.escape(n) + r'\b', t):
                lno = bisect.bisect_right(starts, mm.start())
                if lno == i + 1:
                    continue
                a = max(t.rfind(';', 0, mm.start()), t.rfind('{', 0, mm.start()), t.rfind('}', 0, mm.start())) + 1
                b = t.find(';', mm.end())
                stmt = t[a:b]
                if LOG.search(stmt):
                    continue
                s2 = t[mm.start():b]
                if re.match(re.escape(n) + r'\s*(\[[^\]]*\])?\s*(=(?!=)|\+\+|--|\+=|-=|\|=)', s2) or \
                   re.match(re.escape(n) + r'\.(store|fetch_add|exchange)\(', s2) or \
                   re.search(r'(\+\+|--)\s*$', t[a:mm.start()]):
                    continue
                fr.append(lno)
            yield i + 1, n, sorted(set(fr)), raw


_bin_cache = {}


def binary_refs(sym, binary):
    """Count `bl <sym>` call sites and adrp-page + add-offset address-takes of sym in the binary."""
    if binary not in _bin_cache:
        try:
            _bin_cache[binary] = subprocess.run(["objdump", "-d", "--no-show-raw-insn", binary],
                                                capture_output=True, text=True).stdout
        except OSError:
            _bin_cache[binary] = ""
    dis = _bin_cache[binary]
    m = re.search(r'^([0-9a-f]+) <' + re.escape(sym) + r'>:', dis, re.M)
    if not m:
        return None
    addr = int(m.group(1), 16)
    calls = len(re.findall(r'\bbl\s+0x[0-9a-f]+ <' + re.escape(sym) + r'>', dis))
    page, off = addr & ~0xFFF, addr & 0xFFF
    takes = 0
    prev = None
    for line in dis.split("\n"):
        if prev is not None and re.search(r'\badd\s+x\d+, x\d+, #0x%x\b' % off, line):
            takes += 1
        pm = re.search(r'\badrp\s+x\d+, 0x([0-9a-f]+)', line)
        prev = pm if (pm and int(pm.group(1), 16) == page) else None
    return calls, takes


def run_checks(path, raw, checks, binary):
    for k, v in checks.items():
        if k == "verify" and not re.search(v, raw):
            return "verify /%s/ not found" % v
        if k == "nocaller":
            r = binary_refs(v, binary)
            if r is None:
                return "nocaller: %s not in %s" % (v, binary)
            if r[0] or r[1]:
                return "nocaller: %s has %d calls, %d address-takes" % (v, r[0], r[1])
        if k == "envoff":
            for cf in CONFIG_FILES:
                if os.path.exists(cf) and re.search(r'\b' + v + r'=[1-9]', open(cf, errors="replace").read()):
                    return "envoff: %s armed in %s" % (v, cf)
    return None


def census(files, rules=RULES, binary=BINARY):
    rows, fails = [], 0
    for path in files:
        for ln, n, fr, raw in sites(path):
            rule = next((r for r in rules if path.endswith(r[0]) and r[1] == n), None)
            if rule:
                cls, why = rule[2], rule[3]
                err = run_checks(path, raw, rule[4], binary)
                if err:
                    cls, why = "FAIL-check", err
                    fails += 1
            elif not fr:
                cls, why = "instr-only(auto)", "no functional read"
            elif DIAG_FILE.search(path):
                cls, why = "diag", "sNNNN diagnostic file"
            else:
                g = next((g for g in GROUPS if re.search(g[0], n) and re.search(g[1], raw)), None)
                if g:
                    cls, why = "group:H-instrument-only", g[2]
                else:
                    cls, why = "UNCLASSIFIED", "functional read at %s, no rule" % fr[:4]
                    fails += 1
            rows.append((path, ln, n, cls, why))
    return rows, fails


def files_under(roots):
    out = []
    for r in roots:
        for dp, _, fns in os.walk(r):
            out += [os.path.join(dp, f) for f in fns if f.endswith((".cpp", ".h", ".hpp", ".c"))]
    return sorted(out)


def controls():
    res = []
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "fixture_latch.cpp")
        open(p, "w").write("static uint32_t g_planted_addr = 0;\n"
                           "void set(uint32_t a){ g_planted_addr = a; }\n"
                           "void use(uint8_t* rdram){ rdram[g_planted_addr] = 1; }\n")
        rows, fails = census([p], RULES)
        res.append(("planted-functional-latch -> UNCLASSIFIED", fails == 1 and rows[0][3] == "UNCLASSIFIED", rows))
        q = os.path.join(d, "fixture_log.cpp")
        open(q, "w").write("static uint32_t g_planted_last = 0;\n"
                           "void f(uint32_t a){ g_planted_last = a;\n  fprintf(stderr, \"%u\\n\",\n    g_planted_last); }\n")
        rows, fails = census([q], RULES)
        res.append(("planted-log-only-latch -> instr-only(auto)", fails == 0 and rows[0][3] == "instr-only(auto)", rows))
        rules = RULES + [("fixture_latch.cpp", "g_planted_addr", "H-canon", "x", {"verify": r"g_planted_addr = 0;\s*//reset"})]
        rows, fails = census([p], rules)
        res.append(("ruled-but-reset-missing -> FAIL-check", fails == 1 and rows[0][3] == "FAIL-check", rows))
    # binary: a function with known callers must FAIL nocaller; the live rsp_force_fullsync must pass it
    pos = binary_refs("_rs64_dpc_reset", BINARY)
    res.append(("binary positive: _rs64_dpc_reset has callers", bool(pos and (pos[0] or pos[1])), pos))
    neg = binary_refs("_rsp_force_fullsync", BINARY)
    res.append(("binary: _rsp_force_fullsync has 0 calls/takes", neg == (0, 0), neg))
    rows, fails = census(files_under(ROOTS))
    res.append(("live census 0 fails", fails == 0, "fails=%d" % fails))
    ok = True
    for name, good, detail in res:
        print("control %-48s %s %s" % (name, "PASS" if good else "FAIL", "" if good else detail))
        ok &= good
    print("controls: %d/%d PASS" % (sum(1 for r in res if r[1]), len(res)))
    return 0 if ok else 1


def main():
    if "--controls" in sys.argv:
        sys.exit(controls())
    rows, fails = census(files_under(ROOTS))
    from collections import Counter
    cnt = Counter(r[3] for r in rows)
    for r in rows:
        if r[3] not in ("instr-only(auto)", "diag") and not r[3].startswith("group"):
            print("%-48s %5d %-34s %-18s %s" % (r[0].replace("lib/N64ModernRuntime/", ""), r[1], r[2], r[3], r[4][:110]))
    print("summary: sites=%d %s fails=%d" % (len(rows), dict(cnt), fails))
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
