#!/usr/bin/env python3
"""s7599 class GR: long-lived host containers that grow once per GUEST event and are never cleared, capped or evicted.

Scope: src/, librecomp/src, ultramodern/src, lib/rt64/src (skips tests/tools/contrib/examples/demos/gui), // comments stripped.
Growth op: <recv>(.|->)push_back|emplace_back|emplace|insert|try_emplace|push_front|emplace_front(.
Unit of classification: (file, receiver identifier).  Receiver = the identifier right before the op (g_e9prov.x -> x).
Verdict prefixes:
  local     function-scoped or per-call container (dies at return)
  scoped    per-frame / per-workload / per-call member, cleared or reset at that boundary (the clear is named)
  bounded   run-lifetime, but capped (cap named) or keyed by a bounded domain (domain named)
  host      grows only on host events (boot, config, env parse, user action, thread creation)
  gated     env-gated diagnostic, off in the owner recipe (gate named)
  grow      run-lifetime, ungated, grows per guest event with no bound  -> a defect row (must be 0)
Rules: FILES[file] covers every NON-static receiver of that file (upstream RT64 per-workload code); a receiver that the
scanner sees declared `static`/`thread_local` ALWAYS needs its own ROW.  Every other (file, receiver) needs a ROW, else OPEN.
--controls: (1) plant `static std::vector<uint32_t> s_gr_plant; ... s_gr_plant.push_back(rdram_word)` in a copy of
rt64_state.cpp -> must be OPEN; (2) drop one ROW -> its receiver must be OPEN; (3) plant the same static in a FILES-ruled file
(rt64_rsp.cpp) -> must still be OPEN (statics are never file-covered).  Exit 0 only if 0 open + 0 grow + 0 stale + 3/3 controls.
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIRS = ["src", "lib/N64ModernRuntime/librecomp/src", "lib/N64ModernRuntime/ultramodern/src", "lib/rt64/src"]
SKIP = re.compile(r"/(tests?|tools|contrib|examples?|demos?|gui)/")
EXT = (".cpp", ".cc", ".c", ".h", ".hpp", ".mm")
OP = re.compile(r"([A-Za-z_]\w*)(\[[^\]]*\])?(\.|->)(push_back|emplace_back|emplace|insert|try_emplace|push_front|emplace_front)\(")
WL = "scoped: upstream RT64 per-workload/per-frame container, reset by Workload::reset/begin or the frame's clear (LK s7585/s7586: RT64 memory flat after warm-up)"
FILES = {
    "rt64/src/hle/rt64_rsp.cpp": "scoped: Workload drawData/rawData vectors, reset per workload (rt64_workload.cpp reset)",
    "rt64/src/hle/rt64_workload.cpp": "scoped: the workload reset/merge itself",
    "rt64/src/hle/rt64_workload_queue.cpp": WL,
    "rt64/src/hle/rt64_framebuffer_manager.cpp": WL,
    "rt64/src/hle/rt64_game_frame.cpp": "scoped: GameFrame scene/projection/match vectors rebuilt per frame (local maps passed by reference)",
    "rt64/src/hle/rt64_light_manager.cpp": WL,
    "rt64/src/hle/rt64_framebuffer_storage.cpp": "bounded: handle vector, one slot per live framebuffer (freed handles reused)",
    "rt64/src/render/rt64_framebuffer_renderer.cpp": WL + "; g_depthEvents capped 8192 and depthDirOn()-gated",
    "rt64/src/render/rt64_texture_cache.cpp": "bounded: upstream texture cache with unused-list eviction (evictedTextures, LK s7585 flat); replacement paths host",
    "rt64/src/render/rt64_buffer_uploader.cpp": WL,
    "rt64/src/render/rt64_render_target.cpp": "scoped: barrier vectors per call",
    "rt64/src/render/rt64_look_at_processor.cpp": WL,
    "rt64/src/render/rt64_projection_processor.cpp": WL,
    "rt64/src/render/rt64_tile_processor.cpp": WL,
    "rt64/src/render/rt64_transform_processor.cpp": WL,
    "rt64/src/render/rt64_native_target.cpp": "bounded: read/write buffer history grows only to the in-flight history count",
    "rt64/src/render/rt64_raster_shader.cpp": "host: shader spec constants / pipeline thread list",
    "rt64/src/render/rt64_raster_shader_cache.cpp": "host: compilation thread list",
    "rt64/src/render/rt64_shader_compiler.cpp": "host: compiler argument list",
    "rt64/src/preset/rt64_preset_draw_call.cpp": "bounded: material cache keyed by preset hashes, cleared on preset reload",
    "rt64/src/preset/rt64_preset_light.cpp": "host: preset JSON",
    "rt64/src/preset/rt64_preset.h": "host: preset JSON",
    "rt64/src/preset/rt64_preset_inspector.h": "host: preset library (inspector)",
    "rt64/src/common/rt64_replacement_database.cpp": "host: replacement pack database (none shipped)",
    "librecomp/src/mods.cpp": "host: mod scan (no mods shipped)",
    "librecomp/src/mod_manifest.cpp": "host: mod manifest",
    "librecomp/src/mod_hooks.cpp": "host: hook tables",
    "librecomp/src/mod_events.cpp": "host: event callbacks registered at mod load",
    "librecomp/src/patcher.cpp": "host: BPS patch",
    "librecomp/src/overlays.cpp": "host: overlay tables built at boot from the recompiled section list",
}
# (file suffix) -> {receiver: verdict}
G = lambda env: "gated: " + env + " (off in the owner recipe)"
ROWS = {
    "src/rsp/dpc_bridge.cpp": {
        "o": G("g_bc_on per-bump reference check"), "k": "local: per-check key list",
        "ev": "gated: ROGUESQ_DLWALK, capped 6000",
        **{r: "gated: g_e9prov provenance (ROGUESQ_LOG_M4_PORT_RDRAM / log_e9_provenance)" for r in
           ("m4_norm_rows", "reset_route_first", "reset_route_last", "reset_reuse_first", "reset_reuse_last", "frame_first",
            "frame_last", "frame_slot_first", "spanned_addrs", "conditions", "fetched_addrs", "emitted_addrs")},
        "ord": "local: ROGUESQ_G5B_FRAME_TRIG_LB ring order", "s_flight": G("ROGUESQ_LOG_G1D_RECT"),
        "g_rs64_g1d_walk": G("ROGUESQ_G1D_SPRITE_DIAG"), "g_rs64_g1d_walk_cw": G("ROGUESQ_G1D_SPRITE_DIAG"),
        "shIdx": "local: ROGUESQ_WRAP_MERGE_CHECK index", "cc_sp": G("cc_on wrap census"), "cc_pre": G("cc_on wrap census"),
        "cc_exp": G("cc_on wrap census"), "wm_undo": G("cc_on wrap census"), "wm_live": G("cc_on wrap census"),
        "wm_chk": G("s_wm_chk watermark"),
        "g_deferred_ranges": "scoped: s4272 deferred submit ranges, cleared at every flush (dpc_bridge clear sites 6885/8109/8164/8330)",
        "g_s4272_shadow": "scoped: s4272 shadow bytes, cleared with g_deferred_ranges at flush; ROGUESQ_S4272_CAP bounds a batch",
        "g_s4272_sh": "scoped: cleared with g_deferred_ranges at flush", "g_bc_ranges": G("g_bc_on per-bump lists"),
        "g_bc_sh": G("g_bc_on"), "g_bc_shadow": G("g_bc_on"),
    },
    "src/rsp/s7096_fwd_cover.cpp": {r: G("ROGUESQ_S7096_FWD") for r in ("ex", "hw", "snap", "pend", "miss", "drops")},
    "src/rsp/s7097_edit_census.cpp": {"g_cmds": G("s7097 edit census")},
    "src/rsp/s7331_reset_writer.cpp": {r: G("rs64_s7331_on") for r in ("all", "g_fin", "g_act")},
    "src/rsp/s7521_ucode_watch.cpp": {r: G("rs64_s7521_on") for r in ("seen_off", "tuples", "src28")},
    "src/rsp/s7523_slow_rdp.cpp": {r: G("s7523 slow-RDP witness") for r in ("snap", "tch", "sg", "q")},
    "src/main/main.cpp": {
        "g_rs64_local_symtab": "host: nm symbol table read once at boot", "s_dumped": G("dump `on` flag"),
        "g_s7496_imgs": G("s7495_on"), "g_s7499_pairs": G("s7495/s7499"), "k": G("s7503_on"), "g_s7503": G("s7503_on; trimmed >3000"),
        "col": G("budgeted image dump `on`"), "img": G("budgeted image dump `on`"), "h": "local: lambda parameter",
        "keep": G("s7503_on trim"), "g_s7500": G("ROGUESQ_S7500_EY"), "v": "local: sort scratch",
        "g_plants": "scoped: cleared per check (main.cpp g_plants.clear())", "spans": "bounded: capped 16",
        "glk": "bounded: capped 256", "g_prevW": "bounded: capped 64", "s": "local: name builder", "cur": G("ROGUESQ_LOG_GRIDSPAWN"),
        "s_tanks": G("ROGUESQ_LOG_GRIDSPAWN"), "q": "bounded: s6979se stderr queue drained by the writer, input dropped past 256 MB queued",
        "tags": "bounded: log rate-limit map keyed by log tag string (finite tag set in the binary)", "at": "host: env list parse",
    },
    "src/main/rt64_render_context.cpp": {
        "fz": "host: ROGUESQ_POSE_FREEZE parse", "fzd": "host: ROGUESQ_POSE_FREEZE parse",
        "s_menu_fifo": "bounded: menu completion FIFO capped 64 (pop_front) and drained by the reader",
        "pool": "bounded: async-RDP buffer pool, one per in-flight job (jobs bounded by the queue)",
        "q": "bounded: async-RDP job queue, consumed by the worker", "w": "local: job payload",
        "g_rs64_g1d_ci_frame": "bounded: capped 64 per frame",
    },
    "src/main/upstream_compat.cpp": {
        "s7239_el": G("ROGUESQ_DD_WIDEWIN_MERGE"), "s7239_key": G("ROGUESQ_DD_WIDEWIN_MERGE"), "s7239_l": G("ROGUESQ_DD_WIDEWIN_MERGE"),
        "seen": "bounded: capped 256", "s_s5041_freed": G("ROGUESQ_FREE_CENSUS"), "s_s7325_ord": G("rs64_s7324_on"),
        "s_s7325_freed": G("rs64_s7324_on"), "s_s7472_seen": G("ROGUESQ_S7472_HEAPCHK"), "s_s7475_seen": G("ROGUESQ_S7475_CANARY"),
        "keep": G("s7478/s7480 UAF watch"), "v": "local: range scratch", "s_s7519_dmaA": "gated: s7518/s7519 cache-shape witness, capped 65536",
        "s_s7519_ctlln": G("ROGUESQ_CACHE_SHAPE_CTL_WB"), "s_s7519_set": G("s7518/s7519 cache-shape witness"),
        "s_s7545_thr": G("ROGUESQ_S7545_THRWATCH"), "s_s7545_tc": G("ROGUESQ_S7545_THRWATCH"), "bl": "local: s7777_sweep per-sweep heap block list", "s_s7777_sr": G("ROGUESQ_S7777_DANGLE"), "big": G("s6063_on"),
        "cur": "local: capped 4096 chain walk", "s_s6558_blocks": "bounded: spill-arena bump blocks, total bytes <= the arena cap",
        "lst": "host: ROGUESQ_SPILL_FORCE parse", "s_s6702_free": G("s6702 free-list `on`"), "s7331_q": G("rs64_s7331_on"),
        "by": "gated: fill aggregator, tls->live only under its diagnostic; keyed by (pc,value)", "out": G("rs64_g1d_blk_enabled"),
        "s_s7333_keys": "bounded: keyed by guest heap carve address (<= one per 16-byte heap slot in 8 MB), default-on s7333 keep",
        "s7331_t": G("rs64_s7331_on"), "um": "local: heap walk scratch", "order": "gated: s4899_on, capped 40",
        "tags": "bounded: s4916 tag strings keyed (pc, byte, value): finite pc set x 16 x 256 (fixup-applied mark)",
        "c": "bounded: s6963 template-pointer set, cleared on cell-pool base change (level load); S6963U (map) is mode 2 only, "
             "default mode 3 uses S6963F whose key table is held <= 65536 by rev[] (s7024)",
    },
    "librecomp/src/ai.cpp": {"distinct": G("ROGUESQ_S4239")},
    "librecomp/src/recomp.cpp": {"game_roms": "host: registered at startup", "valid_game_roms": "host: ROM scan"},
    "librecomp/src/rsp.cpp": {
        "g_audio_image_stages": "gated: audio-join probe (ROGUESQ_LOG_PCM_BOUNDARY), capped 8192",
        "g_audio_image_sources": "gated: audio-join probe, capped 8192", "ranges": "local: per-task DMA range list",
        "g_audio_join_tasks": "gated: audio DMA probe (ROGUESQ_LOG_PCM_BOUNDARY path)", "g_audio_join_pcm": G("ROGUESQ_LOG_PCM_BOUNDARY"),
    },
    "ultramodern/src/events.cpp": {
        "buf": G("ROGUESQ_G1E_THREADS sampler"), "known": G("ROGUESQ_G1E_THREADS sampler; capped 65535"), "nb": G("ROGUESQ_G1E_THREADS"),
        "symd": G("ROGUESQ_G1E_THREADS"), "v": "host: ROGUESQ_DD_ADDRS parse", "orig_r": "bounded: one per parsed address, once",
        "io": "bounded: one per parsed address, once",
        "ends": G("ROGUESQ_AI_VI_CLOCK=3") + "; s7867 AI DMA queue, one entry per queued buffer, popped by the AI DMA thread at each DMA end",
    },
    "ultramodern/src/extensions.cpp": {"pending_events": "scoped: DL event list drained each dispatch"},
    "ultramodern/src/mesgqueue.cpp": {
        "g_audio_sp_deliveries": "gated: audio_sp_row_enabled", "seen": "bounded: capped 64",
        "requeued_messages": "local: per-dispatch requeue list"},
    "ultramodern/src/threads.cpp": {"g_live_ctx": "host: one per live thread context, erased at thread exit", "v": "local: report scratch"},
    "ultramodern/src/timer.cpp": {"active_timers": "bounded: guest OSTimer set, erased on stop/fire (5 erase sites); one entry per live timer",
                                   "seen": "local: CheckTimerAction dedupe"},
    "rt64/src/gbi/rt64_gbi_f3dfactor5.cpp": {"s_seen": "gated: gbi_log_enabled (insert short-circuits behind it)",
                                             "s_seenDims": G("ROGUESQ_LOG_CIMG")},
    "rt64/src/gbi/rt64_gbi_rdp.cpp": {"s_lscSeen": "gated: ROGUESQ_LOG_DEPTH_PAIR, capped 2000", "triPointers": G("ROGUESQ_LOG_E9_DISPATCH")},
    "rt64/src/hle/rt64_framebuffer.cpp": {"s7463Raw": "gated: rs64_s7463_mode bit 2, capped 4M", "s7463Fix": "gated: rs64_s7463_mode bit 2, capped 4M"},
    "rt64/src/hle/rt64_framebuffer_pair.cpp": {"s_skip": "host: ROGUESQ_SKIP_CC parse"},
    "rt64/src/hle/rt64_present_queue.cpp": {"at": "host: env schedule parse", "drawSemaphores": "bounded: <= swap-chain texture count"},
    "rt64/src/hle/rt64_rdp.cpp": {
        "drawFbOperations": "scoped: State fb operations, consumed per flush", "seen": G("ROGUESQ_LOG_TEXFMT/ROGUESQ_DUMP_HANGAR_TEX"),
        "dump_seen": G("ROGUESQ_DUMP_HANGAR_TEX"), "commandWarnings": "scoped: workload warnings, reset per workload",
        "loadOperations": "scoped: workload drawData", "seenKeys": "bounded: capped 64", "triPosFloats": "scoped: workload drawData",
        "triTcFloats": "scoped: workload drawData", "triColorFloats": "scoped: workload drawData", "ranges": G("ROGUESQ_TRI_KEEP")},
    "rt64/src/hle/rt64_rdp_tmem.cpp": {"hashSet": "bounded: uploaded-hash set, erased by removeHashes when the texture cache evicts",
                                       "dumpedSet": "gated: texture dump directory set by the user (empty in the owner recipe)"},
    "rt64/src/hle/rt64_state.cpp": {
        "bandSources": "gated: band_wb_enabled, capped 8", "out": "gated: band_wb_enabled", "samples": "gated: band_wb_enabled",
        "seen": G("ROGUESQ_LOG_DRAWTEX"), "byDelta": G("ROGUESQ_DRAWTEX_HIST"), "startFbOperations": "scoped: fbPair ops per frame",
        "commandWarnings": "scoped: workload", "rdpParams": "scoped: workload drawData", "renderParams": "scoped: workload drawData",
        "resizedTargets": "scoped: per frame", "bufferUploaders": "bounded: one per worker, grown to the in-flight count",
        "pre": G("ROGUESQ_WB_COL_PROBE"), "colorDepthPairs": "scoped: per frame", "pointLights": "scoped: workload",
        "extraParams": "scoped: workload drawData", "colorImageAddressSet": "scoped: thread_local, cleared each call",
        "replacementDirectories": "host: user loads a texture pack", "startFbDiscards": "scoped: fbPair per frame",
        "returnAddressStack": "bounded: DL call stack, pushed on G_DL and popped on G_ENDDL (depth of the guest DL nest)",
        "spriteCommands": "scoped: workload"},
    "rt64/src/hle/rt64_game_frame.cpp": {"matchCandidates": "scoped: thread_local, cleared each call"},
    "rt64/src/render/rt64_raster_shader.cpp": {"specConstants": "host: thread_local spec-constant table filled once (specConstantsSetup)"},
    "librecomp/src/mod_hooks.cpp": {"hook_contexts": "bounded: hook context stack, popped on hook return (depth of nested hooks; no mods shipped)"},
    "librecomp/src/overlays.cpp": {
        "reported": G("ROGUESQ_STUB_MISSING_FUNCS"), "base_events": "host: built at boot from recompiled tables",
        "base_exports": "host: boot tables", "ext_base_exports": "host: boot tables", "loaded_sections": "bounded: s7528 evicts the stale entry on every overlay swap (default on; =0 restores the old one-per-swap growth), one per loaded "
        "section, removed on unload (finite section list)", "manual_patch_symbols_by_vram": "host: boot tables",
        "patch_code_sections_by_rom": "host: boot tables"},
}

# s7655: G6a rumble, G6b bindings, G6c stand-ins, s7644 instrument.
for _k, _v in {
    "src/main/main.cpp": {"g_rumble_edges": "bounded: G6a motor edge deque, popped to 512 in set_rumble and aged out (2x100 ms) in rs64_rumble_duty",
        "buttons": "bounded: G6b rs64_bind_apply, one push per F6-panel bind keypress, identical (mask, src) rejected",
        "d": "bounded: G6b direction key list, one push per F6 bind keypress, duplicate scancode rejected"},
    "src/main/rs64_settings.cpp": {"from_file": "local: s7663 rs64_settings_apply settings-file (name, value) list, one per file line",
        "keep": "local: s7663 rs64_settings_apply argv pass-through list (<= argc)"},
    "src/main/rs64_bindings.h": {"buttons": "bounded: rs64_bind_defaults fixed built-in list"},
    "src/main/rs64_bindings_json.h": {"keep": "local: per-button list in rs64_bind_parse_json", "l": "local: rs64_bind_to_json list",
        "v": "local: per-direction key list in rs64_bind_parse_json"},
    "src/main/rs64_standins.cpp": {"s_q_ours_mtx": G("ROGUESQ_STANDINS + STANDINS_LOG/PULL/CTL (rs64_sg_probe)") + "; < 4096, cleared at each queue reset",
        "s_standins": "bounded: ROGUESQ_STANDINS (opt-in); cleared at every rebuild, i < 4096 items",
        "s_gh_idx": "bounded: ROGUESQ_STANDINS (opt-in); cleared at the top of every submit pass, at most one push per stand-in (<= s_standins.size() < 4096) (s7677 row)",
        "s_pseen": "bounded: ROGUESQ_STANDINS + STANDINS_LOG (s_bk_log); insert only while size() < 2000 (s7685 log dedupe, row s7690)"},
    "src/rsp/s7644_rspdma.cpp": {r: G("ROGUESQ_S7644_RSPDMA&2") for r in ("g_gpi", "g_gstale", "g_srcc", "g_srcs", "v")},
    "src/rsp/s7751_task_snap.cpp": {"rdp": G("ROGUESQ_S7751_SNAP") + "; cleared at every task begin, < 16 MB per task"},
}.items():
    ROWS.setdefault(_k, {}).update(_v)

def scan(files_override=None):
    sites = {}  # (relfile, recv) -> [line, static?]
    for d in DIRS:
        for r, _, fs in os.walk(os.path.join(ROOT, d)):
            for f in fs:
                p = os.path.join(r, f); rel = os.path.relpath(p, ROOT)
                if SKIP.search("/" + rel) or not f.endswith(EXT): continue
                src = files_override.get(rel) if files_override and rel in files_override else open(p, errors="ignore").read()
                L = [l.split("//")[0] for l in src.split("\n")]; txt = "\n".join(L)
                for i, l in enumerate(L):
                    for m in OP.finditer(l):
                        v = m.group(1); key = (rel, v)
                        if key not in sites:
                            st = bool(re.search(r"\b(static|thread_local)\b[^;\n]*\b%s\b\s*(\[[^\]]*\])?\s*[;={(]" % re.escape(v), txt))
                            cl = False
                            if st:  # auto rule: per-call static/thread_local scratch cleared within 6 lines of its declaration
                                for j, dl in enumerate(L):
                                    if re.search(r"\b(static|thread_local)\b[^;]*\b%s\b" % re.escape(v), dl) and \
                                       any(re.search(r"\b%s\.clear\(\)" % re.escape(v), x) for x in L[j + 1:j + 7]):
                                        cl = True; break
                            sites[key] = [i + 1, st, cl]
    return sites

def suffix(rel, table):
    for k in table:
        if rel.endswith(k): return k
    return None

def classify(sites, rows):
    out, used = [], set()
    for (rel, v), (ln, st, cl) in sorted(sites.items()):
        fk = suffix(rel, rows); verdict = None
        if fk and v in rows[fk]: verdict = rows[fk][v]; used.add((fk, v))
        elif cl: verdict = "scoped: static/thread_local scratch, .clear() within 6 lines of its declaration (auto)"
        elif not st:
            ff = suffix(rel, FILES)
            if ff: verdict = FILES[ff]
        out.append((rel, v, ln, st, verdict))
    stale = [(f, v) for f in rows for v in rows[f] if (f, v) not in used]
    return out, stale

def report(out, stale, quiet=False):
    op = [o for o in out if o[4] is None]; gr = [o for o in out if o[4] and o[4].startswith("grow")]
    if not quiet:
        from collections import Counter
        c = Counter((o[4] or "OPEN").split(":")[0] for o in out)
        print("s7599 GR census: receivers=%d (static=%d) %s" % (len(out), sum(o[3] for o in out), " ".join("%s=%d" % kv for kv in sorted(c.items()))))
        for o in op: print("  OPEN %s:%d %s%s" % (o[0], o[2], o[1], " [static]" if o[3] else ""))
        for s in stale: print("  STALE row %s %s" % s)
    return len(op), len(gr), len(stale)

def controls():
    ok = 0
    st = "lib/rt64/src/hle/rt64_state.cpp"; rs = "lib/rt64/src/hle/rt64_rsp.cpp"
    plant = "\nstatic std::vector<uint32_t> s_gr_plant;\nvoid s_gr_plant_fn(uint32_t w) { s_gr_plant.push_back(w); }\n"
    for i, f in enumerate((st, rs)):
        srcs = {f: open(os.path.join(ROOT, f)).read() + plant}
        out, _ = classify(scan(srcs), ROWS)
        hit = any(o[0] == f and o[1] == "s_gr_plant" and o[4] is None for o in out)
        print("  control %d plant static in %s -> %s" % (1 if i == 0 else 3, f.split("/")[-1], "OPEN (caught)" if hit else "MISSED"))
        ok += hit
    import copy
    rows = copy.deepcopy(ROWS); del rows["src/main/upstream_compat.cpp"]["s_s7333_keys"]
    out, _ = classify(scan(), rows)
    hit = any(o[1] == "s_s7333_keys" and o[4] is None for o in out)
    print("  control 2 drop row s_s7333_keys -> %s" % ("OPEN (caught)" if hit else "MISSED")); ok += hit
    return ok

if __name__ == "__main__":
    out, stale = classify(scan(), ROWS)
    n_open, n_grow, n_stale = report(out, stale)
    rc = 0 if (n_open == 0 and n_grow == 0 and n_stale == 0) else 1
    if "--controls" in sys.argv:
        k = controls(); print("controls %d/3" % k)
        if k != 3: rc = 1
    print("verdict: open=%d grow=%d stale=%d -> %s" % (n_open, n_grow, n_stale, "CLOSED" if rc == 0 else "NOT CLOSED"))
    sys.exit(rc)
