#!/usr/bin/env python3
"""s7633 class HB census: default-on diagnostic work in the HOST bridge (src/rsp/dpc_bridge.cpp + src/main/rt64_render_context.cpp).
Reuses tools/s7632_dd_census.py (join + gate propagation) and adds the bridge's hand classes.

  python3 tools/s7633_hb_census.py SCAN.json AST.json [--plant-scan P.json --plant-ast P.json] [--drop-control]

  SCAN/AST from: tools/s7632_dd_scan.py / tools/s7632_dd_ast.py --hot src/rsp/dpc_bridge.cpp,src/main/rt64_render_context.cpp
Both extractors only see a gate when the env read is in the same condition; the bridge gates on env-latched GLOBALS
(g_rs64_s7026 = ROGUESQ_S7026_SUB, g_rs64_aq_on = ROGUESQ_G1E_AQ via main.cpp:7219, g_bf_check, g_bfsh_mode, ...) and on
`if (s_x < 0) { getenv }` latches; every row below was read by hand with the enclosing-condition walker scratch/s7633/encl.py."""
import importlib.util, sys
spec = importlib.util.spec_from_file_location("c32", __file__.replace("s7633_hb_census.py", "s7632_dd_census.py"))
c = importlib.util.module_from_spec(spec); spec.loader.exec_module(c)

ENVG = "gated"; SC = "scalar"; FN = "functional"
c.CLASS.update({
    # rt64_render_context.cpp
    "rs64_scr_t0": (FN, "update_screen entry timestamp read by the s7016/G1b present-timing ring (one clock read per VI)"),
    "rs64_scr_t1": (FN, "update_screen drain timestamp (one clock read per VI)"),
    "rs64_vi_n_g": (FN, "VI counter read by phase gates everywhere"),
    "g_rs64_g1cf_tasks": (ENVG, "inside `if (s_f)` = ROGUESQ_G1CF latch"), "g_rs64_g1cf_dsize": (ENVG, "inside `if (s_f)` (ROGUESQ_G1CF)"),
    "rs64_s7858_tick": (ENVG, "s7858 mission-tick ordinal: rs64_xtrace_mark is only called under `if (g_rs64_rand_trace)` (ROGUESQ_RAND_TRACE, fixup_rand_trace.py hooks)"),
    "g_rs64_g1d_ci_frame": (ENVG, "push_back <=64 inside `if (s_route || s_words)` (ROGUESQ_LOG_RDP_ROUTE / _WORDS latches)"),
    # dpc_bridge.cpp
    "rs64_s6843_lo": (ENVG, "rs64_wipe_scan returns unless ROGUESQ_WIPE_SCAN=<lo:hi> (static `on`)"),
    "rs64_s6843_len": (ENVG, "rs64_wipe_scan (ROGUESQ_WIPE_SCAN)"),
    "g_rs64_s7026_rec_ns": (ENVG, "after `if (!g_rs64_s7026) return` (ROGUESQ_S7026_SUB static initialiser, dpc_bridge.cpp:6045)"),
    "g_rs64_s7026_rec_n": (ENVG, "ROGUESQ_S7026_SUB"), "g_rs64_s7026_smp_w": (ENVG, "ROGUESQ_S7026_SUB"),
    "g_rs64_s7026_smp_c": (ENVG, "ROGUESQ_S7026_SUB"), "g_rs64_s7026_smp_n": (ENVG, "ROGUESQ_S7026_SUB"),
    "g_rs64_s7026_rt_ns": (ENVG, "ROGUESQ_S7026_SUB"), "g_rs64_s7026_rt_n": (ENVG, "ROGUESQ_S7026_SUB"),
    "g_rs64_s7026_rt_by": (ENVG, "ROGUESQ_S7026_SUB"),
    "g_rs64_bf_chk2_ctl": (ENVG, "inside `if (g_bf_check_flag())` (ROGUESQ_G1E_BUMPFAST_CHECK static)"),
    "g_rs64_bf_chk2_n": (ENVG, "g_bf_check"), "g_rs64_bf_chk2_bad": (ENVG, "g_bf_check"),
    "g_rs64_bf_chk_ctl": (ENVG, "check-guard methods return unless `on`, armed only under g_bf_check"),
    "g_rs64_bf_chk_n": (ENVG, "g_bf_check guard"), "g_rs64_bf_chk_bad": (ENVG, "g_bf_check guard"),
    "g_rs64_trim": (FN, "per-flush latch of the default-on ROGUESQ_G1E_TRIM fast path (static env + scalar store)"),
    "g_rs64_tmem_fast": (FN, "per-flush latch of default-on ROGUESQ_G1E_TMEM"), "g_rs64_g1e_lbfast": (FN, "latch of default-on ROGUESQ_G1E_LBFAST"),
    "g_rs64_g1e_pcache": (FN, "latch of ROGUESQ_G1E_PROVCACHE (default 0)"), "g_rs64_g1e_hgather": (FN, "latch of default-on ROGUESQ_G1E_HGATHER"),
    "g_rs64_bf_fast": (SC, "s7028 bump fast-path op counter (one ++ per eligible command)"), "g_rs64_bf_slow": (SC, "s7028 slow-path counter"),
    "g_rs64_g1e_ranges": (SC, "deferred-range counter next to the functional emplace_back"),
    "g_rs64_bf_task_on": (FN, "per-task latch of the s7028 bump mode (static g_bf_mode)"),
    "g_rs64_bfsh_arm": (ENVG, "`else g_rs64_bfsh_arm = 0` store; the arm itself needs ROGUESQ_G1E_BUMPFAST_SH"),
    "g_rs64_g1e_batch": (FN, "per-task latch of default-on ROGUESQ_G1E_BATCH"), "g_rs64_g1e_cdiag": (FN, "latch of ROGUESQ_G1E_CDIAG (default 0)"),
    "g_rs64_aq_submit_calls": (ENVG, "every store is under g_rs64_aq_on 1/2/3 (ROGUESQ_G1E_AQ, main.cpp:7219; unset = 0 -> plain call)"),
    "g_rs64_aq_submit_ns": (ENVG, "g_rs64_aq_on 1/3"), "g_rs64_aq_commit_ns": (ENVG, "`if (g_rs64_aq_on != 1 && != 3) return` first"),
})
LATCH = "once"
for fn, why in {
    "submit_rdp_range": "each read is inside `if (s_x < 0)` (s_route, s_words, s_cmd_log, s_img, s_log, s_tc, s_dr) or `if (!s_bin_init)` / `s_bin_from < 0` / `s_bin_vi < 0`",
    "RT64Context": "constructor: once per process",
    "send_dl": "inside `if (s_lle_force < 0)`, `s_skip_hangar_probe < 0`, `s_lle_ungated < 0`, `s_lle_hangar_only < 0`, `s_lle_solo < 0`, `!s_dumped_ucode`, `!s_dumped_vtx`, `s_op_hist < 0`",
    "update_screen": "inside `if (s_sd < 0)` / `s_f < 0` latches, static initialisers, or the one-shot `!s_sd_sampled` stall sampler",
    "rs64_xtrace_mark": "inside `if (fz_ms < 0)` / `nspec < 0` / `npoke < 0` latches",
    "rs64_g1d_join_swap": "inside `if (enabled < 0)`",
    "enable_instant_present": "host hook called once at init (applies PresentEarly)",
    "g5b_tg_fix_init": "file-scope static initialiser + rs64_s7427_tg_fix_reinit (once per mission re-init)",
    "g5b_tg_open": "file-scope static initialiser (static FILE *g_g5b_tg = g5b_tg_open())",
    "rs64_bf_env": "called only from the static initialiser g_bf_diag",
    "rs64_m4_dma_probe": "inside `if (!init) { init = 1; ...}`",
    "rs64_s7427_tg_fix_reinit": "mission re-init only (not per task)",
    "rsp_dpc_submit_impl": "static const bool v = []{getenv}() initialiser (ROGUESQ_LOG_SEQ)",
    "rs64_dpc_defer_end_impl": "FIXED s7633: was a per-commit getenv(ROGUESQ_TRACE_DISPATCH); now a static latch",
}.items():
    c.FNCLASS[(fn, "getenv")] = (LATCH, why)
for fn, (cls, why) in {
    "rs64_rand_trace": ("gated", "returns unless s_rand_trace_f (ROGUESQ_RAND_TRACE)"),
    "rs64_xtrace_mark": ("gated", "prints only for the ROGUESQ_XTRACE_MEM spec list (nspec == 0 by default)"),
    "rs64_bolt_mark": ("gated", "s_rand_trace_f"), "rs64_guided_mark": ("gated", "s_rand_trace_f"),
    "rs64_hp_mark": ("gated", "s_rand_trace_f"), "rs64_bt_mark": ("gated", "s_rand_trace_f"),
    "flush_locked": ("gated", "stats flush of an env-armed counter set (print_locked family)"),
    "print_locked": ("gated", "stats dump of the env-armed load-diff counters; only reached from flush paths under their env"),
    "print2_locked": ("gated", "same family as print_locked"),
    "RT64Context": ("once", "constructor: once per process"),
    "send_dl": ("budget", "n<=8 || every 32nd/64th/128th task, ucode change, or under s_op_hist (ROGUESQ_LOG_OPCODE_HIST)"),
    "update_screen": ("budget", "one-shot (filter installed, stall sample), on VI width change, or every 64th/256th VI"),
    "submit_rdp_range": ("gated", "inside s_route/s_words/s_cmd_log/s_img/s_log/s_bin latches (ROGUESQ_LOG_RDP_*, LOG_G1D_*, RS64_RDP_BIN_PORT)"),
    "rs64_m4_y8000_summary": ("budget", "atexit / width or origin change / every 256th entry"),
    "rs64_g5b_trigen": ("gated", "per-swap summary of the ROGUESQ_G5B_TG trigen log"),
    "rs64_spike_scan": ("gated", "s_bd file (ROGUESQ_LOG_SPIKE dump) per swap; the default-on CULL_SPIKE work is functional"),
    "rs64_floor_cover_emit": ("gated", "ROGUESQ floor-cover diag (callers inside the floor walker's env gate)"),
    "rs64_i4_selftest": ("once", "self-test, one call per process"),
    "emit": ("gated", "member of the env-armed floor/cc summary struct; emit() on leave/width only"),
    "rs64_floor_mesh": ("gated", "floor walker family, env-gated (rs64_floor_scan gate)"),
    "rs64_floor_texel": ("budget", "tile_logged once / raws < 4"), "rs64_floor_note": ("budget", "draws++ == 0 / raws < 8, floor walker env gate"),
    "rs64_floor_scan": ("budget", "every 300th gated scan"),
    "should_drop_wrap_rdp": ("budget", "n <= 16 || every 1024th drop"),
    "rsp_dpc_submit_impl": ("budget", "n<=4 / every 4096th / 16384th / 64th / first 40 / power-of-two / one-shot dump"),
    "rs64_dpc_defer_end_impl": ("budget", "[dpc-merge] every 64th commit, [s4280-tot] every 4096th"),
}.items():
    c.FNCLASS[(fn, "print")] = (cls, why)

c.CLASS.update({
    "g_inline_probe": (SC, "per-task `= {}` reset of a small fixed struct in rs64_e9prov_task_begin"),
    "s_skip_hangar_probe": (LATCH, "latch store inside `if (s_skip_hangar_probe < 0)`"), "s_op_hist": (LATCH, "latch store inside `if (s_op_hist < 0)`"),
    "s_dumped": ("gated", "inside `if (s_cmd_log)` (ROGUESQ_LOG_G1D_CMD), <= 70 dumps"),
    "dumped": ("gated", "rs64_floor_note returns at once without ROGUESQ_LOG_FLOOR (s6934)"),
    "s4283Shown": ("gated", "loop runs only in the `else` arm of `if (!g_rs64_g1e_cdiag)` (ROGUESQ_G1E_CDIAG, default 0)"),
})
for (fn, k), v in {
    ("run_rdp_submission", "print"): ("gated", "inside `#ifdef _WIN32` __except handler (not compiled on macOS)"),
    ("rs64_g1e_bc_check", "print"): ("gated", "`if (!g_bc_on) return` (ROGUESQ_G1E_BATCH_CHECK)"),
    ("rs64_m4_dma_probe", "print"): ("gated", "inside `if (cnt && ...)`; cnt set only from ROGUESQ_G3C_DMALOG"),
    ("rs64_frame_trig_lb", "print"): ("budget", "[lbspan] one start/end line per letterbox span (gaps >= 30 swaps), not per frame"),
    ("rs64_bf2_flush", "print"): ("gated", "inside `if (g_bf_check_flag())` (ROGUESQ_G1E_BUMPFAST_CHECK)"),
    ("rs64_floor_note", "print"): ("gated", "returns at once without ROGUESQ_LOG_FLOOR (s6934)"),
}.items(): c.FNCLASS[(fn, k)] = v

# s7657: rows the live tree grew after s7633 closed (s7634-s7636 walker-fusion work), read by hand when the fresh-input sweep
# mode first ran (frozen scratch/s7633 json had hidden them).
c.CLASS.update({
    "g_s7634_sink": (ENVG, "written only in rs64_s7634_nullwalk, called only `if (s7634null)` (ROGUESQ_S7634_NULLWALK latch)"),
    "g_s7636_odd": (SC, "one bool store per submit: GLUE_TOG parity (false unless ROGUESQ_GLUE_TOG) read by FASTSPIKE=tog"),
})
c.FNCLASS[("rs64_region_scan", "print")] = ("gated", "[s7635-late]/[s7635-chk] only past `if (fused == 1) return`: fused=2/3 "
                                            "need ROGUESQ_S7634_FUSE=chk|inj (default 1); late lines also <=32")
# s7926: rows the s7891-s7896 RAND_TRACE work added in rt64_render_context.cpp (surfaced when an s7324_rcp_spill.cpp edit
# invalidated the sweep cache). Read by hand: both functions are reached ONLY from tools/fixup_rand_trace.py hooks, every one
# wrapped in `if (__builtin_expect(g_rs64_rand_trace, 0))` (ROGUESQ_RAND_TRACE; fixup_rand_trace.py lines 11/71/73/88/264).
_RT = "only called from fixup_rand_trace.py hooks under `if (g_rs64_rand_trace)` (ROGUESQ_RAND_TRACE)"
c.FNCLASS[("rs64_rand_trace", "getenv")] = (ENVG, _RT)
c.CLASS.update({"s_s7896_rdram": (ENVG, "rs64_xtrace_mark: " + _RT), "rs64_s7891_reset": (ENVG, "rs64_xtrace_mark: " + _RT),
                "rs64_s7895_dtpc": (ENVG, "rs64_xtrace_mark: " + _RT)})
c.FRESH.update(d="scratch/s7633", gen_args=("--hot", "src/rsp/dpc_bridge.cpp,src/main/rt64_render_context.cpp"),
               scope=("src/", "lib/rt64/", "lib/N64ModernRuntime/"))  # s7657: no-arg sweep mode, the s7633 --hot set

if __name__ == "__main__":
    c.main()
