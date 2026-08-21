/* rs64_oracle - ground-truth oracle for RogueSquadron64Recomp.
 *
 * Runs the retail ROM under mupen64plus (built with DEBUGGER=1) and reports
 * what the REAL machine does, so a question about game behaviour can be
 * answered by observation instead of by inference from our own runtime.
 *
 * It exists because our runtime is simultaneously the thing under test and
 * the only instrument we had. Every "does the game really do X?" question was
 * being answered with our own recompiled output as the witness. This gives an
 * independent second source.
 *
 * Primary use: memory write/read watches.
 *
 *   rs64_oracle --rom rogue_squadron.z64 --secs 120 \
 *               --watch-write 0x1F3CC0:0x1F3CD0
 *
 * prints, for every access, the guest PC that made it:
 *
 *   [hit] w addr=0x001f3cc0 pc=0x800b1234 prev_pc=0x800b1230 t=41.2s n=1
 *
 * Zero hits over a full run is itself the answer: the retail game never
 * touches that address, so anything our port sees there is ours.
 *
 * Build: ./build.sh   (see README.md for the DEBUGGER=1 core build)
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <dlfcn.h>
#include <pthread.h>
#include <unistd.h>
#include <time.h>
#include <sys/stat.h>

#include "m64p_types.h"
#include "m64p_frontend.h"
#include "m64p_debugger.h"

/* Lives in the core's src/main/version.h, which is not part of the public
 * api/ headers. CoreStartup only compares the top 16 bits. */
#ifndef FRONTEND_API_VERSION
#define FRONTEND_API_VERSION 0x020106
#endif

#define MAX_WATCHES 64
#define MAX_WRITER_PCS 128
#define MAX_POST_VALUE_HIST 64
#define MAX_POST_VALUE_PCS 512
#define MAX_POST_VALUE_SAMPLES 256
#define MAX_POST_VALUE_ROWS_PER_PC 16
#define VI_ORIGIN_ADDR 0xA4400004u
#define VI_WIDTH_ADDR  0xA4400008u

static void *g_core;
static double g_t0;

/* core entry points */
static m64p_error (*pCoreStartup)(int, const char *, const char *, void *,
                                  void (*)(void *, int, const char *), void *,
                                  void (*)(void *, m64p_core_param, int));
static m64p_error (*pCoreShutdown)(void);
static m64p_error (*pCoreDoCommand)(m64p_command, int, void *);
static m64p_error (*pCoreAttachPlugin)(m64p_plugin_type, m64p_dynlib_handle);
static m64p_error (*pConfigOpenSection)(const char *, m64p_handle *);
static m64p_error (*pConfigSetParameter)(m64p_handle, const char *, m64p_type, const void *);
static m64p_error (*pConfigSaveFile)(void);

/* debugger entry points */
static m64p_error (*pDebugSetCallbacks)(void (*)(void), void (*)(unsigned int), void (*)(void));
static m64p_error (*pDebugSetRunState)(m64p_dbg_runstate);
static m64p_error (*pDebugStep)(void);
static int        (*pDebugBreakpointCommand)(m64p_dbg_bkp_command, unsigned int, m64p_breakpoint *);
static void       (*pDebugBreakpointTriggeredBy)(uint32_t *, uint32_t *);
static int        (*pDebugGetState)(m64p_dbg_state);
static unsigned int (*pDebugMemRead32)(unsigned int);
static void (*pDebugMemWrite32)(unsigned int, unsigned int);

struct watch {
    uint32_t start, end;
    unsigned int flags;
    const char *label;
    long hits;
    long read_hits;
    long write_hits;
};
static struct watch g_watch[MAX_WATCHES];
struct writer_pc {
    uint32_t pc;
    long n;
};
static struct writer_pc g_writer_pc[MAX_WATCHES][MAX_WRITER_PCS];
static int g_n_writer_pc[MAX_WATCHES];
static long g_writer_pc_overflow[MAX_WATCHES];
static int g_nwatch;
static long g_hits;
static long g_hit_cap = 200;          /* stop logging after this many, keep running */
static unsigned int g_detail_watch_mask;
static int g_first_watch = -1;
static int g_pc_hist_watch = -1;
static int g_post_value_watch = -1;
static uint32_t g_post_value_requested_pc[32];
static int g_post_value_requested_seen[32];
static uint32_t g_post_value_requested_value[32];
static uint32_t g_post_value_requested_addr[32];
static int g_n_post_value_requested_pc;
struct post_value_requested_row {
    long vi;
    uint32_t width;
    uint32_t origin;
    uint32_t addr;
    uint32_t value;
};
static struct post_value_requested_row
    g_post_value_requested_rows[32][MAX_POST_VALUE_ROWS_PER_PC];
static int g_n_post_value_requested_rows[32];
struct post_value_entry {
    uint32_t value;
    long n;
};
struct post_value_pc_entry {
    uint32_t pc;
    long samples;
    long zero_words;
    long nonzero_words;
};
static struct post_value_entry g_post_value_hist[MAX_POST_VALUE_HIST];
static struct post_value_pc_entry g_post_value_pc[MAX_POST_VALUE_PCS];
static int g_n_post_value_hist;
static int g_n_post_value_pc;
static long g_post_value_samples;
static long g_post_value_overflow;
static long g_post_value_pc_overflow;
static int g_post_value_pending;
static int g_post_value_pending_target = -1;
static int g_post_value_armed;
static uint32_t g_post_value_addr;
static uint32_t g_post_value_pc_addr;
static uint32_t g_post_snapshot_fnv;
static unsigned long g_post_snapshot_nonzero;
static unsigned long g_post_snapshot_bytes;
static int g_post_snapshot_valid;
static long g_vis;
static int g_verbose;
static int g_watches_armed;
static int g_positive_watch_removed;
static long g_pc_hits;
#define MAX_EXEC_PREV 128
struct exec_prev {
    uint32_t pc;
    uint32_t prev;
    long n;
};
static struct exec_prev g_exec_prev[MAX_EXEC_PREV];
static int g_n_exec_prev;
static long g_exec_prev_overflow;
static void count_exec_prev(uint32_t pc, uint32_t prev)
{
    int i;
    for (i = 0; i < g_n_exec_prev; i++) {
        if (g_exec_prev[i].pc == pc && g_exec_prev[i].prev == prev) {
            g_exec_prev[i].n++;
            return;
        }
    }
    if (g_n_exec_prev < MAX_EXEC_PREV) {
        g_exec_prev[g_n_exec_prev].pc = pc;
        g_exec_prev[g_n_exec_prev].prev = prev;
        g_exec_prev[g_n_exec_prev].n = 1;
        g_n_exec_prev++;
        return;
    }
    g_exec_prev_overflow++;
}

static void count_writer_pc(int watch, uint32_t pc)
{
    int i;
    for (i = 0; i < g_n_writer_pc[watch]; i++) {
        if (g_writer_pc[watch][i].pc == pc) {
            g_writer_pc[watch][i].n++;
            return;
        }
    }
    if (g_n_writer_pc[watch] < MAX_WRITER_PCS) {
        g_writer_pc[watch][g_n_writer_pc[watch]].pc = pc;
        g_writer_pc[watch][g_n_writer_pc[watch]].n = 1;
        g_n_writer_pc[watch]++;
    } else {
        g_writer_pc_overflow[watch]++;
    }
}

static void count_post_value(uint32_t pc, uint32_t value)
{
    int i, found = 0;
    g_post_value_samples++;
    for (i = 0; i < g_n_post_value_hist; i++) {
        if (g_post_value_hist[i].value == value) {
            g_post_value_hist[i].n++;
            found = 1;
            break;
        }
    }
    if (!found && g_n_post_value_hist < MAX_POST_VALUE_HIST) {
        g_post_value_hist[g_n_post_value_hist].value = value;
        g_post_value_hist[g_n_post_value_hist].n = 1;
        g_n_post_value_hist++;
    } else if (!found) {
        g_post_value_overflow++;
    }
    for (i = 0; i < g_n_post_value_pc; i++) {
        if (g_post_value_pc[i].pc == pc) {
            g_post_value_pc[i].samples++;
            if (value == 0)
                g_post_value_pc[i].zero_words++;
            else
                g_post_value_pc[i].nonzero_words++;
            return;
        }
    }
    if (g_n_post_value_pc < MAX_POST_VALUE_PCS) {
        g_post_value_pc[g_n_post_value_pc].pc = pc;
        g_post_value_pc[g_n_post_value_pc].samples = 1;
        g_post_value_pc[g_n_post_value_pc].zero_words = value == 0;
        g_post_value_pc[g_n_post_value_pc].nonzero_words = value != 0;
        g_n_post_value_pc++;
    } else {
        g_post_value_pc_overflow++;
    }
}

static void record_post_value_requested_row(int target, uint32_t value)
{
    struct post_value_requested_row *row;

    if (target < 0 || target >= g_n_post_value_requested_pc ||
        g_n_post_value_requested_rows[target] >= MAX_POST_VALUE_ROWS_PER_PC)
        return;
    row = &g_post_value_requested_rows[target]
        [g_n_post_value_requested_rows[target]++];
    row->vi = g_vis;
    row->width = pDebugMemRead32(VI_WIDTH_ADDR);
    row->origin = pDebugMemRead32(VI_ORIGIN_ADDR);
    row->addr = g_post_value_addr & ~3u;
    row->value = value;
    if (!g_post_value_requested_seen[target]) {
        g_post_value_requested_seen[target] = 1;
        g_post_value_requested_value[target] = value;
        g_post_value_requested_addr[target] = row->addr;
    }
    printf("[post-target-row] pc=0x%08x vi=%ld width=%u origin=0x%08x addr=0x%08x value=0x%08x\n",
           g_post_value_requested_pc[target], row->vi, row->width,
           row->origin, row->addr, row->value);
    fflush(stdout);
}

static int post_value_pc_seen(uint32_t pc)
{
    int i;
    for (i = 0; i < g_n_post_value_pc; i++) {
        if (g_post_value_pc[i].pc == pc)
            return 1;
    }
    return 0;
}

static int post_value_requested_index(uint32_t pc)
{
    int i;
    for (i = 0; i < g_n_post_value_requested_pc; i++) {
        if (g_post_value_requested_pc[i] == pc)
            return i;
    }
    return -1;
}

static void add_post_value_pcs(const char *arg)
{
    char *copy = strdup(arg);
    char *tok, *save = NULL;
    if (!copy)
        exit(1);
    for (tok = strtok_r(copy, ",", &save); tok; tok = strtok_r(NULL, ",", &save)) {
        unsigned int pc;
        if (g_n_post_value_requested_pc >= 32 || sscanf(tok, "%x", &pc) != 1) {
            fprintf(stderr, "[oracle] bad --post-value-pc '%s'\n", tok);
            free(copy);
            exit(2);
        }
        g_post_value_requested_pc[g_n_post_value_requested_pc++] = pc;
    }
    free(copy);
}

static uint32_t debug_rdram_addr(uint32_t physical)
{
    return 0x80000000u | (physical & 0x1FFFFFFFu);
}

static void summarize_post_snapshot(int watch)
{
    uint32_t fnv = 2166136261u;
    unsigned long nonzero = 0;
    unsigned long bytes = 0;
    uint32_t addr;

    if (watch < 0 || watch >= g_nwatch)
        return;
    for (addr = g_watch[watch].start; addr + 4 <= g_watch[watch].end; addr += 4) {
        uint32_t value = pDebugMemRead32(debug_rdram_addr(addr));
        unsigned int shift;
        for (shift = 24; ; shift -= 8) {
            unsigned int byte = (value >> shift) & 0xFFu;
            fnv = (fnv * 16777619u) ^ byte;
            nonzero += byte != 0;
            bytes++;
            if (shift == 0)
                break;
        }
    }
    g_post_snapshot_fnv = fnv;
    g_post_snapshot_nonzero = nonzero;
    g_post_snapshot_bytes = bytes;
    g_post_snapshot_valid = 1;
}
static int g_voice_base_write_seen;
static int g_voice_base_read_after_write_seen;
static int g_voice_base_post_step_pending;
static int g_debug_write_enabled;
static unsigned g_debug_write_addr, g_debug_write_value;
static int g_debug_write_done;

static double now_s(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec + ts.tv_nsec / 1e9;
}

static void core_msg(void *ctx, int level, const char *msg)
{
    (void)ctx;
    /* level 1 = error, 2 = warning. Info/status is noise for an oracle run. */
    if (level <= 2 || g_verbose)
        fprintf(stderr, "[core] %s\n", msg);
}

/* ---- debugger callbacks ------------------------------------------------ */

/* Installs every --watch-* the user asked for. Split out of dbg_init() (see
 * below) so it can be deferred to first VI instead of running at debugger
 * init. */
static void arm_watches(void)
{
    int i;
    for (i = 0; i < g_nwatch; i++) {
        m64p_breakpoint bkp;
        int idx;
        bkp.address = g_watch[i].start;
        /* lookup_breakpoint() tests `address <= endaddr`, i.e. endaddr is
         * INCLUSIVE. We take ranges half-open like everyone else, so convert
         * here - otherwise every watch silently covers one extra word and
         * reports hits from outside the range you asked about. */
        bkp.endaddr = g_watch[i].end - 1;
        bkp.flags   = M64P_BKP_FLAG_ENABLED | g_watch[i].flags;
        idx = pDebugBreakpointCommand(M64P_BKP_CMD_ADD_STRUCT, 0, &bkp);
        if (idx < 0) {
            fprintf(stderr, "[oracle] FAILED to add watch %s [0x%08x,0x%08x]\n",
                    g_watch[i].label, g_watch[i].start, g_watch[i].end);
        } else {
            printf("[watch] %s [0x%08x,0x%08x) flags=0x%x idx=%d\n",
                   g_watch[i].label, g_watch[i].start, g_watch[i].end,
                   bkp.flags, idx);
        }
    }
    fflush(stdout);
}

/* Called once, when the debugger is initialised and the CPU is about to run.
 * Does NOT arm watches here even though the breakpoint table already exists
 * by this point (it's allocated as part of debugger init, before this
 * callback fires): poweron_r4300() hasn't run yet, so r4300's PC-tracking
 * field is still NULL, and pif_bootrom_hle_execute() - an internal bootstrap
 * read of the PIF ROM that happens before run_pure_interpreter() ever sets
 * that field - runs before a single CPU instruction does. A PIF-region watch
 * armed here sees that internal read and crashes inside r4300_pc() computing
 * NULL->addr (measured s982: fault at read_with_bp_checks+268, address
 * 0x28 == offsetof(precomp_instr, addr)). Watches arm instead on the first
 * VI (see dbg_vi), by which point the interpreter loop has long since
 * initialized pc, and there is no meaningful "current instruction" to
 * attribute a bootstrap-phase read to anyway. */
static void dbg_init(void)
{
    pDebugSetRunState(M64P_DBG_RUNSTATE_RUNNING);
}

/* Called with the CPU halted whenever a breakpoint hits. Log and resume.
 * Do not block here - the emulator thread is inside this call. */
static void dbg_update(unsigned int pc)
{
    uint32_t flags = 0, accessed = 0;
    int i;
    int detail_hit = 0;
    unsigned int access_flags = flags;

    /* Memory breakpoints stop before the instruction performs its access.
     * The stepping callback is the first debugger callback after that
     * instruction, so sample the field there instead of treating the
     * pre-store value as the store result. */
    if (g_voice_base_post_step_pending) {
        g_voice_base_post_step_pending = 0;
        printf("[voice-base] post-step pc=0x%08x prev_pc=0x%08x value=0x%08x\n",
               pc, (unsigned int)pDebugGetState(M64P_DBG_PREVIOUS_PC),
               pDebugMemRead32(0x001496F8));
        fflush(stdout);
        pDebugSetRunState(M64P_DBG_RUNSTATE_RUNNING);
        pDebugStep();
        return;
    }

    if (g_post_value_pending) {
        uint32_t value;
        g_post_value_pending = 0;
        value = pDebugMemRead32(debug_rdram_addr(g_post_value_addr & ~3u));
        count_post_value(g_post_value_pc_addr, value);
        if (g_post_value_pending_target >= 0) {
            int target = g_post_value_pending_target;
            g_post_value_pending_target = -1;
            record_post_value_requested_row(target, value);
        }
        pDebugSetRunState(M64P_DBG_RUNSTATE_RUNNING);
        pDebugStep();
        return;
    }

    pDebugBreakpointTriggeredBy(&flags, &accessed);
    access_flags = flags & (M64P_BKP_FLAG_READ | M64P_BKP_FLAG_WRITE);

    g_hits++;
    for (i = 0; i < g_nwatch; i++) {
        if (accessed >= g_watch[i].start && accessed < g_watch[i].end &&
            (access_flags & g_watch[i].flags &
             (M64P_BKP_FLAG_READ | M64P_BKP_FLAG_WRITE))) {
            g_watch[i].hits++;
            if (access_flags & M64P_BKP_FLAG_READ)
                g_watch[i].read_hits++;
            if (access_flags & M64P_BKP_FLAG_WRITE)
                g_watch[i].write_hits++;
            if (g_pc_hist_watch == i && (access_flags & M64P_BKP_FLAG_WRITE))
                count_writer_pc(i, pc);
            if (g_post_value_watch == i && (access_flags & M64P_BKP_FLAG_WRITE) &&
                g_post_value_armed) {
                int target = post_value_requested_index(pc);
                int force_target = target >= 0 &&
                    g_n_post_value_requested_rows[target] <
                    MAX_POST_VALUE_ROWS_PER_PC;
                int sample_generic = g_post_value_samples < MAX_POST_VALUE_SAMPLES ||
                    (!post_value_pc_seen(pc) && g_n_post_value_pc < MAX_POST_VALUE_PCS);
                if (force_target || sample_generic) {
                    g_post_value_pending = 1;
                    g_post_value_pending_target = force_target ? target : -1;
                    g_post_value_addr = accessed;
                    g_post_value_pc_addr = pc;
                }
            }
        }
        if ((g_watch[i].flags & M64P_BKP_FLAG_EXEC) &&
            pc >= g_watch[i].start && pc < g_watch[i].end) {
            g_watch[i].hits++;
            g_pc_hits++;
            count_exec_prev(pc, (uint32_t)pDebugGetState(M64P_DBG_PREVIOUS_PC));
        }
        if (accessed >= g_watch[i].start && accessed < g_watch[i].end &&
            (access_flags & g_watch[i].flags &
             (M64P_BKP_FLAG_READ | M64P_BKP_FLAG_WRITE)) &&
            (g_detail_watch_mask & (1u << i)))
            detail_hit = 1;
        if (g_first_watch == i && g_watch[i].hits == 1)
            detail_hit = 1;
    }
    if (!g_positive_watch_removed && g_nwatch > 0 && g_watch[0].write_hits == 10000) {
        int rc = pDebugBreakpointCommand(M64P_BKP_CMD_REMOVE_IDX, 0, NULL);
        printf("[oracle] positive-control threshold reached: watch index 0 callbacks=%ld; removal rc=%d; watch index 1 remains armed\n",
               g_watch[0].write_hits, rc);
        fflush(stdout);
        g_positive_watch_removed = 1;
    }
    if (g_hits <= g_hit_cap || detail_hit) {
        unsigned int prev = (unsigned int)pDebugGetState(M64P_DBG_PREVIOUS_PC);
        printf("[hit] %s%s%s addr=0x%08x pc=0x%08x prev_pc=0x%08x t=%.1fs n=%ld\n",
               (flags & M64P_BKP_FLAG_WRITE) ? "w" : "",
               (flags & M64P_BKP_FLAG_READ)  ? "r" : "",
               (flags & M64P_BKP_FLAG_EXEC)  ? "x" : "",
               accessed, pc, prev, now_s() - g_t0, g_hits);
        if ((flags & (M64P_BKP_FLAG_WRITE | M64P_BKP_FLAG_READ)) &&
            accessed >= 0x001496F8 && accessed < 0x001496FC) {
            if (flags & M64P_BKP_FLAG_WRITE) {
                g_voice_base_write_seen = 1;
                printf("[voice-base] write pc=0x%08x value=0x%08x\n",
                       pc, pDebugMemRead32(0x001496F8));
                g_voice_base_post_step_pending = 1;
            } else if ((flags & M64P_BKP_FLAG_READ) && g_voice_base_write_seen &&
                       !g_voice_base_read_after_write_seen) {
                g_voice_base_read_after_write_seen = 1;
                printf("[voice-base] first-read-after-write pc=0x%08x value=0x%08x\n",
                       pc, pDebugMemRead32(0x001496F8));
            }
        }
        if (g_hits == g_hit_cap)
            printf("[oracle] hit cap %ld reached, counting silently from here\n", g_hit_cap);
        fflush(stdout);
    }

    if (g_voice_base_post_step_pending) {
        pDebugSetRunState(M64P_DBG_RUNSTATE_STEPPING);
        pDebugStep();
    } else if (g_post_value_pending) {
        pDebugSetRunState(M64P_DBG_RUNSTATE_STEPPING);
        pDebugStep();
    } else {
        pDebugSetRunState(M64P_DBG_RUNSTATE_RUNNING);
        pDebugStep();
    }
}

/* One call per vertical interrupt = one displayed frame on real hardware.
 * Printed at the end so a run always reports how far the GAME got, not just
 * how long the wall clock ran: the debugger forces the pure interpreter, so
 * wall seconds and emulated seconds are not the same thing at all.
 *
 * This is also where the phase signal comes from. With no video plugin there
 * is nothing to look at, so VI_WIDTH and VI_ORIGIN stand in for "what is on
 * screen" - the same timeline our port logs as [vi], and the only way to tell
 * a menu from a mission in a headless run. Sampled here rather than from a
 * polling thread because the VI callback runs ON the emulator thread, so the
 * read cannot race the CPU that is writing those registers. */
/* PIF RAM holds the SI's controller readout: after a 0x01 (read controller)
 * command the button word for pad 1 lands at physical 0x1FC007C4. Reading it
 * answers the one question a headless run cannot otherwise settle - does the
 * GAME see the buttons we inject, or are we only talking to the plugin? */
#define PIF_PAD1_ADDR  0xBFC007C4u
#define N64_BTN_START  0x00001000u

static int g_vi_trace;
static int g_vi_poll;
static int g_status_poll;
static int g_pif_trace;
static unsigned g_last_pad0 = 0xFFFFFFFFu;
static unsigned g_last_pad = 0xFFFFFFFFu;
static unsigned g_last_width = 0xFFFFFFFFu, g_last_origin = 0xFFFFFFFFu;
static double g_last_origin_log = -1e9;
static volatile int g_poll_running;

static void dbg_vi(void)
{
    unsigned width, origin;
    double t;

    if (!g_watches_armed) {
        g_watches_armed = 1;
        arm_watches();
    }

    g_vis++;

    if (g_debug_write_enabled && !g_debug_write_done) {
        unsigned width = pDebugMemRead32(VI_WIDTH_ADDR);
        if (width == 320) {
            pDebugMemWrite32(g_debug_write_addr, g_debug_write_value);
            g_debug_write_done = 1;
            printf("[debug-write] vi=%ld width=%u addr=0x%08x value=0x%08x\n",
                   g_vis, width, g_debug_write_addr, g_debug_write_value);
            fflush(stdout);
        }
    }

    if (g_pif_trace) {
        /* Log the whole 8-byte block, not a halfword we assumed was the
         * buttons: the first cut watched only (word>>16) and silently missed
         * every press whose bits landed elsewhere, which looked exactly like
         * "the game ignores that key". Print both words and let the bits
         * identify themselves. */
        unsigned w0 = pDebugMemRead32(PIF_PAD1_ADDR - 4);
        unsigned w1 = pDebugMemRead32(PIF_PAD1_ADDR);
        if (w0 != g_last_pad0 || w1 != g_last_pad) {
            printf("[pad] t=%6.1fs vi=%-6ld 7C0=0x%08x 7C4=0x%08x\n",
                   now_s() - g_t0, g_vis, w0, w1);
            g_last_pad0 = w0;
            g_last_pad = w1;
            fflush(stdout);
        }
    }

    if (g_post_value_watch >= 0) {
        width = pDebugMemRead32(VI_WIDTH_ADDR);
        origin = pDebugMemRead32(VI_ORIGIN_ADDR);
        if ((width == 1024 && origin == 0x00790400u) ||
            (width == 512 && origin == 0x006AB400u))
            g_post_value_armed = 1;
    }

    if (!g_vi_trace) return;

    width  = pDebugMemRead32(VI_WIDTH_ADDR);
    origin = pDebugMemRead32(VI_ORIGIN_ADDR);
    t = now_s() - g_t0;

    if (width != g_last_width) {
        printf("[vi] t=%6.1fs vi=%-6ld WIDTH %u -> %u  origin=0x%08x\n",
               t, g_vis, g_last_width == 0xFFFFFFFFu ? 0 : g_last_width, width, origin);
        g_last_width = width;
        g_last_origin = origin;
        g_last_origin_log = t;
        fflush(stdout);
        return;
    }
    /* Origin flips every frame while double-buffered, so rate-limit it: we
     * only want to see the buffer SET change, not the swapping. */
    if (origin != g_last_origin && (t - g_last_origin_log) >= 1.0) {
        printf("[vi] t=%6.1fs vi=%-6ld origin=0x%08x width=%u\n", t, g_vis, origin, width);
        g_last_origin = origin;
        g_last_origin_log = t;
        fflush(stdout);
    }
}

/* ---- plugins ----------------------------------------------------------- */

/* Attaching a plugin is optional: the core substitutes its own dummy for any
 * type left unattached, which is what we want for video/audio/input in a
 * headless run. RSP is the exception - leaving it dummy means MusyX audio
 * tasks never complete and the game wedges on its own audio countdown, the
 * same wedge our port hit at session 2. */
static int attach_plugin(const char *path, m64p_plugin_type type)
{
    void *h = dlopen(path, RTLD_NOW);
    m64p_error (*pstart)(m64p_dynlib_handle, void *, void (*)(void *, int, const char *));
    if (!h) {
        fprintf(stderr, "[oracle] dlopen %s: %s\n", path, dlerror());
        return -1;
    }
    pstart = dlsym(h, "PluginStartup");
    if (pstart && pstart(g_core, NULL, core_msg) != M64ERR_SUCCESS) {
        fprintf(stderr, "[oracle] PluginStartup failed for %s\n", path);
        return -1;
    }
    if (pCoreAttachPlugin(type, h) != M64ERR_SUCCESS) {
        fprintf(stderr, "[oracle] CoreAttachPlugin failed for %s\n", path);
        return -1;
    }
    printf("[oracle] attached %s\n", path);
    return 0;
}

/* ---- run control ------------------------------------------------------- */

/* Key injection. The core forwards these to whatever input plugin is attached
 * (M64CMD_SEND_SDL_KEYDOWN takes keysym | keymod<<16), so an input plugin must
 * be attached for a press to reach the game - with the dummy input plugin the
 * command still succeeds and does nothing, which is the silent-failure shape
 * this project keeps getting bitten by. Codes are SDL2 keycodes; the mapping
 * from key to N64 button is whatever [Input-SDL-Control1] holds in
 * ~/.config/mupen64plus/mupen64plus.cfg (written on first run). */
/* N64 buttons, not keys. What --press sends is an SDL2 SCANCODE, because
 * mupen64plus-input-sdl matches incoming values against scancodes while its
 * config records SDL1-era keysyms - so sending the "obvious" keycode 13 for
 * Return lands on C-Left, and the config's A Button = key(304) is unreachable
 * by any keycode at all. Verified empirically against PIF RAM: each name below
 * was pressed and the resulting N64 button word read back (--pif-trace).
 *
 * These match the DEFAULT [Input-SDL-Control1] mapping. Change that config and
 * this table is wrong - re-derive it with --pif-trace, do not assume. */
struct keyname { const char *name; int sym; };
static const struct keyname g_keynames[] = {
    { "start",  40 },                                  /* Return   -> 0x1000 */
    { "a",     225 },                                  /* LShift   -> 0x8000 */
    { "b",     224 },                                  /* LCtrl    -> 0x4000 */
    { "z",      29 },                                  /* Z        -> 0x2000 */
    { "dup",    26 }, { "ddown", 22 },                 /* W / S              */
    { "dleft",   4 }, { "dright", 7 },                 /* A / D              */
    { "cup",    12 }, { "cdown", 14 },                 /* I / K              */
    { "cleft",  13 }, { "cright", 15 },                /* J / L              */
    { "l",      27 }, { "r",      6 },                 /* X / C              */
    { NULL, 0 }
};

struct press { double at; int sym; };
static struct press g_press[256];
static int g_npress;
static int g_hold_ms = 150;
static int g_have_input;
static int g_state_smoke;
static int g_state_reach;
static const char *g_state_path;

static int keycode(const char *s)
{
    int i;
    for (i = 0; g_keynames[i].name; i++)
        if (!strcmp(s, g_keynames[i].name)) return g_keynames[i].sym;
    return (int)strtol(s, NULL, 0);      /* raw SDL2 keycode */
}

static void sleep_s(double secs)
{
    struct timespec ts;
    if (secs <= 0) return;
    ts.tv_sec = (time_t)secs;
    ts.tv_nsec = (long)((secs - (double)ts.tv_sec) * 1e9);
    nanosleep(&ts, NULL);
}

static int state_file_exists(const char *path)
{
    struct stat st;
    return path != NULL && stat(path, &st) == 0 && st.st_size > 0;
}

static void *vi_poller(void *arg)
{
    unsigned last_width = 0xFFFFFFFFu, last_origin = 0xFFFFFFFFu;
    unsigned last_status[18];
    double last_raw_log = -1e9;
    int i;
    (void)arg;

    for (i = 0; i < 18; i++) last_status[i] = 0xFFFFFFFFu;

    sleep_s(0.1);
    while (g_poll_running) {
        double t = now_s() - g_t0;
        unsigned width = pDebugMemRead32(VI_WIDTH_ADDR);
        unsigned origin = pDebugMemRead32(VI_ORIGIN_ADDR);
        if (g_status_poll) {
            for (i = 0; i < 18; i++) {
                unsigned addr = 0x00154620u + (unsigned)i * 0x1228u;
                unsigned word = pDebugMemRead32(0xA0000000u | addr);
                unsigned status = (word >> 24) & 0xFFu;
                if (status != last_status[i]) {
                    printf("[oracle-status-poll] t=%6.1fs slot=%d addr=0x%08x word=0x%08x top=0x%02x low=0x%02x\n",
                           t, i, addr, word, status, word & 0xFFu);
                    fflush(stdout);
                    last_status[i] = status;
                }
            }
        }
        if ((t - last_raw_log) >= 1.0) {
            printf("[vi-poll-raw] t=%6.1fs width=%u origin=0x%08x\n", t, width, origin);
            fflush(stdout);
            last_raw_log = t;
        }
        if (width != 0 && (width != last_width || origin != last_origin)) {
            printf("[vi-poll] t=%6.1fs WIDTH %u%s%u origin=0x%08x\n",
                   t, last_width == 0xFFFFFFFFu ? 0 : last_width,
                   last_width == 0xFFFFFFFFu ? " -> " : " => ", width, origin);
            fflush(stdout);
            last_width = width;
            last_origin = origin;
        }
        sleep_s(0.01);
    }
    return NULL;
}

/* Drives the run: fires the press schedule, then stops the emulator. */
static void *director(void *arg)
{
    double secs = *(double *)arg;
    double t = 0;
    int i;

    if (g_state_smoke || g_state_reach) {
        m64p_error save_result, load_result = M64ERR_SYSTEM_FAIL;
        long before_hits, before_vis, after_save_hits, after_load_hits;
        long save_vis, load_vis;

        sleep_s(5.0);
        before_hits = g_hits;
        before_vis = g_vis;
        save_result = pCoreDoCommand(M64CMD_STATE_SAVE, 1, (void *)g_state_path);
        printf("[state-%s] save rc=%d path=%s before_hits=%ld before_vi=%ld\n",
               g_state_reach ? "reach" : "smoke",
               save_result, g_state_path, before_hits, before_vis);
        fflush(stdout);

        /* STATE_SAVE queues work on the emulator thread. Wait for the file so
         * LOAD cannot race the asynchronous writer. */
        for (i = 0; i < 100 && !state_file_exists(g_state_path); i++)
            sleep_s(0.1);
        after_save_hits = g_hits;
        save_vis = g_vis;
        if (state_file_exists(g_state_path))
            load_result = pCoreDoCommand(M64CMD_STATE_LOAD, 0, (void *)g_state_path);
        after_load_hits = g_hits;
        load_vis = g_vis;
        printf("[state-%s] file=%s save_rc=%d load_rc=%d exists=%d save_hits=%ld load_hits=%ld save_vi=%ld load_vi=%ld\n",
               g_state_reach ? "reach" : "smoke",
               g_state_path, save_result, load_result, state_file_exists(g_state_path),
               after_save_hits, after_load_hits, save_vis, load_vis);
        fflush(stdout);
    }

    for (i = 0; i < g_npress; i++) {
        if (g_press[i].at >= secs) break;
        sleep_s(g_press[i].at - t);
        t = g_press[i].at;
        pCoreDoCommand(M64CMD_SEND_SDL_KEYDOWN, g_press[i].sym, NULL);
        sleep_s(g_hold_ms / 1000.0);
        pCoreDoCommand(M64CMD_SEND_SDL_KEYUP, g_press[i].sym, NULL);
        t += g_hold_ms / 1000.0;
        printf("[press] t=%.1fs sym=%d%s\n", t, g_press[i].sym,
               g_have_input ? "" : "  (NO INPUT PLUGIN - press went nowhere)");
        fflush(stdout);
    }

    sleep_s(secs - t);
    printf("[oracle] %.0fs elapsed, stopping\n", secs);
    fflush(stdout);
    pCoreDoCommand(M64CMD_STOP, 0, NULL);
    return NULL;
}

/* Watches are compared against PHYSICAL addresses. r4300_write_aligned_word()
 * masks with 0x1ffffffc before mem_get_handler(), so the address that reaches
 * check_breakpoints_on_mem_access() has already lost its KSEG0/KSEG1 prefix.
 * A watch set on 0x801F3CC0 therefore never fires - and reports a clean zero,
 * which reads exactly like "the game never writes here". Mask on input so both
 * spellings work and neither can produce that false negative. */
static uint32_t to_phys(uint32_t a) { return a & 0x1FFFFFFFu; }

static int parse_range(const char *s, uint32_t *start, uint32_t *end)
{
    char *colon = strchr(s, ':');
    *start = to_phys((uint32_t)strtoul(s, NULL, 0));
    if (colon)
        *end = to_phys((uint32_t)strtoul(colon + 1, NULL, 0));
    else
        *end = *start + 4;          /* one word by default */
    return (*end > *start) ? 0 : -1;
}

static void add_watch(const char *arg, unsigned int flags, const char *label)
{
    if (g_nwatch >= MAX_WATCHES) {
        fprintf(stderr, "[oracle] too many watches\n");
        exit(2);
    }
    if (parse_range(arg, &g_watch[g_nwatch].start, &g_watch[g_nwatch].end) != 0) {
        fprintf(stderr, "[oracle] bad range '%s' (want START[:END], END exclusive)\n", arg);
        exit(2);
    }
    g_watch[g_nwatch].flags = flags;
    g_watch[g_nwatch].label = label;
    g_nwatch++;
}

static void add_pc_watches(const char *arg)
{
    char *copy = strdup(arg), *tok, *save = NULL;
    if (!copy) exit(2);
    for (tok = strtok_r(copy, ",", &save); tok; tok = strtok_r(NULL, ",", &save)) {
        uint32_t pc = (uint32_t)strtoul(tok, NULL, 0);
        if (g_nwatch >= MAX_WATCHES) {
            fprintf(stderr, "[oracle] too many watches\n");
            free(copy);
            exit(2);
        }
        g_watch[g_nwatch].start = pc;
        g_watch[g_nwatch].end = pc + 4;
        g_watch[g_nwatch].flags = M64P_BKP_FLAG_EXEC;
        g_watch[g_nwatch].label = "pc";
        g_nwatch++;
    }
    free(copy);
}

static void usage(void)
{
    fprintf(stderr,
        "usage: rs64_oracle --rom PATH [options]\n"
        "  --watch-write A[:B]   log writes to physical [A,B), e.g. 0x1F3CC0:0x1F3CD0\n"
        "  --watch-read  A[:B]   log reads\n"
        "  --watch-rw    A[:B]   log both\n"
        "  --watch-pc    A[,B...] watch execution at guest PCs\n"
        "  --secs N              run for N seconds (default 120)\n"
        "  --hit-cap N           log at most N hits, then count silently (default 200)\n"
        "  --detail-watch N      always log hits for watch index N\n"
        "  --first-watch N       log the first hit for watch index N\n"
        "  --pc-hist-watch N     summarize writer PCs for watch index N\n"
        "  --post-value-watch N  sample post-store words and final range summary\n"
        "  --post-value-pc A[,B] force one post-store sample for writer PCs\n"
        "  --core PATH           libmupen64plus.dylib built with DEBUGGER=1\n"
        "  --rsp PATH            RSP plugin (default homebrew mupen64plus-rsp-hle)\n"
        "  --datadir PATH        dir holding mupen64plus.ini (default homebrew share dir)\n"
        "  --press SEC:KEY[,...] press KEY at SEC seconds, e.g. --press 6:return,12:return\n"
        "                        KEY is an N64 button name (start a b z dup ddown dleft\n"
        "                        dright cup cdown cleft cright l r) or a raw SDL2 SCANCODE.\n"
        "                        Attaches input-sdl automatically.\n"
        "  --hold-ms N           how long each press is held (default 150)\n"
        "  --input PATH          input plugin (default homebrew mupen64plus-input-sdl)\n"
        "  --video PATH          video plugin (default none -> core dummy, no RDP at all)\n"
        "  --audio PATH          audio plugin (default none -> core dummy)\n"
        "  --oracle-debugger 0|1 set Core/EnableDebugger (default 1; 0 disables watches and traces)\n"
        "  --oracle-emulator N   set Core/R4300Emulator (default 0, pure interpreter)\n"
        "  --vi-trace            log VI width/origin changes - the headless phase signal\n"
        "  --vi-poll             poll VI width/origin through the core API outside callbacks\n"
        "  --status-poll         poll the 18 status-table words through the core API\n"
        "  --pif-trace           log pad-1 buttons as the GAME reads them from PIF RAM\n"
        "  --debug-write VADDR:VALUE  write one 32-bit word on first VI width 320\n"
        "  --state-path PATH     savestate path used by ORACLE_STATE_SMOKE/REACH=1\n"
        "  --verbose             pass through core info messages\n"
        "\n"
        "Watch addresses are PHYSICAL and are masked with 0x1FFFFFFF on input,\n"
        "so 0x1F3CC0 and 0x801F3CC0 both mean physical 0x1F3CC0. The pc= field\n"
        "in each hit is the virtual PC of the storing instruction.\n");
    exit(2);
}

int main(int argc, char **argv)
{
    const char *rom = NULL;
    const char *corepath = "libmupen64plus.dylib";
    const char *rsppath = "/opt/homebrew/lib/mupen64plus/mupen64plus-rsp-hle.dylib";
    const char *datadir = "/opt/homebrew/share/mupen64plus";
    const char *inputpath = NULL;
    const char *configdir = NULL;
    const char *videopath = NULL;
    const char *audiopath = NULL;
    const char *state_path = NULL;
    double secs = 120.0;
    int oracle_debugger = 1;
    int oracle_emulator = 0;
    FILE *f; long romsize; void *rombuf;
    pthread_t th, poll_th;
    int i;

    for (i = 1; i < argc; i++) {
        if (!strcmp(argv[i], "--rom") && i + 1 < argc)             rom = argv[++i];
        else if (!strcmp(argv[i], "--core") && i + 1 < argc)       corepath = argv[++i];
        else if (!strcmp(argv[i], "--rsp") && i + 1 < argc)        rsppath = argv[++i];
        else if (!strcmp(argv[i], "--datadir") && i + 1 < argc)    datadir = argv[++i];
        else if (!strcmp(argv[i], "--configdir") && i + 1 < argc)  configdir = argv[++i];
        else if (!strcmp(argv[i], "--video") && i + 1 < argc)      videopath = argv[++i];
        else if (!strcmp(argv[i], "--audio") && i + 1 < argc)      audiopath = argv[++i];
        else if (!strcmp(argv[i], "--oracle-debugger") && i + 1 < argc) {
            oracle_debugger = atoi(argv[++i]);
            if (oracle_debugger != 0 && oracle_debugger != 1) usage();
        }
        else if (!strcmp(argv[i], "--oracle-emulator") && i + 1 < argc) {
            oracle_emulator = atoi(argv[++i]);
            if (oracle_emulator < 0) usage();
        }
        else if (!strcmp(argv[i], "--secs") && i + 1 < argc)       secs = atof(argv[++i]);
        else if (!strcmp(argv[i], "--hit-cap") && i + 1 < argc)    g_hit_cap = atol(argv[++i]);
        else if (!strcmp(argv[i], "--detail-watch") && i + 1 < argc) {
            int watch = atoi(argv[++i]);
            if (watch >= 0 && watch < MAX_WATCHES)
                g_detail_watch_mask |= 1u << watch;
        }
        else if (!strcmp(argv[i], "--first-watch") && i + 1 < argc)
            g_first_watch = atoi(argv[++i]);
        else if (!strcmp(argv[i], "--pc-hist-watch") && i + 1 < argc)
            g_pc_hist_watch = atoi(argv[++i]);
        else if (!strcmp(argv[i], "--post-value-watch") && i + 1 < argc)
            g_post_value_watch = atoi(argv[++i]);
        else if (!strcmp(argv[i], "--post-value-pc") && i + 1 < argc)
            add_post_value_pcs(argv[++i]);
        else if (!strcmp(argv[i], "--watch-write") && i + 1 < argc)
            add_watch(argv[++i], M64P_BKP_FLAG_WRITE, "write");
        else if (!strcmp(argv[i], "--watch-read") && i + 1 < argc)
            add_watch(argv[++i], M64P_BKP_FLAG_READ, "read");
        else if (!strcmp(argv[i], "--watch-rw") && i + 1 < argc)
            add_watch(argv[++i], M64P_BKP_FLAG_READ | M64P_BKP_FLAG_WRITE, "rw");
        else if (!strcmp(argv[i], "--watch-pc") && i + 1 < argc)
            add_pc_watches(argv[++i]);
        else if (!strcmp(argv[i], "--hold-ms") && i + 1 < argc)    g_hold_ms = atoi(argv[++i]);
        else if (!strcmp(argv[i], "--input") && i + 1 < argc)      inputpath = argv[++i];
        else if (!strcmp(argv[i], "--press") && i + 1 < argc) {
            char *spec = argv[++i], *tok, *save = NULL;
            for (tok = strtok_r(spec, ",", &save); tok; tok = strtok_r(NULL, ",", &save)) {
                char *colon = strchr(tok, ':');
                if (!colon || g_npress >= 256) { fprintf(stderr, "[oracle] bad --press '%s'\n", tok); exit(2); }
                *colon = 0;
                g_press[g_npress].at  = atof(tok);
                g_press[g_npress].sym = keycode(colon + 1);
                g_npress++;
            }
        }
        else if (!strcmp(argv[i], "--vi-trace"))                   g_vi_trace = 1;
        else if (!strcmp(argv[i], "--vi-poll"))                    g_vi_poll = 1;
        else if (!strcmp(argv[i], "--status-poll"))                g_status_poll = 1;
        else if (!strcmp(argv[i], "--pif-trace"))                  g_pif_trace = 1;
        else if (!strcmp(argv[i], "--debug-write") && i + 1 < argc) {
            unsigned addr, value;
            if (sscanf(argv[++i], "%x:%x", &addr, &value) != 2) {
                fprintf(stderr, "[oracle] bad --debug-write '%s'\n", argv[i]);
                return 2;
            }
            g_debug_write_enabled = 1;
            g_debug_write_addr = addr;
            g_debug_write_value = value;
        }
        else if (!strcmp(argv[i], "--state-path") && i + 1 < argc) state_path = argv[++i];
        else if (!strcmp(argv[i], "--verbose"))                    g_verbose = 1;
        else usage();
    }
    if (!rom) usage();
    g_state_smoke = getenv("ORACLE_STATE_SMOKE") != NULL;
    g_state_reach = getenv("ORACLE_STATE_REACH") != NULL;
    g_state_path = state_path;
    if ((g_state_smoke || g_state_reach) && !g_state_path) {
        fprintf(stderr, "[oracle] ORACLE_STATE_SMOKE/REACH=1 requires --state-path\n");
        return 2;
    }

    g_core = dlopen(corepath, RTLD_NOW);
    if (!g_core) { fprintf(stderr, "[oracle] dlopen core: %s\n", dlerror()); return 1; }

#define SYM(v, n) do { *(void **)&v = dlsym(g_core, n); \
    if (!v) { fprintf(stderr, "[oracle] missing %s - is the core built with DEBUGGER=1?\n", n); return 1; } } while (0)
    SYM(pCoreStartup, "CoreStartup");
    SYM(pCoreShutdown, "CoreShutdown");
    SYM(pCoreDoCommand, "CoreDoCommand");
    SYM(pCoreAttachPlugin, "CoreAttachPlugin");
    SYM(pConfigOpenSection, "ConfigOpenSection");
    SYM(pConfigSetParameter, "ConfigSetParameter");
    SYM(pConfigSaveFile, "ConfigSaveFile");
    SYM(pDebugSetCallbacks, "DebugSetCallbacks");
    SYM(pDebugSetRunState, "DebugSetRunState");
    SYM(pDebugStep, "DebugStep");
    SYM(pDebugBreakpointCommand, "DebugBreakpointCommand");
    SYM(pDebugBreakpointTriggeredBy, "DebugBreakpointTriggeredBy");
    SYM(pDebugGetState, "DebugGetState");
    SYM(pDebugMemRead32, "DebugMemRead32");
    SYM(pDebugMemWrite32, "DebugMemWrite32");
#undef SYM

    /* DataPath must hold mupen64plus.ini or the core has no per-ROM settings
     * (save type, count-per-op) and Rogue Squadron in particular is one of
     * the ROMs that needs its entry. Homebrew's share dir has it. */
    if (pCoreStartup(FRONTEND_API_VERSION, configdir, datadir, NULL, core_msg, NULL, NULL)
        != M64ERR_SUCCESS) {
        fprintf(stderr, "[oracle] CoreStartup failed\n"); return 1;
    }

    /* Two settings the debugger needs, and neither defaults the way we want.
     * EnableDebugger is checked once in main_run() - without it init_debugger()
     * never runs and our callbacks are simply never called (silently: the run
     * looks healthy and reports zero hits, which would be a false negative).
     * R4300Emulator=0 is the pure interpreter: memory breakpoints are checked
     * per access there, and the reported PC is exact. */
    {
        m64p_handle core_section;
        int enable = oracle_debugger, interp = oracle_emulator;
        if (pConfigOpenSection("Core", &core_section) == M64ERR_SUCCESS) {
            pConfigSetParameter(core_section, "EnableDebugger", M64TYPE_BOOL, &enable);
            pConfigSetParameter(core_section, "R4300Emulator", M64TYPE_INT, &interp);
        } else {
            fprintf(stderr, "[oracle] WARNING: cannot open Core config section; "
                            "debugger will not activate\n");
        }
    }

    f = fopen(rom, "rb");
    if (!f) { fprintf(stderr, "[oracle] cannot open %s\n", rom); return 1; }
    fseek(f, 0, SEEK_END); romsize = ftell(f); fseek(f, 0, SEEK_SET);
    rombuf = malloc(romsize);
    if (fread(rombuf, 1, romsize, f) != (size_t)romsize) {
        fprintf(stderr, "[oracle] short read on %s\n", rom); return 1;
    }
    fclose(f);

    if (pCoreDoCommand(M64CMD_ROM_OPEN, (int)romsize, rombuf) != M64ERR_SUCCESS) {
        fprintf(stderr, "[oracle] ROM_OPEN failed\n"); return 1;
    }
    free(rombuf);

    /* Order matters: the core expects gfx, audio, input, RSP and warns
     * "plugins are attached in wrong order" otherwise. Anything left
     * unattached gets the core's dummy. */
    if (videopath) attach_plugin(videopath, M64PLUGIN_GFX);
    if (audiopath) attach_plugin(audiopath, M64PLUGIN_AUDIO);
    if (g_npress > 0 && !inputpath)
        inputpath = "/opt/homebrew/lib/mupen64plus/mupen64plus-input-sdl.dylib";
    if (inputpath)
        g_have_input = (attach_plugin(inputpath, M64PLUGIN_INPUT) == 0);
    attach_plugin(rsppath, M64PLUGIN_RSP);

    if (pDebugSetCallbacks(dbg_init, dbg_update, dbg_vi) != M64ERR_SUCCESS) {
        fprintf(stderr, "[oracle] DebugSetCallbacks failed\n"); return 1;
    }

    g_t0 = now_s();
    g_poll_running = g_vi_poll || g_status_poll;
    if (g_poll_running)
        pthread_create(&poll_th, NULL, vi_poller, NULL);
    pthread_create(&th, NULL, director, &secs);

    printf("[oracle] running %s for %.0fs with %d watch(es), debugger=%d emulator=%d\n",
           rom, secs, g_nwatch, oracle_debugger, oracle_emulator);
    fflush(stdout);
    pCoreDoCommand(M64CMD_EXECUTE, 0, NULL);

    g_poll_running = 0;
    if (g_vi_poll || g_status_poll)
        pthread_join(poll_th, NULL);

    printf("[oracle] done: %ld hit(s) in %.1fs wall, %ld VI (~%.1fs emulated)\n",
           g_hits, now_s() - g_t0, g_vis, g_vis / 60.0);
    if (g_post_value_watch >= 0 && g_post_value_watch < g_nwatch) {
        int j;
        summarize_post_snapshot(g_post_value_watch);
        printf("[oracle] post-value watch=%d range=[0x%08x,0x%08x) samples=%ld unique=%d overflow=%ld\n",
               g_post_value_watch, g_watch[g_post_value_watch].start,
               g_watch[g_post_value_watch].end, g_post_value_samples,
               g_n_post_value_hist, g_post_value_overflow);
        for (j = 0; j < g_n_post_value_hist; j++)
            printf("[oracle] post-value value=0x%08x n=%ld\n",
                   g_post_value_hist[j].value, g_post_value_hist[j].n);
        for (j = 0; j < g_n_post_value_pc; j++)
            printf("[oracle] post-value-pc pc=0x%08x samples=%ld zero=%ld nonzero=%ld\n",
                   g_post_value_pc[j].pc, g_post_value_pc[j].samples,
                   g_post_value_pc[j].zero_words, g_post_value_pc[j].nonzero_words);
        if (g_post_value_pc_overflow)
            printf("[oracle] post-value-pc overflow=%ld\n", g_post_value_pc_overflow);
        for (j = 0; j < g_n_post_value_requested_pc; j++)
            printf("[oracle] post-target-summary pc=0x%08x seen=%d addr=0x%08x value=0x%08x\n",
                   g_post_value_requested_pc[j], g_post_value_requested_seen[j],
                   g_post_value_requested_addr[j], g_post_value_requested_value[j]);
        for (j = 0; j < g_n_post_value_requested_pc; j++) {
            int k;
            printf("[oracle] post-target-rows pc=0x%08x n=%d/%d\n",
                   g_post_value_requested_pc[j],
                   g_n_post_value_requested_rows[j],
                   MAX_POST_VALUE_ROWS_PER_PC);
            for (k = 0; k < g_n_post_value_requested_rows[j]; k++)
                printf("[oracle] post-target-row-final pc=0x%08x vi=%ld width=%u origin=0x%08x addr=0x%08x value=0x%08x\n",
                       g_post_value_requested_pc[j],
                       g_post_value_requested_rows[j][k].vi,
                       g_post_value_requested_rows[j][k].width,
                       g_post_value_requested_rows[j][k].origin,
                       g_post_value_requested_rows[j][k].addr,
                       g_post_value_requested_rows[j][k].value);
        }
        if (g_post_snapshot_valid)
            printf("[oracle] post-value snapshot bytes=%lu nonzero=%lu fnv=0x%08x\n",
                   g_post_snapshot_bytes, g_post_snapshot_nonzero,
                   g_post_snapshot_fnv);
    }
    for (int i = 0; i < g_nwatch; i++)
        printf("[oracle] watch %s [0x%08x,0x%08x): %ld hit(s), %ld read(s), %ld write(s)\n",
               g_watch[i].label, g_watch[i].start, g_watch[i].end,
               g_watch[i].hits, g_watch[i].read_hits, g_watch[i].write_hits);
    if (g_pc_hist_watch >= 0 && g_pc_hist_watch < g_nwatch) {
        int i;
        printf("[oracle] writer-pc watch=%d range=[0x%08x,0x%08x)\n",
               g_pc_hist_watch, g_watch[g_pc_hist_watch].start,
               g_watch[g_pc_hist_watch].end);
        for (i = 0; i < g_n_writer_pc[g_pc_hist_watch]; i++)
            printf("[oracle] writer-pc pc=0x%08x n=%ld\n",
                   g_writer_pc[g_pc_hist_watch][i].pc,
                   g_writer_pc[g_pc_hist_watch][i].n);
        if (g_writer_pc_overflow[g_pc_hist_watch])
            printf("[oracle] writer-pc overflow=%ld\n",
                   g_writer_pc_overflow[g_pc_hist_watch]);
    }
    printf("[oracle] execution watch hits: %ld\n", g_pc_hits);
    for (int i = 0; i < g_n_exec_prev; i++)
        printf("[oracle] exec-prev pc=0x%08x prev=0x%08x n=%ld\n",
               g_exec_prev[i].pc, g_exec_prev[i].prev, g_exec_prev[i].n);
    if (g_exec_prev_overflow)
        printf("[oracle] exec-prev overflow=%ld (unique pairs truncated at %d)\n",
               g_exec_prev_overflow, MAX_EXEC_PREV);
    /* Materialise the config so the input mapping is inspectable. Without
     * this nothing is ever written and the key->button mapping the presses
     * rely on is invisible in-memory defaults - i.e. an unverifiable
     * instrument. Look at [Input-SDL-Control1] in
     * ~/.config/mupen64plus/mupen64plus.cfg. */
    if (pConfigSaveFile() != M64ERR_SUCCESS)
        fprintf(stderr, "[oracle] ConfigSaveFile failed (pass --configdir to a writable dir "
                        "if you want to inspect the input mapping)\n");
    pCoreDoCommand(M64CMD_ROM_CLOSE, 0, NULL);
    pCoreShutdown();
    return g_hits > 0 ? 0 : 3;      /* rc 3 = clean run, zero hits (a real answer) */
}
