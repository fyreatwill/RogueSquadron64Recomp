"""Rule table for tools/s7542_gc_census.py (class GC: host writes into guest RAM vs the signal that tells the guest).
Each rule: (file suffix, enclosing function, (lo, hi) line range | None, [(mode, class, why, checks)]).
Extra check kinds (on top of tools/s7538_gb_census.py run_checks):
  ("near", rx, n)      rx occurs in the n characters of the function body before the site (env gates of diag blocks)
  ("noptrwrite",)      the site is a pointer local (idiom ptr) and the function never stores through that name
"""
import re
import s7538_gb_census as gb

OK = {"H-before", "H-guest-thread", "H-init", "H-late-noreader", "H-lever", "H-latent-FIXED(opt-in)", "H-diag", "H-def",
      "not-guest", "read-alias", "H-dead", "H-os-private"}

EVP = "lib/N64ModernRuntime/ultramodern/src/events.cpp"
PIP = "lib/N64ModernRuntime/librecomp/src/pi.cpp"
RCP = "src/main/rt64_render_context.cpp"
MNP = "src/main/main.cpp"
OPT = "docs/OWNER-OPT-INS.md"

_orig = gb.run_checks


def run_checks(site, checks, over, lib):
    plain = [c for c in checks if c[0] not in ("near", "noptrwrite")]
    fails = _orig(site, plain, over, lib)
    for c in checks:
        if c[0] == "near":
            ok = re.search(c[1], site["body"][max(0, site["off"] - c[2]):site["off"]]) is not None
        elif c[0] == "noptrwrite":
            m = re.match(r'[\w:]+\s*\*\s*(\w+)\s*=', site.get("text", ""))
            n = m.group(1) if m else None
            body = re.sub(r'[\w:]+\s*\*\s*%s\s*=' % re.escape(n), 'DECL =', site["body"]) if n else ""
            ok = n is not None and re.search(
                r'(?:\b%s\s*(?:\[[^]]*\])+\s*(?:[-+|&^]?=(?!=)|\+\+|--)|\*\s*%s\s*(?:[-+|&^]?=(?!=))|\b%s\s*->\s*\w+(?:\.\w+|\[[^]]*\])*\s*(?:[-+|&^]?=(?!=)|\+\+|--)'
                r'|\b(?:memcpy|memset|memmove)\s*\(\s*%s\b)' % ((re.escape(n),) * 4), body) is None
        else:
            continue
        if not ok:
            fails.append(":".join(str(x) for x in c)[:90])
    return fails


gb.run_checks = run_checks


def G(f, fn, imp=None, why="", extra=()):
    """guest-thread: a libultra replacement the game imports (nm -u) -> runs on the calling guest thread, synchronously"""
    imp = imp or fn
    return (f, fn, None, [("guest", "H-guest-thread", why or ("%s runs on the calling guest thread (game imports %s)" % (fn, imp)),
                           [("nm_present", imp)] + list(extra))])


def D(f, fn, env, rng=None, n=4000, why="", cls="H-diag"):
    """env-gated diagnostic / harness writer: the env name must appear in the n chars before the site"""
    # s7653: a given line range is replaced by the env text anchor itself (line ranges drifted: 17 sites UNCLASSIFIED)
    if rng is not None:
        rng = ("near", env, n)
    return (f, fn, rng, [("diag", cls, why or ("only under %s (off by default)" % env), [("near", env, n)])])


def A(f, fn, rng=None, why="read-only pointer (dump / log / compare); no store through it in the function"):
    return (f, fn, rng, [("alias", "read-alias", why, [("noptrwrite",)])])


def DEAD(f, fn, imp):
    return (f, fn, None, [("dead", "H-dead", "the game does not import %s" % imp, [("nm_absent", imp)])])


L, U, T = "librecomp/src/", "ultramodern/src/", "lib/rt64/src/"
GFX_EARLY = ("early", "H-latent-FIXED(opt-in)",
             "F5 gfx LLE DMEM->RDRAM writes: default early sp_complete (class GA) posts SP-done before send_dl runs the LLE, so "
             "these land after the signal; consequence measured s7536 (no geometry change, H-colour-only, same-run A/B covering the "
             "whole ordering); fix ROGUESQ_SP_LATE=1 (owner opt-in)",
             [("fnbody", EVP, "gfx_thread_func", r"if \(!s7535_late\) sp_complete\(\)"), ("file", OPT, r"ROGUESQ_SP_LATE=1")])
GFX_LATE = ("late", "H-before", "ROGUESQ_SP_LATE=1: sp_complete after send_dl returned (the LLE and every DMA write ran inside it)",
            [("fnbody", EVP, "gfx_thread_func", r"send_dl\(&task_action->task\);[\s\S]*if \(s7535_late\) sp_complete\(\)")])
GFX = [GFX_EARLY, GFX_LATE]
WB_SYNC = ("sync", "H-before", "default (RDP_ASYNC off): RT64 fullSync runs inside send_dl on the gfx thread; dp_complete follows send_dl",
           [("fnbody", EVP, "gfx_thread_func", r"send_dl\(&task_action->task\);[\s\S]*dp_complete\(\)")])
WB_DRAIN = ("drained", "H-before", "ROGUESQ_RDP_ASYNC=1 without NODRAIN: rs64 task_exit drains the RT64 worker before dp_complete",
            [("file", RCP, r"rdpq::drain\(\); if \(rdpq::task_async\)")])
WB_NODRAIN = ("nodrain", "H-late-noreader",
              "ROGUESQ_RDP_ASYNC=1 NODRAIN=1|3: ~84% of writebacks land after dp_complete (s7541). WBW page-protect census "
              "(ROGUESQ_G1E_WBW + _CTL): s6938 (L1 default) and s7541_wbw_rwait under NODRAIN=3 (L4/L12 dd4, L1 dd8 21:9, ctl fired): "
              "flight readers are only RT64's own XXH3 in State::updateScreen (VI hash) and copyRAMToNativeAndChanges; 0 guest readers",
              [("file", MNP, r"ROGUESQ_G1E_WBW_CTL"), ("file", OPT, r"ROGUESQ_RDP_NODRAIN=3")])

RULES = [
    # --- RSP DMA -------------------------------------------------------------------------------------------------------------
    ("rsp.hpp", "<file>", None, [("def", "H-def", "DO_DMA_WRITE macro / dma_dmem_to_rdram definition: ordered at each ucode call site", [])]),
    ("rsp.hpp", "dma_dmem_to_rdram", None, [("def", "H-def", "the DMEM->RDRAM copy primitive", [])]),
    ("factor5_ucode_b_recompiled.c", "factor5_ucode_b", None, [("audio", "H-before",
     "audio (MusyX) ucode: run_task runs it synchronously on the SP task thread, then sp_complete",
     [("fnbody", EVP, "task_thread_func", r"run_task\(PASS_RDRAM task\)[\s\S]*sp_complete\(\)")])]),
    ("factor5_ucode_recompiled.c", "factor5_ucode", None, GFX),
] + [("factor5_ucode_ovl%s_recompiled.c" % o, "factor5_ucode_ovl%s" % o, None, GFX)
     for o in ("4", "10", "12", "14", "18", "1c", "20", "24", "2c")] + [
    # --- RT64 ----------------------------------------------------------------------------------------------------------------
    ("rt64_framebuffer.cpp", "<file>", None, [("def", "H-def", "copyNativeToRAM definition (call sites in fullSync)", [])]),
    ("rt64_framebuffer.h", "<file>", None, [("def", "H-def", "copyNativeToRAM declaration", [])]),
    ("hle/rt64_state.cpp", "fullSync", ("near", "ROGUESQ_RI_CLEAR", 600), [("diag", "H-diag", "ROGUESQ_RI_CLEAR read-in clear (s6249)", [("near", "ROGUESQ_RI_CLEAR", 600)])]),
    ("hle/rt64_state.cpp", "fullSync", ("near", "ROGUESQ_WB_CLEAR", 600), [("diag", "H-diag", "ROGUESQ_WB_CLEAR (s6246)", [("near", "ROGUESQ_WB_CLEAR", 600)])]),
    ("hle/rt64_state.cpp", "fullSync", ("near", "ROGUESQ_S7704_POISON", 900), [("diag", "H-diag", "s7707: ROGUESQ_S7704_POISON magenta fill (s7704), default off", [("near", "ROGUESQ_S7704_POISON", 900)])]),
    ("hle/rt64_state.cpp", "fullSync", ("line", r"copyNativeToRAM\("), [WB_SYNC, WB_DRAIN, WB_NODRAIN]),
    ("gbi/rt64_gbi.cpp", "getGBIForUCode", None, [("alias", "read-alias", "ucode text scan (read)", [("noptrwrite",)])]),
    ("mupen64plus-core/src/device/rdram/rdram.c", "poweron_rdram", None, [("own", "not-guest",
     "mupen64plus-core's own rdram device struct (regs/dram) inside RT64 contrib, not the port's guest RDRAM", [("body", r"rdram->dram")])]),
    # --- PI / SI / flash / init (librecomp) ----------------------------------------------------------------------------------
    (L + "pi.cpp", "do_rom_read", None, [("rom", "H-before",
     "PI ROM DMA: do_dma copies the whole transfer synchronously, then posts the Pi message (same guest thread)",
     [("fnbody", PIP, "do_dma", r"recomp::do_rom_read\(rdram, rdram_address, physical_addr, size\);(?:(?!enqueue_external_message)[\s\S])*?s7196_test_hit\(\)")])]),
    (L + "pi.cpp", "save_read", None, [("sram", "H-before", "SRAM read copied before the Pi message (do_dma sram branch); eeprom/flash callers synchronous",
     [("fnbody", PIP, "do_dma", r"save_read\(rdram, rdram_address, [^;]*\);\s*ultramodern::enqueue_external_message_src")])]),
    (L + "pi.cpp", "do_rom_pio", None, [("pio", "H-guest-thread", "PI PIO word read, called synchronously from the guest's osPiReadIo",
     [("file", PIP, r"do_rom_pio\(")])]),
    G(L + "pi.cpp", "osPiStartDma_recomp", why="writes the guest OSIoMesg fields on the calling guest thread before do_dma"),
    DEAD(L + "pi.cpp", "osEPiStartDma_recomp", "osEPiStartDma_recomp"),
    DEAD(L + "pi.cpp", "osEPiReadIo_recomp", "osEPiReadIo_recomp"),
    DEAD(L + "pi.cpp", "osCartRomInit_recomp", "osCartRomInit_recomp"),
    DEAD(L + "pi.cpp", "osDriveRomInit_recomp", "osDriveRomInit_recomp"),
    G(L + "cont.cpp", "osContInit_recomp"),
    G(L + "cont.cpp", "osContGetReadData_recomp", why="controller data copied into the guest buffer on the calling guest thread "
      "(osContStartReadData's SI message already posted; hardware fills the buffer in osContGetReadData too)"),
    DEAD(L + "flash.cpp", "osFlashReadStatus_recomp", "osFlashReadStatus_recomp"),
    DEAD(L + "flash.cpp", "osFlashReadId_recomp", "osFlashReadId_recomp"),
    DEAD(L + "flash.cpp", "osFlashWriteBuffer_recomp", "osFlashWriteBuffer_recomp"),
    DEAD(L + "flash.cpp", "osFlashReadArray_recomp", "osFlashReadArray_recomp"),
    (L + "recomp.cpp", "init", None, [("init", "H-init", "os globals (osTvType/osRomBase/osResetType/osMemSize) before the game thread starts",
     [("body", r"MEM_W\(osMemSize, 0\)")])]),
    G(L + "ultra_translation.cpp", "osInitialize_recomp"),
    (L + "overlays.cpp", "read_patch_data", None, [("init", "H-init", "patch data copied from recomp::init before the game starts",
     [("fnbody", "lib/N64ModernRuntime/librecomp/src/recomp.cpp", "init", r"read_patch_data\(")])]),
    (L + "mods.cpp", "init_mod_code", None, [("mods", "H-init", "mod loader: runs at mod load, before the game starts (no mods ship)", [])]),
    (L + "mod_config_api.cpp", "return_string", None, [("mods", "H-guest-thread", "mod config API return, called by a mod on its guest thread", [])]),
    (L + "overlays.cpp", "rs64_s7520_swap", None, [("diag", "H-diag", "s7520 FQ code-watch control flip (ROGUESQ_S7520_CTL)",
     [("near", r"s7\.ctl &&", 600), ("file", "lib/N64ModernRuntime/librecomp/src/overlays.cpp", r'getenv\("ROGUESQ_S7520_CTL"\)')])]),
    (L + "overlays.cpp", "rs64_s7520_gf", None, [("diag", "H-diag", "s7520 FQ control flip (ROGUESQ_S7520_CTL)",
     [("near", r"s7\.ctl", 900), ("file", "lib/N64ModernRuntime/librecomp/src/overlays.cpp", r'getenv\("ROGUESQ_S7520_CTL"\)')])]),
    G(L + "sp.cpp", "__attribute__", imp="osSpTaskStartGo_recomp", why="osSpTaskStartGo task pointer on the guest thread"),
    # --- ultramodern -----------------------------------------------------------------------------------------------------------
    (U + "events.cpp", "apply", ("line", r"rdram \+ (?:0x9ECB0|addrs\[i\]|ia\[i\])"), [("lever", "H-lever",
     "G1c draw-distance lever (ROGUESQ_DD_RADIUS/_LOD/_IMUL/_ADDRS): rewrites the same rodata constants to the same values each VI "
     "from the gfx thread; the game only reads them", [("body", r"ROGUESQ_DD_RADIUS")])]),
    (U + "events.cpp", "apply", ("line", r"&rdram\[0x128EAF \^ 3\]"), [("lever", "H-lever",
     "ROGUESQ_FPS60 arbiter-limit clamp 2->1 from the gfx thread; byte CAS (class FZ s7533) never overwrites a guest store",
     [("near", r'getenv\("ROGUESQ_FPS60"\)', 1500), ("body", r"__atomic_compare_exchange_n\(lb")])]),
    (U + "events.cpp", "apply", ("line", r"rdram\[LIM \^ 3\]"), [("lever", "H-diag", "ROGUESQ_G1E_LIMIT arbiter lever (s6255, test only)",
     [("near", r'getenv\("ROGUESQ_G1E_LIMIT"\)', 3000)])]),
    G(U + "events.cpp", "osViSetMode", imp="osViSetMode_recomp"),
    G(U + "events.cpp", "submit_rsp_task", imp="osSpTaskStartGo_recomp", why="called from osSpTaskStartGo on the guest thread"),
    G(U + "input.cpp", "osContInit", imp="osContInit_recomp"),
    G(U + "input.cpp", "osContGetQuery", imp="osContGetQuery_recomp"),
    G(U + "input.cpp", "osMotorInit", imp="osMotorInit_recomp"),
    G(U + "input.cpp", "__osMotorAccess", imp="osMotorInit_recomp", why="rumble access, guest thread (osMotorStart/Stop macros)"),
    (U + "mesgqueue.cpp", "dequeue_external_messages", None, [("guest", "H-guest-thread",
     "host device messages are queued host-side; dequeue (the guest-RAM OSMesgQueue store) runs on a guest thread inside "
     "osSendMesg/osJamMesg/osRecvMesg/rs64_preempt_point", [("fnbody", "lib/N64ModernRuntime/ultramodern/src/mesgqueue.cpp", "osRecvMesg", r"dequeue_external_messages\(")])]),
    (U + "mesgqueue.cpp", "do_send", None, [("guest", "H-guest-thread", "called only from os*Mesg and dequeue_external_messages (guest threads)",
     [("nm_present", "osSendMesg_recomp")])]),
    (U + "mesgqueue.cpp", "do_recv", None, [("guest", "H-guest-thread", "osRecvMesg body", [("nm_present", "osRecvMesg_recomp")])]),
    G(U + "mesgqueue.cpp", "osCreateMesgQueue", imp="osCreateMesgQueue_recomp"),
    G(U + "mesgqueue.cpp", "osSendMesg", imp="osSendMesg_recomp"),
    G(U + "mesgqueue.cpp", "osRecvMesg", imp="osRecvMesg_recomp"),
    D(U + "scheduling.cpp", "s4583_dump", "ROGUESQ_LOG_S4583", n=2000),
    G(U + "scheduling.cpp", "schedule_running_thread", imp="osStartThread_recomp", why="scheduler, called from os thread calls on guest threads"),
    G(U + "threadqueue.cpp", "thread_queue_insert", imp="osStartThread_recomp", why="guest OS thread queue, guest threads"),
    G(U + "threadqueue.cpp", "PTR", imp="osStartThread_recomp", why="thread_queue_pop (guest OS thread queue), guest threads"),
    G(U + "threadqueue.cpp", "thread_queue_remove", imp="osSetThreadPri_recomp", why="guest OS thread queue, guest threads"),
    (U + "threadqueue.cpp", "s7396_control", None, [("diag", "H-diag", "s7396 TQ control (ROGUESQ_S7396_TQ_CTL) on fake structs",
     [("file", "lib/N64ModernRuntime/ultramodern/src/threadqueue.cpp", r"ROGUESQ_S7396_TQ_CTL")])]),
    G(U + "threads.cpp", "run_next_thread_and_wait", imp="osStartThread_recomp"),
    G(U + "threads.cpp", "resume_thread_and_wait", imp="osStartThread_recomp"),
    G(U + "threads.cpp", "_thread_func", imp="osCreateThread_recomp", why="the guest thread's own host thread"),
    G(U + "threads.cpp", "osStartThread", imp="osStartThread_recomp"),
    G(U + "threads.cpp", "osCreateThread", imp="osCreateThread_recomp"),
    G(U + "threads.cpp", "osDestroyThread", imp="osDestroyThread_recomp"),
    G(U + "threads.cpp", "osSetThreadPri", imp="osSetThreadPri_recomp"),
    G(U + "timer.cpp", "osSetTimer", imp="osSetTimer_recomp"),
    (U + "timer.cpp", "timer_thread", None, [("os", "H-os-private",
     "Timer thread stores OSTimer.timestamp/interval/mq/msg (s7397 carry) and re-arms timestamp after posting the Timer "
     "message, as hardware __osTimerInterrupt re-inserts after osSendMesg. OSTimer is libultra-private: every routine that "
     "reads it (osSetTimer/osStopTimer/__osTimerInterrupt) is host-replaced; s7397 found 1 live osSetTimer site. Single-source "
     "(code reading): no runtime guest-reader census of OSTimer fields", [("nm_present", "osSetTimer_recomp"), ("body", r"enqueue_external_message_src\(cur_timer->mq")])]),
    # --- src/main ------------------------------------------------------------------------------------------------------------
    D(MNP, "rs64_s6848_force_ovl", "ROGUESQ_S6848_FORCE_OVL", n=1200),
    D(MNP, "start_level_poller", "ROGUESQ_FORCE_SEL", n=4000, why="harness level/mission force (ROGUESQ_FORCE_SEL/FORCE_MISSION/LOG_LEVEL; "
      "poller thread returns at start unless one is set)"),
    D(MNP, "start_state_poller", "ROGUESQ_FORCE_EMPTY_POOL_SENTINEL", n=800),
    A(RCP, "?", ("line", r"uint8_t\* rdram = app->core\.RDRAM;")),
    D(RCP, "?", "ROGUESQ_FORCE_BUFFER_PROGRESS", rng=True, n=1600),
    D(RCP, "?", "ROGUESQ_DEBUG_WRITE", rng=True, n=2000),  # s7846: s7845 RAND_TRACE_BOOT block put the store 1778 chars after the getenv
    A(RCP, "submit_rdp_range"),
    D("src/main/upstream_compat.cpp", "rs64_s6883_tables", r"s6883_mode\(\) & 4", n=200,
      why="ROGUESQ_G1D_SPANCELL bit 4 only (default 3)"),
    G("src/main/upstream_compat.cpp", "osDpGetCounters_recomp"),
    D("src/main/upstream_compat.cpp", "osViSwapBuffer_recomp", "s_ts_ctl", n=200, why="ROGUESQ_TIME_SHAPE_CTL control poke (guest thread)"),
    G("src/main/upstream_compat.cpp", "osViSetMode_recomp", why="VI mode struct edits (G1d width) on the calling guest thread"),
    D("src/main/upstream_compat.cpp", "rs64_s5042_poison", "ROGUESQ_FREE_POISON", n=1500),
    ("src/main/upstream_compat.cpp", "zmemcpy", None, [("guest", "H-guest-thread", "host body of a recompiled game function (recomp_context)",
     [("body", r"ctx->r2")])]),
    G("src/main/upstream_compat.cpp", "osSpTaskStartGo_recomp"),
    G("src/main/upstream_compat.cpp", "osStopThread_recomp"),
    # --- src/rsp -------------------------------------------------------------------------------------------------------------
    D("src/rsp/dpc_bridge.cpp", "rsp_dpc_submit_impl", r"gate_inject \|\| s_pipe_inject == 0", rng=True, n=600,
      why="ROGUESQ_FS_PIPE_INJECT synth FULL_SYNC scratch (off by default)"),
    D("src/rsp/dpc_bridge.cpp", "rsp_dpc_submit_impl", "alpha_full", rng=True, n=600, why="ROGUESQ_PRIM_ALPHA_FF (diag)"),
    D("src/rsp/dpc_bridge.cpp", "rsp_dpc_submit_impl", "ROGUESQ_PRIM_FF|prim_ff", rng=True, n=2500, why="ROGUESQ_PRIM_FF (diag)"),
    A("src/rsp/dpc_bridge.cpp", "rsp_dpc_submit_impl", ("line", r"\bbase = rdram \+ \(g_pak_last_tlut_addr")),
    # s7653: G6c stand-ins opt-in levers (guest-thread scenegraph hook; matrix stack copy at sp+0x10 / control-arm zeroing)
    D("src/main/rs64_standins.cpp", "rs64_sg_draw", r"s_pull > 0\.0f && z > s_pull", rng=True, n=400,
      why="ROGUESQ_STANDINS_PULL depth-pull discriminator (off by default)"),
    D("src/main/rs64_standins.cpp", "rs64_sg_draw", r"if \(s_ctl && s_sg_cur == 0", rng=True, n=300,
      why="ROGUESQ_STANDINS_CTL real-object positive control (off by default)"),
    ("src/rsp/s7521_ucode_watch.cpp", "rs64_s7521_task", None, [("diag", "H-diag", "ROGUESQ_S7521_CTL flip/restore",
     [("file", "src/rsp/s7521_ucode_watch.cpp", r'getenv\("ROGUESQ_S7521_CTL"\)'), ("near", r"if \(c\)", 120)])]),
    ("src/rsp/s7521_ucode_watch.cpp", "rs64_s7521_imem", None, [("diag", "H-diag", "ROGUESQ_S7521_CTL imem flip",
     [("file", "src/rsp/s7521_ucode_watch.cpp", r'getenv\("ROGUESQ_S7521_CTL"\)'), ("near", r"if \(c\)", 120)])]),
]
