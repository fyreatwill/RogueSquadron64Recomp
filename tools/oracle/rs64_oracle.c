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

#include "m64p_types.h"
#include "m64p_frontend.h"
#include "m64p_debugger.h"

/* Lives in the core's src/main/version.h, which is not part of the public
 * api/ headers. CoreStartup only compares the top 16 bits. */
#ifndef FRONTEND_API_VERSION
#define FRONTEND_API_VERSION 0x020106
#endif

#define MAX_WATCHES 64

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

struct watch {
    uint32_t start, end;
    unsigned int flags;
    const char *label;
    long hits;
};
static struct watch g_watch[MAX_WATCHES];
static int g_nwatch;
static long g_hits;
static long g_hit_cap = 200;          /* stop logging after this many, keep running */
static unsigned int g_detail_watch_mask;
static int g_verbose;
static int g_watches_armed;
static int g_positive_watch_removed;
static long g_pc_hits;

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
    pDebugBreakpointTriggeredBy(&flags, &accessed);

    g_hits++;
    for (i = 0; i < g_nwatch; i++) {
        if (accessed >= g_watch[i].start && accessed < g_watch[i].end)
            g_watch[i].hits++;
        if ((g_watch[i].flags & M64P_BKP_FLAG_EXEC) &&
            pc >= g_watch[i].start && pc < g_watch[i].end) {
            g_watch[i].hits++;
            g_pc_hits++;
        }
        if (accessed >= g_watch[i].start && accessed < g_watch[i].end &&
            (g_detail_watch_mask & (1u << i)))
            detail_hit = 1;
    }
    if (!g_positive_watch_removed && g_nwatch > 0 && g_watch[0].hits == 10000) {
        int rc = pDebugBreakpointCommand(M64P_BKP_CMD_REMOVE_IDX, 0, NULL);
        printf("[oracle] positive-control threshold reached: watch index 0 callbacks=%ld; removal rc=%d; watch index 1 remains armed\n",
               g_watch[0].hits, rc);
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
        if (g_hits == g_hit_cap)
            printf("[oracle] hit cap %ld reached, counting silently from here\n", g_hit_cap);
        fflush(stdout);
    }

    pDebugSetRunState(M64P_DBG_RUNSTATE_RUNNING);
    pDebugStep();
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
#define VI_ORIGIN_ADDR 0xA4400004u   /* KSEG1: uncached, no TLB, masks to 0x04400004 */
#define VI_WIDTH_ADDR  0xA4400008u

/* PIF RAM holds the SI's controller readout: after a 0x01 (read controller)
 * command the button word for pad 1 lands at physical 0x1FC007C4. Reading it
 * answers the one question a headless run cannot otherwise settle - does the
 * GAME see the buttons we inject, or are we only talking to the plugin? */
#define PIF_PAD1_ADDR  0xBFC007C4u
#define N64_BTN_START  0x00001000u

static long g_vis;
static int g_vi_trace;
static int g_vi_poll;
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

static void *vi_poller(void *arg)
{
    unsigned last_width = 0xFFFFFFFFu, last_origin = 0xFFFFFFFFu;
    double last_raw_log = -1e9;
    (void)arg;

    sleep_s(0.1);
    while (g_poll_running) {
        double t = now_s() - g_t0;
        unsigned width = pDebugMemRead32(VI_WIDTH_ADDR);
        unsigned origin = pDebugMemRead32(VI_ORIGIN_ADDR);
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
        "  --pif-trace           log pad-1 buttons as the GAME reads them from PIF RAM\n"
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
        else if (!strcmp(argv[i], "--pif-trace"))                  g_pif_trace = 1;
        else if (!strcmp(argv[i], "--verbose"))                    g_verbose = 1;
        else usage();
    }
    if (!rom) usage();

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
    g_poll_running = g_vi_poll;
    if (g_vi_poll)
        pthread_create(&poll_th, NULL, vi_poller, NULL);
    pthread_create(&th, NULL, director, &secs);

    printf("[oracle] running %s for %.0fs with %d watch(es), debugger=%d emulator=%d\n",
           rom, secs, g_nwatch, oracle_debugger, oracle_emulator);
    fflush(stdout);
    pCoreDoCommand(M64CMD_EXECUTE, 0, NULL);

    g_poll_running = 0;
    if (g_vi_poll)
        pthread_join(poll_th, NULL);

    printf("[oracle] done: %ld hit(s) in %.1fs wall, %ld VI (~%.1fs emulated)\n",
           g_hits, now_s() - g_t0, g_vis, g_vis / 60.0);
    for (int i = 0; i < g_nwatch; i++)
        printf("[oracle] watch %s [0x%08x,0x%08x): %ld hit(s)\n",
               g_watch[i].label, g_watch[i].start, g_watch[i].end,
               g_watch[i].hits);
    printf("[oracle] execution watch hits: %ld\n", g_pc_hits);
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
