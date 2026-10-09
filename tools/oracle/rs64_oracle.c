#include <math.h>
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
#include <signal.h>

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
#define MAX_PC_HIST_PHASES 16
#define MAX_POST_VALUE_HIST 64
#define MAX_POST_VALUE_PCS 512
#define MAX_POST_VALUE_SAMPLES 256
#define MAX_POST_VALUE_ROWS_PER_PC 16
#define MAX_POST_VALUE_SEQUENCE_ROWS 16384
#define MAX_POST_VALUE_PC_DETAIL_ROWS 16384
#define MAX_DETAIL_HANGAR_READ_ROWS 65536u
#define MAX_VI_SWAP_PHASE_ROWS 256
#define MAX_MODE_DUMP_ROWS 4096
#define MAX_VI_CONTEXT_ROWS 1024
#define MAX_PC_FIELD_DUMP_PCS 32
#define MAX_PC_FIELD_DUMP_ROWS 32768
#define MAX_STORE_FIELD_DUMP_PCS 32
#define MAX_STORE_FIELD_DUMP_ROWS 32768
#define MAX_PC_TASK_DUMP_ROWS 8192
#define MAX_ORDINAL_WRITER_KEYS 4096
#define MAX_PHASE_SNAPSHOTS 8
#define VI_ORIGIN_ADDR 0xA4400004u
#define VI_WIDTH_ADDR  0xA4400008u
#define VI_CURRENT_ADDR 0xA4400010u
#define VI_NEXT_PTR_ADDR 0x80039214u
#define RDRAM_SIZE 0x00800000u
#define VI_SWAP_PC 0x80035500u
#define AI_SET_NEXT_PC 0x80029E80u

static void *g_core;
static double g_t0;
static double now_s(void);

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
static void *     (*pDebugGetCPUDataPtr)(m64p_dbg_cpu_data);

struct watch {
    uint32_t start, end;
    unsigned int flags;
    const char *label;
    long hits;
    long read_hits;
    long write_hits;
    int breakpoint_idx;
    int armed;
};
static struct watch g_watch[MAX_WATCHES];
struct writer_pc {
    uint32_t pc;
    long n;
};
static struct writer_pc g_writer_pc[MAX_WATCHES][MAX_WRITER_PCS];
static int g_n_writer_pc[MAX_WATCHES];
static long g_writer_pc_overflow[MAX_WATCHES];
struct writer_pc_hist {
    struct writer_pc entries[MAX_WRITER_PCS];
    int n;
    long overflow;
};
static uint32_t g_pc_hist_phase_origin[MAX_PC_HIST_PHASES];
static uint32_t g_pc_hist_phase_width[MAX_PC_HIST_PHASES];
static long g_pc_hist_phase_vis[MAX_PC_HIST_PHASES];
static struct writer_pc_hist
    g_pc_hist_phase[MAX_PC_HIST_PHASES][MAX_WATCHES];
static int g_n_pc_hist_phase;
static int g_nwatch;
static long g_hits;
static volatile sig_atomic_t g_checkpoint_requested;
static long g_hit_cap = 200;          /* stop logging after this many, keep running */
static unsigned int g_detail_watch_mask;
static unsigned int g_detail_hangar_read_rows;
static int g_first_watch = -1;
static uint64_t g_pc_hist_watch_mask;
static uint64_t g_post_value_watch_mask;
static uint64_t g_phase_snapshot_watch_mask;
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
struct post_value_requested_sequence_row {
    long ordinal;
    uint32_t pc;
    long vi;
    uint32_t addr;
    uint32_t value;
    int sentinel;
};
static struct post_value_requested_sequence_row
    g_post_value_requested_sequence[MAX_POST_VALUE_SEQUENCE_ROWS];
static int g_n_post_value_requested_sequence;
static long g_post_value_requested_sequence_count[32];
static long g_post_value_requested_sequence_overflow;
struct post_value_requested_tuple {
    long vi;
    uint32_t addr;
    uint32_t value;
    int valid;
};
struct post_value_requested_class {
    long samples;
    struct post_value_requested_tuple first;
    struct post_value_requested_tuple last;
};
static struct post_value_requested_class
    g_post_value_requested_classes[32][2];
struct post_value_pc_detail_row {
    uint32_t pc;
    long vi;
    uint32_t width;
    uint32_t origin;
    uint32_t addr;
    uint32_t value;
};
static struct post_value_pc_detail_row
    g_post_value_pc_detail_rows[MAX_POST_VALUE_PC_DETAIL_ROWS];
static int g_n_post_value_pc_detail_rows;
static long g_post_value_pc_detail_overflow;
static int g_post_value_pc_detail;
static int g_post_value_pc_detail_phase;
static uint32_t g_post_value_pc_detail_origin;
static uint32_t g_post_value_pc_detail_width;
struct post_value_entry {
    uint32_t value;
    long n;
};
struct post_value_pc_entry {
    uint32_t pc;
    long samples;
    long zero_words;
    long nonzero_words;
    long scalar_samples;
    long scalar_zero;
    long scalar_nonzero;
    long scalar_mismatch;
};
struct post_value_stats {
    struct post_value_entry hist[MAX_POST_VALUE_HIST];
    struct post_value_pc_entry pc[MAX_POST_VALUE_PCS];
    int n_hist;
    int n_pc;
    long samples;
    long overflow;
    long pc_overflow;
    uint32_t snapshot_fnv;
    unsigned long snapshot_nonzero;
    unsigned long snapshot_bytes;
    int snapshot_valid;
};
static struct post_value_stats g_post_value_stats[MAX_WATCHES];
struct phase_snapshot {
    uint32_t origin;
    uint32_t width;
    long vi;
    uint32_t fnv;
    unsigned long nonzero;
    unsigned long bytes;
    int valid;
    unsigned char values[4096];
};
static struct phase_snapshot g_phase_snapshots[MAX_WATCHES][MAX_PHASE_SNAPSHOTS];
static int g_post_value_pending;
static int g_post_value_pending_target = -1;
static int g_post_value_pending_watch = -1;
static int g_post_value_armed;
static uint32_t g_post_value_addr;
static uint32_t g_post_value_pc_addr;
static uint32_t g_post_store_mask;
static uint32_t g_post_store_expected;
static long g_post_value_pending_vi;
static uint32_t g_post_value_pending_width;
static uint32_t g_post_value_pending_origin;
static long g_vis;
static int g_verbose;
static int g_watches_armed;
static int g_defer_exec_watches;
static int g_exec_watches_phase_armed;
static int g_positive_watch_removed;
static uint32_t gpr32(int idx);
static uint32_t debug_mem_u8(uint32_t guest);
static uint32_t debug_mem_u32(uint32_t guest);
struct ai_output_bucket {
    const char *name;
    uint32_t width;
    uint32_t origin;
    long calls;
    long rows;
    long nonzero_rows;
    long clipped, total;
    double sumsq;
};
static struct ai_output_bucket g_ai_output[] = {
    { "pre-title", 0, 0, 0, 0, 0 },
    { "title", 1024, 0x00790400u, 0, 0, 0 },
    { "hangar", 512, 0x006AB400u, 0, 0, 0 },
};

static void dump_ai_output(void)
{
    uint32_t width = pDebugMemRead32(VI_WIDTH_ADDR);
    uint32_t origin = pDebugMemRead32(VI_ORIGIN_ADDR);
    uint32_t addr = gpr32(4);
    uint32_t len = gpr32(5);
    int bucket = 0;
    uint32_t fnv = 2166136261u;
    uint32_t nonzero = 0;
    uint32_t i;
    if (width == 1024u && origin == 0x00790400u) bucket = 1;
    else if (width == 512u && origin == 0x006AB400u) bucket = 2;
    g_ai_output[bucket].calls++;
    if (bucket == 0 || len == 0 || len > 0x40000u) return;
    for (i = 0; i < len; i++) {
        uint32_t byte = debug_mem_u8(addr + i);
        fnv = (fnv * 16777619u) ^ byte;
        nonzero += byte != 0;
    }
    g_ai_output[bucket].rows++;
    g_ai_output[bucket].nonzero_rows += nonzero != 0;
    {   /* s4238: clip fraction (|x|>=32000) + RMS, big-endian s16 samples, matches port [ai-output-clip] */
        double sumsq = 0.0; long clipped = 0, total = 0;
        for (i = 0; i + 1 < len; i += 2) {
            int v = (int16_t)((debug_mem_u8(addr + i) << 8) | debug_mem_u8(addr + i + 1));
            if (v >= 32000 || v <= -32000) clipped++;
            sumsq += (double)v * v; total++;
        }
        g_ai_output[bucket].clipped += clipped; g_ai_output[bucket].total += total; g_ai_output[bucket].sumsq += sumsq;
        if (g_ai_output[bucket].rows <= 20 || (g_ai_output[bucket].rows % 128) == 0)
            printf("[ai-output-clip] bucket=%s n=%ld clipped=%ld total=%ld rms=%.1f\n",
                   g_ai_output[bucket].name, g_ai_output[bucket].rows, clipped, total, total ? sqrt(sumsq / total) : 0.0);
    }
    if (g_ai_output[bucket].rows <= 20 || (g_ai_output[bucket].rows % 128) == 0) {
        printf("[ai-output] bucket=%s width=%u origin=0x%06x addr=0x%08x len=%u fnv=0x%08x nz=%u n=%ld\n",
               g_ai_output[bucket].name, width, origin, addr, len, fnv, nonzero,
               g_ai_output[bucket].rows);
        fflush(stdout);
    }
}
static long g_pc_hits;
static int g_gpr_ctl_printed;
static long g_exec_logged;
#define EXEC_LOG_CAP 64
#define MAX_EXEC_PREV 128
#define MAX_PC_PHASE_LOG_ORIGINS 8
struct pc_phase_log_bucket {
    uint32_t origin;
    uint32_t width;
};
static struct pc_phase_log_bucket
    g_pc_phase_log[MAX_PC_PHASE_LOG_ORIGINS];
static int g_n_pc_phase_log_origin;
static uint32_t g_latched_phase_width;
static uint32_t g_latched_phase_origin;
static uint32_t g_mode_dump_pc;
static int g_mode_dump_enabled;
static long g_mode_dump_rows;
static long g_mode_dump_overflow;
struct mode_descriptor_snapshot {
    int valid;
    uint32_t mode_ptr;
    uint32_t fld0_origin;
    uint32_t fld0_y_scale;
    uint32_t fld1_origin;
    uint32_t fld1_y_scale;
};
static struct mode_descriptor_snapshot g_last_mode_descriptor;
static uint32_t g_post_swap_table_pc;
static int g_post_swap_table_enabled;
static int g_post_swap_any_vi;
struct post_swap_pending {
    int valid;
    uint32_t pre_width;
    uint32_t pre_origin;
    uint32_t prev_pc;
    uint32_t a0_phys;
    struct mode_descriptor_snapshot mode;
};
static struct post_swap_pending g_post_swap_pending;
static long g_post_swap_latched;
static long g_post_swap_joined;
static long g_post_swap_dropped;
static long g_post_swap_overflow;
static uint32_t g_vi_context_table_pc;
static int g_vi_context_table_enabled;
static int g_vi_context_any_vi;
struct vi_context_snapshot {
    int context_valid;
    int mode_valid;
    uint32_t context_ptr;
    uint32_t state;
    uint32_t framep_phys;
    uint32_t mode_ptr;
    uint32_t current_field;
    uint32_t fld0_origin;
    uint32_t fld0_y_scale;
    uint32_t fld1_origin;
    uint32_t fld1_y_scale;
    uint32_t candidate0;
    uint32_t candidate1;
};
struct vi_context_pending {
    int valid;
    struct vi_context_snapshot snapshot;
};
static struct vi_context_pending g_vi_context_pending;
static long g_vi_context_latched;
static long g_vi_context_joined;
static long g_vi_context_dropped;
static long g_vi_context_overflow;
struct pc_field_dump_row {
    uint32_t object;
    uint32_t s0;
    uint32_t s1;
    uint32_t prev_pc;
    uint32_t ra;
    uint32_t source_word;
    uint32_t source_byte;
    uint32_t branch_selector;
    uint32_t branch_state;
    uint32_t cursor;
    uint32_t base_198;
    uint32_t selected_addr;
    uint32_t selected_word;
    uint32_t state_18a;
    uint32_t state_18c;
    long n;
};
struct pc_field_dump_bucket {
    uint32_t pc;
    struct pc_field_dump_row rows[MAX_PC_FIELD_DUMP_ROWS];
    int n_rows;
    long hits;
    long overflow;
};
static struct pc_field_dump_bucket
    g_pc_field_dump[MAX_PC_FIELD_DUMP_PCS];
static int g_n_pc_field_dump;
static int g_pc_field_dump_any_phase;
static int g_boundary_join_enabled;
struct boundary_join_row {
    uint32_t pc;
    uint32_t width;
    uint32_t origin;
    long task_n;
    uint32_t task_ptr;
    uint32_t data_ptr;
    uint32_t data_size;
    uint64_t event_ordinal;
    uint32_t object;
    uint32_t cursor;
    uint32_t selected_addr;
    uint32_t selected_word;
    uint32_t branch_state;
    uint32_t instruction;
    uint32_t source_reg;
    uint32_t source_value;
    long n;
};
#define MAX_BOUNDARY_JOIN_ROWS 2048
static struct boundary_join_row g_boundary_join_rows[MAX_BOUNDARY_JOIN_ROWS];
static int g_n_boundary_join_rows;
static long g_boundary_join_hits;
static long g_boundary_join_no_task;
static long g_boundary_join_overflow;
struct c904_witness_row {
    uint32_t pc;
    uint32_t width;
    uint32_t origin;
    uint32_t prev_pc;
    uint32_t object;
    uint32_t input;
    uint32_t input_w0;
    uint32_t input_w1;
    uint32_t input_words[8];
    uint32_t v0;
    uint32_t a2;
    uint32_t a3;
    uint32_t s1;
    uint32_t selected_addr;
    uint32_t selected_word;
    int family;
    long n;
};
#define MAX_C904_WITNESS_ROWS 512
static struct c904_witness_row g_c904_witness_rows[MAX_C904_WITNESS_ROWS];
static int g_c904_witness_enabled;
static long g_c904_witness_hits;
static long g_c904_witness_overflow;
static int g_c904_task_join_enabled;
static long g_c904_task_join_matched;
static long g_c904_task_join_unmatched;
static long g_c904_task_join_overflow;
struct c904_task_join_row {
    uint32_t pc;
    uint32_t width;
    uint32_t origin;
    uint32_t task_ptr;
    uint32_t data_ptr;
    uint32_t data_size;
    uint32_t input;
    uint32_t input_w0;
    uint32_t input_w1;
    uint32_t input_words[8];
    uint32_t selected_addr;
    uint32_t selected_word;
    uint32_t payload[8];
    long n;
};
#define MAX_C904_TASK_JOIN_ROWS 1536
static struct c904_task_join_row
    g_c904_task_join_rows[MAX_C904_TASK_JOIN_ROWS];
static int g_n_c904_task_join_rows;
struct c904_input_span {
    uint32_t input;
    uint32_t width;
    uint32_t origin;
    long n;
};
#define MAX_C904_INPUT_SPANS 128
static struct c904_input_span g_c904_input_spans[MAX_C904_INPUT_SPANS];
static int g_n_c904_input_spans;
static long g_c904_input_writer_hits;
struct store_field_dump_pc {
    uint32_t pc;
    uint64_t watch_mask;
};
struct store_field_dump_row {
    int watch;
    uint32_t pc;
    uint32_t store_addr;
    uint32_t instruction;
    uint32_t effective_addr;
    uint32_t source_reg;
    uint32_t source_value;
    uint32_t scalar_mask;
    uint32_t pre_store_word;
    uint32_t ra;
    uint32_t a0;
    uint32_t a1;
    uint32_t a2;
    uint32_t t0;
    uint32_t t1;
    uint32_t s0;
    uint32_t s1;
    uint32_t source_word;
    uint32_t source_byte;
    uint32_t branch_selector;
    uint32_t branch_state;
    long n;
};
static struct store_field_dump_pc
    g_store_field_dump_pc[MAX_STORE_FIELD_DUMP_PCS];
static int g_n_store_field_dump_pc;
static unsigned int g_store_field_dump_all_mask;
static struct store_field_dump_row
    g_store_field_dump_rows[MAX_STORE_FIELD_DUMP_ROWS];
static int g_n_store_field_dump_rows;
static long g_store_field_dump_hits;
static long g_store_field_dump_overflow;
static long g_store_field_dump_candidate_callbacks;
static int g_store_field_dump_any_phase;
static uint32_t g_pc_task_dump_pc;
static int g_pc_task_dump_enabled;
static uint32_t g_pc_task_dump_type = 2; /* 0 = any type */
struct pc_task_dump_row {
    long task_n;
    uint64_t event_ordinal;
    uint32_t task_ptr;
    uint32_t task_phys;
    uint32_t type;
    uint32_t data_ptr;
    uint32_t data_size;
    uint32_t output_buff;
    uint32_t output_buff_size;
    uint32_t yield_data_ptr;
    uint32_t yield_data_size;
    uint32_t data_ptr_plus_100;
    uint32_t field_phys;
    uint32_t published_words[4];
    uint8_t published_valid[4];
    uint32_t width;
    uint32_t origin;
};
static struct pc_task_dump_row
    g_pc_task_dump_rows[MAX_PC_TASK_DUMP_ROWS];
static long g_pc_task_dump_phase_hits;
static long g_pc_task_dump_type2_rows;
static long g_pc_task_dump_invalid;
static long g_pc_task_dump_non_type2;
static long g_pc_task_dump_overflow;
static int g_n_pc_task_dump_rows;
static int g_pc_task_join_enabled;
static int g_pc_phase_quiet;
static int g_ordinal_join_enabled;
static uint64_t g_event_ordinal;
#define MAX_ORDINAL_WRITES 2097152
struct ordinal_write_row {
    int watch;
    uint32_t pc;
    uint32_t store_addr;
    uint32_t instruction;
    uint32_t effective_addr;
    uint32_t source_reg;
    uint32_t source_value;
    uint32_t scalar_mask;
    uint32_t pre_store_word;
    uint32_t post_store_word;
    uint32_t width;
    uint32_t origin;
    uint64_t event_ordinal;
};
static struct ordinal_write_row g_ordinal_writes[MAX_ORDINAL_WRITES];
static int g_n_ordinal_writes;
static long g_ordinal_write_overflow;
struct published_word_stats {
    long joined, in_span, unsupported;
    long source_match, source_mismatch, post_match, post_mismatch;
    long no_task;
};
static struct published_word_stats g_published_word_stats[MAX_PC_PHASE_LOG_ORIGINS][4][4];
struct published_word_key {
    uint32_t width;
    uint32_t origin;
    int writer_class;
    int value_class;
    long joined;
    long in_span;
    long unsupported;
    long source_match;
    long post_match;
    long source_mismatch;
    long post_mismatch;
    long no_task;
};
#define MAX_PUBLISHED_WORD_KEYS 256
struct ordinal_writer_key {
    uint32_t width;
    uint32_t origin;
    int watch;
    uint32_t pc;
    uint32_t effective_addr;
    int writer_class;
    int value_class;
    long nearest;
    long before;
    long after;
    long equal;
    long no_task;
};

#define MAX_SPAN_WRITER_KEYS 2048
struct span_writer_key {
    uint32_t width;
    uint32_t origin;
    int watch;
    int writer_class;
    int value_class;
    long joined;
    long in_data_span;
    long in_plus_100;
    long outside;
    long no_task;
};

static int ordinal_writer_class(uint32_t pc)
{
    if (pc == 0x80090DE4u || pc == 0x80090B68u)
        return 1;
    if (pc == 0x80090CA4u || pc == 0x80091078u)
        return 2;
    return 3;
}

static const char *ordinal_writer_class_name(int class_id)
{
    if (class_id == 1) return "semantic";
    if (class_id == 2) return "maintenance";
    return "other";
}

static int ordinal_value_class(const struct ordinal_write_row *write)
{
    if (write->scalar_mask == 0)
        return 3;
    return (write->source_value & write->scalar_mask) == 0 ? 1 : 2;
}

static const char *ordinal_value_class_name(int class_id)
{
    if (class_id == 1) return "scalar-zero";
    if (class_id == 2) return "scalar-nonzero";
    return "unsupported";
}
#define MAX_PC_RANGE_TASK_ROWS 16384
#define MAX_PC_RANGE_TASK_ROWS_PER_PHASE 8192
struct pc_range_task_row {
    uint32_t pc;
    uint32_t width;
    uint32_t origin;
    uint32_t a0;
    uint32_t a0_word;
    uint32_t output_buff;
    uint32_t output_buff_size;
    uint32_t data_ptr;
    uint32_t data_size;
    uint32_t yield_data_ptr;
    uint32_t yield_data_size;
    long n;
};
static int g_pc_range_task_dump_enabled;
static struct pc_range_task_row
    g_pc_range_task_rows[MAX_PC_RANGE_TASK_ROWS];
static int g_n_pc_range_task_rows;
static long g_pc_range_task_hits;
static long g_pc_range_task_invalid;
static long g_pc_range_task_overflow;
struct pc_task_join_row {
    uint32_t width;
    uint32_t origin;
    uint32_t task_ptr;
    uint32_t data_ptr;
    uint32_t data_size;
    uint32_t s1;
    uint32_t prev_pc;
    uint32_t ra;
    long n;
};
static struct pc_task_join_row
    g_pc_task_join_rows[MAX_PC_TASK_DUMP_ROWS];
static int g_n_pc_task_join_rows;
static long g_pc_task_join_overflow;
static const uint32_t g_published_word_addrs[4] = {
    0x00171CE0u, 0x00173B20u, 0x00171E70u, 0x00173CB0u
};

static uint32_t debug_rdram_addr(uint32_t physical);
static uint32_t to_phys(uint32_t a);
static uint32_t scalar_store_mask(uint32_t instruction, uint32_t address);

/* GPR file is int64_t[32] (r4300_regs). Print the 32-bit guest view. */
static uint32_t gpr32(int idx)
{
    int64_t *gpr;
    if (!pDebugGetCPUDataPtr)
        return 0;
    gpr = (int64_t *)pDebugGetCPUDataPtr(M64P_CPU_REG_REG);
    if (!gpr)
        return 0;
    return (uint32_t)gpr[idx];
}

static void print_gpr_fields(void)
{
    printf(" v0=0x%08x s1=0x%08x a0=0x%08x a1=0x%08x a2=0x%08x s0=0x%08x v1=0x%08x s2=0x%08x s3=0x%08x s4=0x%08x s5=0x%08x s6=0x%08x fp=0x%08x ra=0x%08x",
           gpr32(2), gpr32(17), gpr32(4), gpr32(5), gpr32(6), gpr32(16), gpr32(3),
           gpr32(18), gpr32(19), gpr32(20), gpr32(21), gpr32(22), gpr32(30), gpr32(31));
}

static int pc_phase_log_match(void)
{
    unsigned width;
    unsigned origin;
    int i;

    if (g_n_pc_phase_log_origin == 0)
        return 0;
    width = pDebugMemRead32(VI_WIDTH_ADDR);
    origin = pDebugMemRead32(VI_ORIGIN_ADDR);
    for (i = 0; i < g_n_pc_phase_log_origin; i++) {
        if (width == g_pc_phase_log[i].width &&
            origin == g_pc_phase_log[i].origin)
            return 1;
    }
    return 0;
}

static int store_field_phase_log_match(void)
{
    uint32_t width = pDebugMemRead32(VI_WIDTH_ADDR);
    uint32_t origin = pDebugMemRead32(VI_ORIGIN_ADDR);
    int i;
    for (i = 0; i < g_n_pc_phase_log_origin; i++)
        if (width == g_pc_phase_log[i].width &&
            origin == g_pc_phase_log[i].origin)
            return 1;
    return 0;
}

static int pc_task_dump_phase_match(void)
{
    unsigned width;
    unsigned origin;
    int i;

    if (g_n_pc_phase_log_origin > 0)
        return pc_phase_log_match();
    if (g_n_pc_hist_phase == 0)
        return 0;
    width = pDebugMemRead32(VI_WIDTH_ADDR);
    origin = pDebugMemRead32(VI_ORIGIN_ADDR);
    for (i = 0; i < g_n_pc_hist_phase; i++) {
        if (width == g_pc_hist_phase_width[i] &&
            origin == g_pc_hist_phase_origin[i])
            return 1;
    }
    return 0;
}

static uint32_t debug_mem_u8(uint32_t guest)
{
    uint32_t aligned = guest & ~3u;
    uint32_t value = pDebugMemRead32(debug_rdram_addr(aligned));
    unsigned shift = 24u - ((guest & 3u) * 8u);
    return (value >> shift) & 0xFFu;
}

static uint32_t debug_mem_u32(uint32_t guest)
{
    return pDebugMemRead32(debug_rdram_addr(guest & ~3u));
}

static uint32_t debug_mem_u16(uint32_t guest)
{
    uint32_t aligned = guest & ~3u;
    uint32_t value = pDebugMemRead32(debug_rdram_addr(aligned));
    unsigned shift = (guest & 2u) ? 0u : 16u;
    return (value >> shift) & 0xFFFFu;
}

static int pc_field_dump_index(uint32_t pc)
{
    int i;
    for (i = 0; i < g_n_pc_field_dump; i++) {
        if (g_pc_field_dump[i].pc == pc)
            return i;
    }
    return -1;
}

static void dump_pc_field(uint32_t pc)
{
    struct pc_field_dump_bucket *bucket;
    struct pc_field_dump_row row;
    int index;
    int i;

    if (!g_pc_field_dump_any_phase && !pc_phase_log_match())
        return;
    index = pc_field_dump_index(pc);
    if (index < 0)
        return;
    bucket = &g_pc_field_dump[index];
    bucket->hits++;
    row.object = gpr32(4);
    row.s0 = gpr32(16);
    row.s1 = gpr32(17);
    row.prev_pc = (uint32_t)pDebugGetState(M64P_DBG_PREVIOUS_PC);
    row.ra = gpr32(31);
    row.source_word = pDebugMemRead32(debug_rdram_addr((row.s0 + 0x60u) & ~3u));
    row.source_byte = debug_mem_u8(row.s0 + 0x22u);
    row.branch_selector = gpr32(2);
    row.branch_state = debug_mem_u16(row.s1 + 0x22u);
    row.cursor = pDebugMemRead32(debug_rdram_addr((row.object + 0x11C8u) & ~3u));
    row.base_198 = debug_mem_u32(row.object + 0x198u);
    row.selected_addr = (row.object + 0x1A0u + ((row.cursor >> 3) & 0xFFCu)) & 0x1FFFFFFFu;
    row.selected_word = pDebugMemRead32(debug_rdram_addr(row.selected_addr & ~3u));
    row.state_18a = debug_mem_u16(row.object + 0x18Au);
    row.state_18c = debug_mem_u16(row.object + 0x18Cu);
    if (g_pc_task_join_enabled && g_n_pc_task_dump_rows > 0) {
        uint32_t width = pDebugMemRead32(VI_WIDTH_ADDR);
        uint32_t origin = pDebugMemRead32(VI_ORIGIN_ADDR);
        int task_i = g_n_pc_task_dump_rows - 1;
        struct pc_task_dump_row *task = NULL;
        while (task_i >= 0) {
            if (g_pc_task_dump_rows[task_i].width == width &&
                g_pc_task_dump_rows[task_i].origin == origin) {
                task = &g_pc_task_dump_rows[task_i];
                break;
            }
            task_i--;
        }
        if (task != NULL) {
            int join_i;
            for (join_i = 0; join_i < g_n_pc_task_join_rows; join_i++) {
                struct pc_task_join_row *joined = &g_pc_task_join_rows[join_i];
                if (joined->width == width && joined->origin == origin &&
                    joined->task_ptr == task->task_ptr &&
                    joined->data_ptr == task->data_ptr &&
                    joined->data_size == task->data_size &&
                    joined->s1 == row.s1 && joined->prev_pc == row.prev_pc &&
                    joined->ra == row.ra) {
                    joined->n++;
                    goto joined_done;
                }
            }
            if (g_n_pc_task_join_rows >= MAX_PC_TASK_DUMP_ROWS) {
                g_pc_task_join_overflow++;
            } else {
                struct pc_task_join_row *joined =
                    &g_pc_task_join_rows[g_n_pc_task_join_rows++];
                joined->width = width;
                joined->origin = origin;
                joined->task_ptr = task->task_ptr;
                joined->data_ptr = task->data_ptr;
                joined->data_size = task->data_size;
                joined->s1 = row.s1;
                joined->prev_pc = row.prev_pc;
                joined->ra = row.ra;
                joined->n = 1;
                printf("[pc-task-join] field_pc=0x%08x width=%u origin=0x%08x "
                       "task_ptr=0x%08x data_ptr=0x%08x data_size=0x%08x "
                       "s1=0x%08x prev_pc=0x%08x ra=0x%08x n=1\n",
                       pc, width, origin, task->task_ptr, task->data_ptr,
                       task->data_size, row.s1, row.prev_pc, row.ra);
                fflush(stdout);
            }
        }
    }
joined_done:
    for (i = 0; i < bucket->n_rows; i++) {
        if (bucket->rows[i].s0 == row.s0 &&
            bucket->rows[i].object == row.object &&
            bucket->rows[i].s1 == row.s1 &&
            bucket->rows[i].prev_pc == row.prev_pc &&
            bucket->rows[i].ra == row.ra &&
            bucket->rows[i].source_word == row.source_word &&
            bucket->rows[i].source_byte == row.source_byte &&
            bucket->rows[i].branch_selector == row.branch_selector &&
            bucket->rows[i].branch_state == row.branch_state) {
            if (bucket->rows[i].cursor == row.cursor &&
                bucket->rows[i].base_198 == row.base_198 &&
                bucket->rows[i].selected_addr == row.selected_addr &&
                bucket->rows[i].selected_word == row.selected_word &&
                bucket->rows[i].state_18a == row.state_18a &&
                bucket->rows[i].state_18c == row.state_18c) {
            bucket->rows[i].n++;
            return;
            }
        }
    }
    if (bucket->n_rows >= MAX_PC_FIELD_DUMP_ROWS) {
        bucket->overflow++;
        return;
    }
    row.n = 1;
    bucket->rows[bucket->n_rows++] = row;
    printf("[pc-field-dump] pc=0x%08x width=%u origin=0x%08x "
           "prev_pc=0x%08x ra=0x%08x s0=0x%08x s1=0x%08x source_word=0x%08x "
           "source_byte=0x%02x branch_selector=0x%08x "
           "branch_state=0x%04x object=0x%08x cursor=0x%08x base_198=0x%08x "
           "selected_addr=0x%08x selected_word=0x%08x state_18a=0x%04x "
           "state_18c=0x%04x n=1\n",
           pc, pDebugMemRead32(VI_WIDTH_ADDR),
           pDebugMemRead32(VI_ORIGIN_ADDR), row.prev_pc, row.ra,
           row.s0, row.s1,
           row.source_word, row.source_byte, row.branch_selector,
           row.branch_state, row.object, row.cursor, row.base_198, row.selected_addr,
           row.selected_word, row.state_18a, row.state_18c);
    fflush(stdout);
}

static void dump_boundary_join(uint32_t pc)
{
    struct boundary_join_row row;
    struct pc_task_dump_row *task = NULL;
    uint32_t width, origin;
    int task_i;

    if (!g_boundary_join_enabled ||
        (pc != 0x8009C950u && pc != 0x8009C954u &&
         pc != 0x8009D78Cu && pc != 0x8009D790u && pc != 0x8009DC38u) ||
        !pc_phase_log_match())
        return;
    width = pDebugMemRead32(VI_WIDTH_ADDR);
    origin = pDebugMemRead32(VI_ORIGIN_ADDR);
    for (task_i = g_n_pc_task_dump_rows - 1; task_i >= 0; task_i--) {
        if (g_pc_task_dump_rows[task_i].width == width &&
            g_pc_task_dump_rows[task_i].origin == origin) {
            task = &g_pc_task_dump_rows[task_i];
            break;
        }
    }
    g_boundary_join_hits++;
    if (!task) {
        g_boundary_join_no_task++;
        return;
    }
    if (g_n_boundary_join_rows >= MAX_BOUNDARY_JOIN_ROWS) {
        g_boundary_join_overflow++;
        return;
    }
    row.pc = pc;
    row.width = width;
    row.origin = origin;
    row.task_n = task->task_n;
    row.task_ptr = task->task_ptr;
    row.data_ptr = task->data_ptr;
    row.data_size = task->data_size;
    row.event_ordinal = g_event_ordinal;
    row.object = gpr32(4);
    row.cursor = pDebugMemRead32(debug_rdram_addr((row.object + 0x11C8u) & ~3u));
    row.selected_addr = pc == 0x8009C950u
        ? (gpr32(2) & 0x1FFFFFFFu) : 0;
    row.selected_word = row.selected_addr
        ? debug_mem_u32(row.selected_addr) : 0;
    row.branch_state = debug_mem_u16(gpr32(17) + 0x22u);
    row.instruction = pDebugMemRead32(pc);
    row.source_reg = (row.instruction >> 16) & 31u;
    row.source_value = gpr32((int)row.source_reg);
    row.n = 1;
    g_boundary_join_rows[g_n_boundary_join_rows++] = row;
    printf("[boundary-join] pc=0x%08x width=%u origin=0x%08x task_n=%ld "
           "task_ptr=0x%08x data_ptr=0x%08x data_size=0x%08x "
           "event=%llu object=0x%08x cursor=0x%08x selected_addr=0x%08x "
           "selected_word=0x%08x branch_state=0x%04x instruction=0x%08x "
           "source_reg=%u source_value=0x%08x\n",
           pc, width, origin, row.task_n, row.task_ptr, row.data_ptr,
           row.data_size, (unsigned long long)row.event_ordinal, row.object,
           row.cursor, row.selected_addr, row.selected_word, row.branch_state,
           row.instruction, row.source_reg, row.source_value);
    fflush(stdout);
}

static void dump_c904_witness(uint32_t pc)
{
    struct c904_witness_row row;
    uint32_t object, selected_addr, selected_word;
    int i;

    if (!g_c904_witness_enabled || !pc_phase_log_match())
        return;
    if ((pc == 0x8009C0E8u || pc == 0x8009C904u) &&
        g_n_c904_input_spans < MAX_C904_INPUT_SPANS) {
        struct c904_input_span *span =
            &g_c904_input_spans[g_n_c904_input_spans++];
        span->input = gpr32(5) & 0x1FFFFFFFu;
        span->width = pDebugMemRead32(VI_WIDTH_ADDR);
        span->origin = pDebugMemRead32(VI_ORIGIN_ADDR);
        span->n = 1;
        printf("[c904-input-span] pc=0x%08x input=0x%08x w0=0x%08x w1=0x%08x width=%u origin=0x%08x n=1\n",
               pc, span->input, debug_mem_u32(span->input),
               debug_mem_u32(span->input + 4u), span->width, span->origin);
        fflush(stdout);
    }
    g_c904_witness_hits++;
    row.pc = pc;
    row.width = pDebugMemRead32(VI_WIDTH_ADDR);
    row.origin = pDebugMemRead32(VI_ORIGIN_ADDR);
    row.prev_pc = (uint32_t)pDebugGetState(M64P_DBG_PREVIOUS_PC);
    row.object = gpr32(4);
    row.input = gpr32(5);
    row.input_w0 = debug_mem_u32(row.input);
    row.input_w1 = debug_mem_u32(row.input + 4u);
    for (int input_i = 0; input_i < 8; input_i++)
        row.input_words[input_i] =
            debug_mem_u32(row.input + (uint32_t)input_i * 4u);
    row.v0 = gpr32(2);
    row.a2 = gpr32(6);
    row.a3 = gpr32(7);
    row.s1 = gpr32(17);
    object = gpr32(30);
    selected_addr = row.pc == 0x8009C950u ? (row.v0 & 0x1FFFFFFFu) : 0;
    selected_word = selected_addr ? debug_mem_u32(selected_addr) : 0;
    row.selected_addr = selected_addr;
    row.selected_word = selected_word;
    row.family = selected_word == 0x10u || selected_word == 0x3108u ||
                 (selected_word & 0xFFFFu) == 0x10u ||
                 (selected_word & 0xFFFFu) == 0x3108u;
    if (pc == 0x8009C904u)
        row.object = gpr32(4);
    else
        row.object = object;

    if (g_c904_task_join_enabled) {
        uint32_t width = pDebugMemRead32(VI_WIDTH_ADDR);
        uint32_t origin = pDebugMemRead32(VI_ORIGIN_ADDR);
        int task_i = g_n_pc_task_dump_rows - 1;
        struct pc_task_dump_row *task = NULL;
        while (task_i >= 0) {
            if (g_pc_task_dump_rows[task_i].width == width &&
                g_pc_task_dump_rows[task_i].origin == origin) {
                task = &g_pc_task_dump_rows[task_i];
                break;
            }
            task_i--;
        }
        if (task == NULL) {
            g_c904_task_join_unmatched++;
        } else {
            int join_i;
            g_c904_task_join_matched++;
            uint32_t payload[8];
            uint32_t payload_phys = task->data_ptr & 0x1FFFFFFFu;
            for (int payload_i = 0; payload_i < 8; payload_i++) {
                uint32_t off = (uint32_t)payload_i * 4u;
                payload[payload_i] = payload_phys <= RDRAM_SIZE - 4u - off
                    ? pDebugMemRead32(debug_rdram_addr(payload_phys + off)) : 0;
            }
            for (join_i = 0; join_i < g_n_c904_task_join_rows; join_i++) {
                struct c904_task_join_row *joined =
                    &g_c904_task_join_rows[join_i];
                if (joined->pc == pc && joined->width == width &&
                    joined->origin == origin &&
                    joined->task_ptr == task->task_ptr &&
                    joined->data_ptr == task->data_ptr &&
                    joined->data_size == task->data_size &&
                    joined->input == row.input &&
                    joined->input_w0 == row.input_w0 &&
                    joined->input_w1 == row.input_w1 &&
                    memcmp(joined->input_words, row.input_words,
                           sizeof(row.input_words)) == 0 &&
                    joined->selected_addr == row.selected_addr &&
                    joined->selected_word == row.selected_word &&
                    memcmp(joined->payload, payload, sizeof(payload)) == 0) {
                    joined->n++;
                    goto c904_task_join_done;
                }
            }
            if (g_n_c904_task_join_rows >= MAX_C904_TASK_JOIN_ROWS) {
                g_c904_task_join_overflow++;
            } else {
                struct c904_task_join_row *joined =
                    &g_c904_task_join_rows[g_n_c904_task_join_rows++];
                joined->pc = pc;
                joined->width = width;
                joined->origin = origin;
                joined->task_ptr = task->task_ptr;
                joined->data_ptr = task->data_ptr;
                joined->data_size = task->data_size;
                joined->input = row.input;
                joined->input_w0 = row.input_w0;
                joined->input_w1 = row.input_w1;
                memcpy(joined->input_words, row.input_words,
                       sizeof(row.input_words));
                joined->selected_addr = row.selected_addr;
                joined->selected_word = row.selected_word;
                memcpy(joined->payload, payload, sizeof(payload));
                joined->n = 1;
                printf("[c904-task-join] pc=0x%08x width=%u origin=0x%08x "
                       "task_ptr=0x%08x data_ptr=0x%08x data_size=0x%08x "
                       "input=0x%08x input_w0=0x%08x input_w1=0x%08x input_words=",
                       pc, width, origin, task->task_ptr, task->data_ptr,
                       task->data_size, row.input, row.input_w0, row.input_w1);
                for (int input_i = 0; input_i < 8; input_i++)
                    printf("%08x%s", row.input_words[input_i],
                           input_i == 7 ? " " : ",");
                printf("selected_addr=0x%08x selected_word=0x%08x payload=",
                       row.selected_addr, row.selected_word);
                for (int payload_i = 0; payload_i < 8; payload_i++)
                    printf("%08x%s", payload[payload_i], payload_i == 7 ? "" : ",");
                printf(" n=1\n");
                fflush(stdout);
            }
        }
    }
c904_task_join_done:
    for (i = 0; i < MAX_C904_WITNESS_ROWS; i++) {
        if (g_c904_witness_rows[i].pc == row.pc &&
            g_c904_witness_rows[i].width == row.width &&
            g_c904_witness_rows[i].origin == row.origin &&
            g_c904_witness_rows[i].prev_pc == row.prev_pc &&
            g_c904_witness_rows[i].object == row.object &&
            g_c904_witness_rows[i].input == row.input &&
            g_c904_witness_rows[i].input_w0 == row.input_w0 &&
            g_c904_witness_rows[i].input_w1 == row.input_w1 &&
            memcmp(g_c904_witness_rows[i].input_words, row.input_words,
                   sizeof(row.input_words)) == 0 &&
            g_c904_witness_rows[i].v0 == row.v0 &&
            g_c904_witness_rows[i].a2 == row.a2 &&
            g_c904_witness_rows[i].a3 == row.a3 &&
            g_c904_witness_rows[i].s1 == row.s1 &&
            g_c904_witness_rows[i].selected_addr == row.selected_addr &&
            g_c904_witness_rows[i].selected_word == row.selected_word) {
            g_c904_witness_rows[i].n++;
            return;
        }
        if (g_c904_witness_rows[i].n == 0) {
            row.n = 1;
            g_c904_witness_rows[i] = row;
            printf("[c904-witness] pc=0x%08x width=%u origin=0x%08x "
                   "prev_pc=0x%08x object=0x%08x input=0x%08x "
                   "input_w0=0x%08x input_w1=0x%08x "
                   "v0=0x%08x a2=0x%08x a3=0x%08x s1=0x%08x "
                   "selected_addr=0x%08x selected_word=0x%08x family=%d "
                   "input_words=",
                   row.pc, row.width, row.origin, row.prev_pc, row.object,
                   row.input,
                   row.input_w0, row.input_w1, row.v0, row.a2, row.a3,
                   row.s1, row.selected_addr, row.selected_word, row.family);
            for (int input_i = 0; input_i < 8; input_i++)
                printf("%08x%s", row.input_words[input_i],
                       input_i == 7 ? "\n" : ",");
            fflush(stdout);
            return;
        }
    }
    g_c904_witness_overflow++;
}

static int store_field_dump_pc_index(uint32_t pc)
{
    int i;
    for (i = 0; i < g_n_store_field_dump_pc; i++)
        if (g_store_field_dump_pc[i].pc == pc)
            return i;
    return -1;
}

static void dump_store_field(int watch, uint32_t pc, uint32_t accessed)
{
    struct store_field_dump_row row;
    int pc_index = store_field_dump_pc_index(pc);
    int i;

    if ((g_store_field_dump_all_mask & (1u << watch)) == 0 &&
        (pc_index < 0 || !(g_store_field_dump_pc[pc_index].watch_mask &
                           (UINT64_C(1) << watch))))
        return;
    g_store_field_dump_candidate_callbacks++;
    if (!g_store_field_dump_any_phase && !store_field_phase_log_match())
        return;
    g_store_field_dump_hits++;
    row.watch = watch;
    row.pc = pc;
    row.store_addr = accessed;
    row.instruction = pDebugMemRead32(pc);
    row.source_reg = (row.instruction >> 16) & 31u;
    row.effective_addr = gpr32((row.instruction >> 21) & 31u) +
        (uint32_t)(int32_t)(int16_t)row.instruction;
    row.source_value = gpr32(row.source_reg);
    row.scalar_mask = ((row.effective_addr & 0x1FFFFFFCu) ==
                       (accessed & 0x1FFFFFFCu)) ?
        scalar_store_mask(row.instruction, row.effective_addr) : 0;
    row.pre_store_word = pDebugMemRead32(debug_rdram_addr(accessed & ~3u));
    row.ra = gpr32(31);
    row.a0 = gpr32(4);
    row.a1 = gpr32(5);
    row.a2 = gpr32(6);
    row.t0 = gpr32(8);
    row.t1 = gpr32(9);
    row.s0 = gpr32(16);
    row.s1 = gpr32(17);
    row.source_word = pDebugMemRead32(debug_rdram_addr((row.s0 + 0x60u) & ~3u));
    row.source_byte = debug_mem_u8(row.s0 + 0x22u);
    row.branch_selector = gpr32(2);
    row.branch_state = debug_mem_u16(row.s1 + 0x22u);
    for (i = 0; i < g_n_store_field_dump_rows; i++) {
        struct store_field_dump_row *old = &g_store_field_dump_rows[i];
        if (old->watch == row.watch && old->pc == row.pc &&
            old->store_addr == row.store_addr &&
            old->instruction == row.instruction &&
            old->effective_addr == row.effective_addr &&
            old->source_reg == row.source_reg &&
            old->source_value == row.source_value &&
            old->scalar_mask == row.scalar_mask &&
            old->pre_store_word == row.pre_store_word &&
            old->ra == row.ra && old->a0 == row.a0 && old->a1 == row.a1 &&
            old->a2 == row.a2 && old->t0 == row.t0 && old->t1 == row.t1 &&
            old->s0 == row.s0 && old->s1 == row.s1 &&
            old->source_word == row.source_word &&
            old->source_byte == row.source_byte &&
            old->branch_selector == row.branch_selector &&
            old->branch_state == row.branch_state) {
            old->n++;
            return;
        }
    }
    if (g_n_store_field_dump_rows >= MAX_STORE_FIELD_DUMP_ROWS) {
        g_store_field_dump_overflow++;
        return;
    }
    row.n = 1;
    g_store_field_dump_rows[g_n_store_field_dump_rows++] = row;
    printf("[store-field-dump] watch=%d pc=0x%08x width=%u origin=0x%08x "
           "store_addr=0x%08x instruction=0x%08x effective_addr=0x%08x "
           "source_reg=%u source_value=0x%08x scalar_mask=0x%08x "
           "pre_store_word=0x%08x ra=0x%08x "
           "a0=0x%08x a1=0x%08x a2=0x%08x t0=0x%08x t1=0x%08x "
           "s0=0x%08x s1=0x%08x source_word=0x%08x source_byte=0x%02x "
           "branch_selector=0x%08x branch_state=0x%04x n=1\n",
           row.watch, row.pc, pDebugMemRead32(VI_WIDTH_ADDR),
           pDebugMemRead32(VI_ORIGIN_ADDR), row.store_addr,
           row.instruction, row.effective_addr, row.source_reg,
           row.source_value, row.scalar_mask, row.pre_store_word, row.ra,
           row.a0, row.a1, row.a2, row.t0, row.t1,
           row.s0, row.s1, row.source_word, row.source_byte,
           row.branch_selector, row.branch_state);
    fflush(stdout);
}

static void add_store_field_dump(const char *arg)
{
    char *copy = strdup(arg);
    char *pcs, *tok, *save = NULL;
    int watch;
    if (!copy)
        exit(1);
    pcs = strchr(copy, ':');
    if (!pcs) {
        fprintf(stderr, "[oracle] bad --store-field-dump '%s'\n", arg);
        free(copy);
        exit(2);
    }
    *pcs++ = '\0';
    watch = atoi(copy);
    if (watch < 0 || watch >= MAX_WATCHES || !*pcs) {
        fprintf(stderr, "[oracle] bad --store-field-dump '%s'\n", arg);
        free(copy);
        exit(2);
    }
    for (tok = strtok_r(pcs, ",", &save); tok;
         tok = strtok_r(NULL, ",", &save)) {
        uint32_t pc = (uint32_t)strtoul(tok, NULL, 0);
        int i = store_field_dump_pc_index(pc);
        if (i < 0) {
            if (g_n_store_field_dump_pc >= MAX_STORE_FIELD_DUMP_PCS) {
                fprintf(stderr, "[oracle] too many --store-field-dump PCs\n");
                free(copy);
                exit(2);
            }
            i = g_n_store_field_dump_pc++;
            g_store_field_dump_pc[i].pc = pc;
            g_store_field_dump_pc[i].watch_mask = 0;
        }
        g_store_field_dump_pc[i].watch_mask |= UINT64_C(1) << watch;
    }
    free(copy);
}

static void add_store_field_dump_all(const char *arg)
{
    unsigned long watch = strtoul(arg, NULL, 0);
    if (watch >= 32 || watch >= MAX_WATCHES) {
        fprintf(stderr, "[oracle] bad --store-field-dump-all '%s'\n", arg);
        exit(2);
    }
    g_store_field_dump_all_mask |= 1u << watch;
}

static void add_pc_field_dump_pcs(const char *arg)
{
    char *copy = strdup(arg);
    char *tok, *save = NULL;
    if (!copy)
        exit(1);
    for (tok = strtok_r(copy, ",", &save); tok;
         tok = strtok_r(NULL, ",", &save)) {
        unsigned int pc;
        if (g_n_pc_field_dump >= MAX_PC_FIELD_DUMP_PCS ||
            sscanf(tok, "%x", &pc) != 1) {
            fprintf(stderr, "[oracle] bad --pc-field-dump '%s'\n", tok);
            free(copy);
            exit(2);
        }
        g_pc_field_dump[g_n_pc_field_dump++].pc = pc;
    }
    free(copy);
}

static void dump_audio_objects(uint32_t task, uint32_t data, uint32_t count) {
    uint32_t width = pDebugMemRead32(VI_WIDTH_ADDR);
    uint32_t origin = pDebugMemRead32(VI_ORIGIN_ADDR);
    static uint32_t rows[2];
    uint32_t row = rows[width == 512]++;
    if (row >= 8 && (row % 128 != 0 || row >= 4096)) return;
    data &= 0x1FFFFFFF;
    printf("[audio-objects-task] width=%u origin=%08X row=%u ucode=%08X data=%08X count=%u\n",
           width, origin, row, pDebugMemRead32(debug_rdram_addr(task + 0x10)), data, count);
    if (count > 8 || data > RDRAM_SIZE || count * 0xA10 > RDRAM_SIZE - data) return;
    for (uint32_t frame = 0; frame < count; frame++) {
        uint32_t base = data + frame * 0xA10;
        uint32_t state = pDebugMemRead32(debug_rdram_addr(base + 8)) & 0x1FFFFFFF;
        uint32_t nz = 0, active = 0, output = 0;
        int valid = state <= RDRAM_SIZE - 0x298;
        if (valid) for (uint32_t i = 0; i < 0x298; i++) nz += debug_mem_u8(state + i) != 0;
        for (uint32_t voice = 0; voice < 32; voice++) {
            uint32_t v = base + 0x10 + voice * 0x50;
            output = pDebugMemRead32(debug_rdram_addr(v + 0x44));
            if (debug_mem_u16(v + 0x2C) == 0) break;
            active++;
            if (output) break;
        }
        printf("[audio-objects-frame] width=%u row=%u frame=%u base=%08X h0=%08X h4=%08X state=%08X hc=%08X valid=%u state_nz=%u active=%u output=%08X first=",
               width, row, frame, base, pDebugMemRead32(debug_rdram_addr(base)),
               pDebugMemRead32(debug_rdram_addr(base + 4)), state,
               pDebugMemRead32(debug_rdram_addr(base + 12)), valid, nz, active, output);
        for (uint32_t i = 0; i < 0x50; i += 4) printf("%08X,", pDebugMemRead32(debug_rdram_addr(base + 0x10 + i)));
        printf("\n");
        {
            /* s4219: census of output-ring buffers (record +0x44 ptr, 0x300 B each) */
            uint32_t nbuf = 0, nz_buf = 0, nz_bytes = 0, tot = 0, blk_nz = 0;
            for (uint32_t i = 0; i < 0xA10 - 0x10 && base + 0x10 + i < RDRAM_SIZE; i++)
                blk_nz += debug_mem_u8(base + 0x10 + i) != 0; /* positive control */
            for (uint32_t voice = 0; voice < 32; voice++) {
                uint32_t v = base + 0x10 + voice * 0x50;
                uint32_t o = pDebugMemRead32(debug_rdram_addr(v + 0x44)) & 0x1FFFFFFF;
                uint32_t k, c = 0;
                if (!o || o > RDRAM_SIZE - 0x300) continue;
                nbuf++;
                for (k = 0; k < 0x300; k++) c += debug_mem_u8(o + k) != 0;
                nz_bytes += c; tot += 0x300; nz_buf += c != 0;
            }
            printf("[out-census] width=%u row=%u frame=%u bufs=%u nz_bufs=%u nz_bytes=%u of=%u ctrl_blk_nz=%u\n",
                   width, row, frame, nbuf, nz_buf, nz_bytes, tot, blk_nz);
        }
    }
}

static void dump_pc_task(uint32_t pc)
{
    struct pc_task_dump_row *row;
    uint32_t task_ptr;
    uint32_t task_phys;
    uint32_t data_ptr;
    uint32_t width;
    uint32_t origin;

    if (!g_pc_task_dump_enabled || pc != g_pc_task_dump_pc ||
        !pc_task_dump_phase_match())
        return;
    g_pc_task_dump_phase_hits++;
    task_ptr = gpr32(4);
    task_phys = task_ptr & 0x1FFFFFFFu;
    if (task_phys > RDRAM_SIZE - 0x40u) {
        g_pc_task_dump_invalid++;
        return;
    }
    {
        uint32_t type = pDebugMemRead32(debug_rdram_addr(task_phys));
        if (g_pc_task_dump_type != 0 && type != g_pc_task_dump_type) {
            g_pc_task_dump_non_type2++;
            return;
        }
        g_pc_task_dump_type2_rows++;
        if (g_n_pc_task_dump_rows >= MAX_PC_TASK_DUMP_ROWS) {
            g_pc_task_dump_overflow++;
            return;
        }
        row = &g_pc_task_dump_rows[g_n_pc_task_dump_rows++];
        row->task_n = g_pc_task_dump_type2_rows;
        row->event_ordinal = g_event_ordinal;
        row->task_ptr = task_ptr;
        row->task_phys = task_phys;
        row->type = type;
    }
    row->output_buff = pDebugMemRead32(debug_rdram_addr(task_phys + 0x28u));
    row->output_buff_size = pDebugMemRead32(debug_rdram_addr(task_phys + 0x2Cu));
    row->data_ptr = pDebugMemRead32(debug_rdram_addr(task_phys + 0x30u));
    row->data_size = pDebugMemRead32(debug_rdram_addr(task_phys + 0x34u));
    row->yield_data_ptr = pDebugMemRead32(debug_rdram_addr(task_phys + 0x38u));
    row->yield_data_size = pDebugMemRead32(debug_rdram_addr(task_phys + 0x3Cu));
    for (int published_i = 0; published_i < 4; published_i++) {
        uint32_t published_addr = g_published_word_addrs[published_i];
        uint32_t base = row->data_ptr & 0x1FFFFFFFu;
        uint64_t len = (uint64_t)row->data_size * 0xA10u;
        row->published_valid[published_i] =
            len && published_addr >= base &&
            (uint64_t)published_addr + 4u <= (uint64_t)base + len &&
            published_addr <= RDRAM_SIZE - 4u;
        row->published_words[published_i] = row->published_valid[published_i]
            ? debug_mem_u32(published_addr) : 0;
    }
    if (row->type == 2 && !g_pc_task_join_enabled)
        dump_audio_objects(task_phys, row->data_ptr, row->data_size);
    if (row->type == 2) {
        /* s4217: content census of the whole data_ptr block (count*0xA10 B) */
        static long blk_n;
        uint32_t base = row->data_ptr & 0x1FFFFFFFu;
        uint32_t len = row->data_size * 0xA10u;
        long n = blk_n++;
        if (len && len <= 0x4000u && base < RDRAM_SIZE &&
            len <= RDRAM_SIZE - base && (n < 24 || n % 64 == 0)) {
            uint32_t zero = 0, ascii = 0, p801 = 0, i;
            for (i = 0; i < len; i++) {
                uint32_t b = debug_mem_u8(base + i);
                zero += b == 0;
                ascii += b >= 0x20 && b < 0x7F;
            }
            for (i = 0; i + 4 <= len; i += 4)
                p801 += (pDebugMemRead32(debug_rdram_addr(base + i)) >> 20) == 0x801;
            printf("[blk-census] n=%ld width=%u origin=0x%08x base=0x%06x len=0x%x "
                   "zero=%u ascii=%u p801=%u w30=",
                   n, pDebugMemRead32(VI_WIDTH_ADDR), pDebugMemRead32(VI_ORIGIN_ADDR),
                   base, len, zero, ascii, p801);
            for (i = 0x30; i < 0x70 && i + 4 <= len; i += 4)
                printf("%08X,", pDebugMemRead32(debug_rdram_addr(base + i)));
            printf("\n");
        }
    }
    data_ptr = row->data_ptr;
    row->data_ptr_plus_100 = data_ptr + 0x100u;
    row->field_phys = row->data_ptr_plus_100 & 0x007FFFFFu;
    width = pDebugMemRead32(VI_WIDTH_ADDR);
    origin = pDebugMemRead32(VI_ORIGIN_ADDR);
    row->width = width;
    row->origin = origin;
    printf("[pc-task-dump] pc=0x%08x width=%u origin=0x%08x "
           "task_n=%ld task_ptr=0x%08x task_phys=0x%08x type=0x%08x "
           "data_ptr=0x%08x data_size=0x%08x "
           "output_buff=0x%08x output_buff_size=0x%08x "
           "yield_data_ptr=0x%08x yield_data_size=0x%08x "
           "data_ptr_plus_100=0x%08x field_phys=0x%06x\n",
           pc, width, origin, row->task_n, row->task_ptr, row->task_phys,
           row->type, row->data_ptr, row->data_size, row->output_buff,
           row->output_buff_size, row->yield_data_ptr,
           row->yield_data_size, row->data_ptr_plus_100, row->field_phys);
    fflush(stdout);
}

static void dump_pc_range_task(uint32_t pc)
{
    struct pc_range_task_row *row;
    uint32_t task_ptr;
    uint32_t task_phys;
    uint32_t width;
    uint32_t origin;

    if (!g_pc_range_task_dump_enabled || !pc_phase_log_match())
        return;
    g_pc_range_task_hits++;
    width = pDebugMemRead32(VI_WIDTH_ADDR);
    origin = pDebugMemRead32(VI_ORIGIN_ADDR);
    task_ptr = gpr32(4);
    task_phys = task_ptr & 0x1FFFFFFFu;
    if (task_phys > RDRAM_SIZE - 0x40u) {
        g_pc_range_task_invalid++;
        return;
    }
    {
        int phase_rows = 0;
        int i;
        for (i = 0; i < g_n_pc_range_task_rows; i++)
            if (g_pc_range_task_rows[i].width == width &&
                g_pc_range_task_rows[i].origin == origin)
                phase_rows++;
        if (phase_rows >= MAX_PC_RANGE_TASK_ROWS_PER_PHASE ||
            g_n_pc_range_task_rows >= MAX_PC_RANGE_TASK_ROWS) {
            g_pc_range_task_overflow++;
            return;
        }
    }
    row = &g_pc_range_task_rows[g_n_pc_range_task_rows++];
    row->pc = pc;
    row->width = width;
    row->origin = origin;
    row->a0 = task_ptr;
    row->a0_word = pDebugMemRead32(debug_rdram_addr(task_phys));
    row->output_buff = pDebugMemRead32(debug_rdram_addr(task_phys + 0x28u));
    row->output_buff_size = pDebugMemRead32(debug_rdram_addr(task_phys + 0x2Cu));
    row->data_ptr = pDebugMemRead32(debug_rdram_addr(task_phys + 0x30u));
    row->data_size = pDebugMemRead32(debug_rdram_addr(task_phys + 0x34u));
    row->yield_data_ptr = pDebugMemRead32(debug_rdram_addr(task_phys + 0x38u));
    row->yield_data_size = pDebugMemRead32(debug_rdram_addr(task_phys + 0x3Cu));
    row->n = g_pc_range_task_hits;
}

static void add_pc_phase_log_width(char *spec)
{
    char *colon = strchr(spec, ':');
    if (!colon || colon == spec || !colon[1]) {
        fprintf(stderr, "[oracle] bad --pc-phase-log-width '%s' (want ORIGIN:WIDTH)\n",
                spec);
        exit(2);
    }
    *colon = 0;
    if (g_n_pc_phase_log_origin >= MAX_PC_PHASE_LOG_ORIGINS) {
        fprintf(stderr, "[oracle] too many phase-log buckets\n");
        exit(2);
    }
    g_pc_phase_log[g_n_pc_phase_log_origin].origin =
        to_phys((uint32_t)strtoul(spec, NULL, 0));
    g_pc_phase_log[g_n_pc_phase_log_origin].width =
        (uint32_t)strtoul(colon + 1, NULL, 0);
    g_n_pc_phase_log_origin++;
}

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

struct vi_swap_phase_row {
    uint32_t origin;
    uint32_t prev_pc;
    uint32_t a0_phys;
    long n;
};
static struct vi_swap_phase_row g_vi_swap_phase[MAX_VI_SWAP_PHASE_ROWS];
static int g_n_vi_swap_phase;
static long g_vi_swap_phase_overflow;

static void count_vi_swap_phase(uint32_t origin, uint32_t prev_pc,
                                uint32_t a0_phys)
{
    int i;
    for (i = 0; i < g_n_vi_swap_phase; i++) {
        if (g_vi_swap_phase[i].origin == origin &&
            g_vi_swap_phase[i].prev_pc == prev_pc &&
            g_vi_swap_phase[i].a0_phys == a0_phys) {
            g_vi_swap_phase[i].n++;
            return;
        }
    }
    if (g_n_vi_swap_phase < MAX_VI_SWAP_PHASE_ROWS) {
        g_vi_swap_phase[g_n_vi_swap_phase].origin = origin;
        g_vi_swap_phase[g_n_vi_swap_phase].prev_pc = prev_pc;
        g_vi_swap_phase[g_n_vi_swap_phase].a0_phys = a0_phys;
        g_vi_swap_phase[g_n_vi_swap_phase].n = 1;
        g_n_vi_swap_phase++;
    } else {
        g_vi_swap_phase_overflow++;
    }
}

static void dump_mode_descriptor(uint32_t pc)
{
    uint32_t mode_ptr = gpr32(4);
    uint32_t mode_phys = mode_ptr & 0x1FFFFFFFu;
    uint32_t mode_width = pDebugMemRead32(debug_rdram_addr(mode_phys + 0x08));

    if (mode_width != 640)
        return;
    g_mode_dump_rows++;
    if (g_mode_dump_rows > MAX_MODE_DUMP_ROWS) {
        g_mode_dump_overflow++;
        return;
    }
    g_last_mode_descriptor.valid = 1;
    g_last_mode_descriptor.mode_ptr = mode_ptr;
    g_last_mode_descriptor.fld0_origin =
        pDebugMemRead32(debug_rdram_addr(mode_phys + 0x28));
    g_last_mode_descriptor.fld0_y_scale =
        pDebugMemRead32(debug_rdram_addr(mode_phys + 0x2C));
    g_last_mode_descriptor.fld1_origin =
        pDebugMemRead32(debug_rdram_addr(mode_phys + 0x3C));
    g_last_mode_descriptor.fld1_y_scale =
        pDebugMemRead32(debug_rdram_addr(mode_phys + 0x40));
    printf("[mode-dump] pc=0x%08x mode_ptr=0x%08x width=%u "
           "fld0.origin=0x%08x fld0.yScale=0x%08x "
           "fld1.origin=0x%08x fld1.yScale=0x%08x\n",
           pc, mode_ptr, mode_width,
           g_last_mode_descriptor.fld0_origin,
           g_last_mode_descriptor.fld0_y_scale,
           g_last_mode_descriptor.fld1_origin,
           g_last_mode_descriptor.fld1_y_scale);
    fflush(stdout);
}

static void latch_post_swap_table(uint32_t pc)
{
    if (!g_post_swap_table_enabled || pc != g_post_swap_table_pc)
        return;
    if (g_post_swap_pending.valid)
        g_post_swap_dropped++;
    g_post_swap_pending.valid = 1;
    g_post_swap_pending.pre_width = pDebugMemRead32(VI_WIDTH_ADDR);
    g_post_swap_pending.pre_origin = pDebugMemRead32(VI_ORIGIN_ADDR);
    g_post_swap_pending.prev_pc =
        (uint32_t)pDebugGetState(M64P_DBG_PREVIOUS_PC);
    g_post_swap_pending.a0_phys = gpr32(4) & 0x1FFFFFFFu;
    g_post_swap_pending.mode = g_last_mode_descriptor;
    g_post_swap_latched++;
}

static int is_post_swap_target_origin(uint32_t origin)
{
    return origin == 0x00696100u || origin == 0x00696600u;
}

static int is_vi_context_target_origin(uint32_t origin)
{
    return origin == 0x0066A500u || origin == 0x005D4500u ||
           origin == 0x0066AA00u || origin == 0x00696600u ||
           origin == 0x00696100u || origin == 0x0062C200u ||
           origin == 0x0062BD00u;
}

static int is_valid_rdram_phys(uint32_t physical)
{
    return physical < RDRAM_SIZE;
}

static struct vi_context_snapshot read_vi_context_snapshot(void)
{
    struct vi_context_snapshot snapshot;
    uint32_t context_phys;
    uint32_t framep;
    uint32_t mode_phys;

    memset(&snapshot, 0, sizeof(snapshot));
    snapshot.context_ptr = pDebugMemRead32(VI_NEXT_PTR_ADDR);
    snapshot.current_field = pDebugMemRead32(VI_CURRENT_ADDR) & 1u;
    context_phys = snapshot.context_ptr & 0x1FFFFFFFu;
    if (!is_valid_rdram_phys(context_phys))
        return snapshot;

    snapshot.context_valid = 1;
    snapshot.state = pDebugMemRead32(debug_rdram_addr(context_phys)) & 0xFFFFu;
    framep = pDebugMemRead32(debug_rdram_addr(context_phys + 0x04u));
    snapshot.framep_phys = framep & 0x1FFFFFFFu;
    snapshot.mode_ptr = pDebugMemRead32(debug_rdram_addr(context_phys + 0x08u));
    mode_phys = snapshot.mode_ptr & 0x1FFFFFFFu;
    if (!is_valid_rdram_phys(mode_phys))
        return snapshot;

    snapshot.mode_valid = 1;
    snapshot.fld0_origin =
        pDebugMemRead32(debug_rdram_addr(mode_phys + 0x28u));
    snapshot.fld0_y_scale =
        pDebugMemRead32(debug_rdram_addr(mode_phys + 0x2Cu));
    snapshot.fld1_origin =
        pDebugMemRead32(debug_rdram_addr(mode_phys + 0x3Cu));
    snapshot.fld1_y_scale =
        pDebugMemRead32(debug_rdram_addr(mode_phys + 0x40u));
    snapshot.candidate0 = snapshot.framep_phys + snapshot.fld0_origin;
    snapshot.candidate1 = snapshot.framep_phys + snapshot.fld1_origin;
    return snapshot;
}

static void latch_vi_context_table(uint32_t pc)
{
    if (!g_vi_context_table_enabled || pc != g_vi_context_table_pc ||
        (!g_vi_context_any_vi && pDebugMemRead32(VI_WIDTH_ADDR) != 640))
        return;
    if (g_vi_context_pending.valid)
        g_vi_context_dropped++;
    g_vi_context_pending.valid = 1;
    g_vi_context_pending.snapshot = read_vi_context_snapshot();
    g_vi_context_latched++;
}

static void join_vi_context_table(uint32_t width, uint32_t origin)
{
    struct vi_context_snapshot snapshot;

    if (!g_vi_context_table_enabled || !g_vi_context_pending.valid)
        return;
    snapshot = g_vi_context_pending.snapshot;
    g_vi_context_pending.valid = 0;
    if ((!g_vi_context_any_vi && width != 640) ||
        (!g_vi_context_any_vi && !is_vi_context_target_origin(origin))) {
        g_vi_context_dropped++;
        return;
    }
    if (g_vi_context_joined >= MAX_VI_CONTEXT_ROWS) {
        g_vi_context_overflow++;
        return;
    }
    printf("[vi-context-row] context_ptr=0x%08x context_valid=%d "
           "state=0x%04x framep_phys=0x%08x mode_ptr=0x%08x "
           "mode_valid=%d current_field=%u "
           "fld0.origin=0x%08x fld0.yScale=0x%08x "
           "fld1.origin=0x%08x fld1.yScale=0x%08x "
           "candidate0=0x%08x candidate1=0x%08x next_origin=0x%08x\n",
           snapshot.context_ptr, snapshot.context_valid, snapshot.state,
           snapshot.framep_phys, snapshot.mode_ptr, snapshot.mode_valid,
           snapshot.current_field, snapshot.fld0_origin,
           snapshot.fld0_y_scale, snapshot.fld1_origin,
           snapshot.fld1_y_scale, snapshot.candidate0,
           snapshot.candidate1, origin);
    fflush(stdout);
    g_vi_context_joined++;
}

static void join_post_swap_table(uint32_t width, uint32_t origin)
{
    struct post_swap_pending pending;

    if (!g_post_swap_table_enabled || !g_post_swap_pending.valid)
        return;
    pending = g_post_swap_pending;
    g_post_swap_pending.valid = 0;
    if ((!g_post_swap_any_vi && width != 640) ||
        (!g_post_swap_any_vi && !is_post_swap_target_origin(origin))) {
        g_post_swap_dropped++;
        return;
    }
    if (g_post_swap_joined >= MAX_MODE_DUMP_ROWS) {
        g_post_swap_overflow++;
        return;
    }
    printf("[post-swap-row] pre_width=%u pre_origin=0x%08x swap_prev_pc=0x%08x "
           "a0_phys=0x%08x next_origin=0x%08x mode_valid=%d "
           "mode_ptr=0x%08x fld0.origin=0x%08x fld0.yScale=0x%08x "
           "fld1.origin=0x%08x fld1.yScale=0x%08x\n",
           pending.pre_width, pending.pre_origin, pending.prev_pc,
           pending.a0_phys, origin,
           pending.mode.valid, pending.mode.mode_ptr,
           pending.mode.fld0_origin, pending.mode.fld0_y_scale,
           pending.mode.fld1_origin, pending.mode.fld1_y_scale);
    fflush(stdout);
    g_post_swap_joined++;
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

static void count_writer_pc_phase(int phase, int watch, uint32_t pc)
{
    struct writer_pc_hist *hist = &g_pc_hist_phase[phase][watch];
    int i;

    for (i = 0; i < hist->n; i++) {
        if (hist->entries[i].pc == pc) {
            hist->entries[i].n++;
            return;
        }
    }
    if (hist->n < MAX_WRITER_PCS) {
        hist->entries[hist->n].pc = pc;
        hist->entries[hist->n].n = 1;
        hist->n++;
    } else {
        hist->overflow++;
    }
}

static void request_checkpoint(int signo)
{
    (void)signo;
    g_checkpoint_requested = 1;
}

/* Signal only requests a report; all debugger/core reads stay on the emulator
 * thread in dbg_vi, where they cannot race the interpreter. */
static void emit_checkpoint(void)
{
    int phase, watch, i;
    unsigned width = pDebugMemRead32(VI_WIDTH_ADDR);
    unsigned origin = pDebugMemRead32(VI_ORIGIN_ADDR);

    printf("[oracle-checkpoint] t=%.1fs vi=%ld width=%u origin=0x%08x hits=%ld pc_hits=%ld\n",
           now_s() - g_t0, g_vis, width, origin, g_hits, g_pc_hits);
    for (watch = 0; watch < g_nwatch; watch++)
        printf("[oracle-checkpoint-watch] watch=%d range=[0x%08x,0x%08x) hits=%ld reads=%ld writes=%ld\n",
               watch, g_watch[watch].start, g_watch[watch].end,
               g_watch[watch].hits, g_watch[watch].read_hits,
               g_watch[watch].write_hits);
    for (phase = 0; phase < g_n_pc_hist_phase; phase++) {
        printf("[oracle-checkpoint-phase] origin=0x%08x width=%u vi=%ld\n",
               g_pc_hist_phase_origin[phase], g_pc_hist_phase_width[phase],
               g_pc_hist_phase_vis[phase]);
        for (watch = 0; watch < g_nwatch; watch++) {
            if (!(g_pc_hist_watch_mask & (UINT64_C(1) << watch))) continue;
            printf("[oracle-checkpoint-hist] origin=0x%08x width=%u watch=%d\n",
                   g_pc_hist_phase_origin[phase], g_pc_hist_phase_width[phase], watch);
            for (i = 0; i < g_pc_hist_phase[phase][watch].n; i++)
                printf("[oracle-checkpoint-writer] origin=0x%08x width=%u watch=%d pc=0x%08x n=%ld\n",
                       g_pc_hist_phase_origin[phase], g_pc_hist_phase_width[phase],
                       watch, g_pc_hist_phase[phase][watch].entries[i].pc,
                       g_pc_hist_phase[phase][watch].entries[i].n);
        }
    }
    for (watch = 0; watch < g_nwatch; watch++) {
        struct post_value_stats *stats;
        if (!(g_post_value_watch_mask & (UINT64_C(1) << watch)))
            continue;
        stats = &g_post_value_stats[watch];
        printf("[oracle-checkpoint-post-value] watch=%d samples=%ld unique=%d overflow=%ld\n",
               watch, stats->samples, stats->n_hist, stats->overflow);
        for (i = 0; i < stats->n_hist; i++)
            printf("[oracle-checkpoint-post-value-word] watch=%d value=0x%08x n=%ld\n",
                   watch, stats->hist[i].value, stats->hist[i].n);
        for (i = 0; i < stats->n_pc; i++)
            printf("[oracle-checkpoint-post-value-pc] watch=%d pc=0x%08x samples=%ld zero=%ld nonzero=%ld\n",
                   watch, stats->pc[i].pc, stats->pc[i].samples,
                   stats->pc[i].zero_words, stats->pc[i].nonzero_words);
    }
    fflush(stdout);
}

/* A byte clear can leave its containing word nonzero. Compare only the
 * bytes written by the instruction, using big-endian guest byte lanes. */
static uint32_t scalar_store_mask(uint32_t instruction, uint32_t address)
{
    unsigned lane = address & 3u;
    switch (instruction >> 26) {
    case 0x28: return 0xFFu << ((3u - lane) * 8u);
    case 0x29: return (lane & 1u) ? 0u : 0xFFFFu << ((2u - lane) * 8u);
    case 0x2B: return lane ? 0u : UINT32_MAX;
    default: return 0u;
    }
}

static uint32_t scalar_store_expected(uint32_t mask, uint32_t value)
{
    if (!mask) return 0;
    unsigned shift = 0;
    while (!(mask & (1u << shift))) shift++;
    return (value << shift) & mask;
}

static void count_scalar_store(struct post_value_pc_entry *entry, uint32_t value)
{
    if (!g_post_store_mask) return;
    uint32_t stored = value & g_post_store_mask;
    entry->scalar_samples++;
    entry->scalar_zero += stored == 0;
    entry->scalar_nonzero += stored != 0;
    entry->scalar_mismatch += stored != g_post_store_expected;
}

static void count_post_value(int watch, uint32_t pc, uint32_t value)
{
    struct post_value_stats *stats;
    int i, found = 0;
    if (watch < 0 || watch >= MAX_WATCHES)
        return;
    stats = &g_post_value_stats[watch];
    stats->samples++;
    for (i = 0; i < stats->n_hist; i++) {
        if (stats->hist[i].value == value) {
            stats->hist[i].n++;
            found = 1;
            break;
        }
    }
    if (!found && stats->n_hist < MAX_POST_VALUE_HIST) {
        stats->hist[stats->n_hist].value = value;
        stats->hist[stats->n_hist].n = 1;
        stats->n_hist++;
    } else if (!found) {
        stats->overflow++;
    }
    for (i = 0; i < stats->n_pc; i++) {
        if (stats->pc[i].pc == pc) {
            count_scalar_store(&stats->pc[i], value);
            stats->pc[i].samples++;
            if (value == 0)
                stats->pc[i].zero_words++;
            else
                stats->pc[i].nonzero_words++;
            return;
        }
    }
    if (stats->n_pc < MAX_POST_VALUE_PCS) {
        stats->pc[stats->n_pc].pc = pc;
        stats->pc[stats->n_pc].samples = 1;
        stats->pc[stats->n_pc].zero_words = value == 0;
        stats->pc[stats->n_pc].nonzero_words = value != 0;
        count_scalar_store(&stats->pc[stats->n_pc], value);
        stats->n_pc++;
    } else {
        stats->pc_overflow++;
    }
}

static void record_post_value_requested_row(int target, uint32_t value,
                                            long vi, uint32_t width,
                                            uint32_t origin)
{
    struct post_value_requested_row *row;

    if (target < 0 || target >= g_n_post_value_requested_pc)
        return;
    if (width != 512 || origin != 0x006AB400)
        return;
    if (value == 0x7F7F7F7F)
        return;
    if (g_n_post_value_requested_rows[target] >= MAX_POST_VALUE_ROWS_PER_PC)
        return;
    row = &g_post_value_requested_rows[target]
        [g_n_post_value_requested_rows[target]++];
    row->vi = vi;
    row->width = width;
    row->origin = origin;
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

static void record_post_value_requested_sequence(int target, uint32_t value,
                                                 long vi, uint32_t width,
                                                 uint32_t origin)
{
    struct post_value_requested_sequence_row *row;

    if (target < 0 || target >= g_n_post_value_requested_pc)
        return;
    if (width != 512 || origin != 0x006AB400)
        return;
    g_post_value_requested_sequence_count[target]++;
    if (g_n_post_value_requested_sequence >= MAX_POST_VALUE_SEQUENCE_ROWS) {
        g_post_value_requested_sequence_overflow++;
        return;
    }
    row = &g_post_value_requested_sequence[g_n_post_value_requested_sequence];
    row->ordinal = g_n_post_value_requested_sequence + 1;
    row->pc = g_post_value_requested_pc[target];
    row->vi = vi;
    row->addr = g_post_value_addr & ~3u;
    row->value = value;
    row->sentinel = value == 0x7F7F7F7F;
    g_n_post_value_requested_sequence++;
}

static void record_post_value_pc_detail(uint32_t pc, uint32_t value,
                                        long vi, uint32_t width,
                                        uint32_t origin)
{
    struct post_value_pc_detail_row *row;

    if (!g_post_value_pc_detail)
        return;
    if (g_post_value_pc_detail_phase &&
        (width != g_post_value_pc_detail_width ||
         origin != g_post_value_pc_detail_origin))
        return;
    if (g_n_post_value_pc_detail_rows >= MAX_POST_VALUE_PC_DETAIL_ROWS) {
        g_post_value_pc_detail_overflow++;
        return;
    }
    row = &g_post_value_pc_detail_rows[g_n_post_value_pc_detail_rows++];
    row->pc = pc;
    row->vi = vi;
    row->width = width;
    row->origin = origin;
    row->addr = g_post_value_addr & ~3u;
    row->value = value;
}

static void record_post_value_requested_class(int target, uint32_t value,
                                               long vi, uint32_t width,
                                               uint32_t origin)
{
    struct post_value_requested_class *stats;
    uint32_t addr;
    int class_index;

    if (target < 0 || target >= g_n_post_value_requested_pc)
        return;
    if (width != 512 || origin != 0x006AB400)
        return;
    class_index = value == 0x7F7F7F7F ? 0 : 1;
    stats = &g_post_value_requested_classes[target][class_index];
    addr = g_post_value_addr & ~3u;
    stats->samples++;
    if (!stats->first.valid) {
        stats->first.vi = vi;
        stats->first.addr = addr;
        stats->first.value = value;
        stats->first.valid = 1;
    }
    stats->last.vi = vi;
    stats->last.addr = addr;
    stats->last.value = value;
    stats->last.valid = 1;
}

static int post_value_pc_seen(int watch, uint32_t pc)
{
    struct post_value_stats *stats;
    int i;
    if (watch < 0 || watch >= MAX_WATCHES)
        return 0;
    stats = &g_post_value_stats[watch];
    for (i = 0; i < stats->n_pc; i++) {
        if (stats->pc[i].pc == pc)
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
    g_post_value_stats[watch].snapshot_fnv = fnv;
    g_post_value_stats[watch].snapshot_nonzero = nonzero;
    g_post_value_stats[watch].snapshot_bytes = bytes;
    g_post_value_stats[watch].snapshot_valid = 1;
}

static void capture_phase_snapshot(int watch, unsigned width, unsigned origin)
{
    struct phase_snapshot *snapshot;
    uint32_t addr;
    int phase = -1;

    if (watch < 0 || watch >= g_nwatch ||
        !(g_phase_snapshot_watch_mask & (UINT64_C(1) << watch)))
        return;
    if ((width == 1024 && origin == 0x00790400u)) phase = 0;
    if ((width == 512 && origin == 0x006AB400u)) phase = 1;
    if (phase < 0 || g_phase_snapshots[watch][phase].valid)
        return;
    if (g_watch[watch].end - g_watch[watch].start > 4096u)
        return;

    snapshot = &g_phase_snapshots[watch][phase];
    snapshot->origin = origin;
    snapshot->width = width;
    snapshot->vi = g_vis;
    snapshot->fnv = 2166136261u;
    for (addr = g_watch[watch].start; addr < g_watch[watch].end; addr += 4) {
        uint32_t word = pDebugMemRead32(debug_rdram_addr(addr));
        for (unsigned lane = 0; lane < 4 && addr + lane < g_watch[watch].end; lane++) {
            unsigned byte = (word >> ((3u - lane) * 8u)) & 0xFFu;
            snapshot->values[addr + lane - g_watch[watch].start] = (unsigned char)byte;
            snapshot->fnv = (snapshot->fnv * 16777619u) ^ byte;
            snapshot->nonzero += byte != 0;
            snapshot->bytes++;
        }
    }
    snapshot->valid = 1;
}

static void emit_phase_snapshot(int watch, int phase)
{
    struct phase_snapshot *snapshot;
    uint32_t addr;

    if (watch < 0 || watch >= g_nwatch || phase < 0 || phase >= MAX_PHASE_SNAPSHOTS)
        return;
    snapshot = &g_phase_snapshots[watch][phase];
    if (!snapshot->valid)
        return;
    printf("[oracle] phase-snapshot watch=%d phase=%d vi=%ld width=%u origin=0x%08x bytes=%lu nonzero=%lu fnv=0x%08x\n",
           watch, phase, snapshot->vi, snapshot->width, snapshot->origin,
           snapshot->bytes, snapshot->nonzero, snapshot->fnv);
    for (addr = g_watch[watch].start; addr < g_watch[watch].end; addr++) {
        unsigned byte = snapshot->values[addr - g_watch[watch].start];
        if (byte != 0)
            printf("[oracle] phase-snapshot-byte watch=%d phase=%d offset=0x%04x value=0x%02x\n",
                   watch, phase, addr - g_watch[watch].start, byte);
    }
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

static void arm_watch(int i);

/* Installs every --watch-* the user asked for. Split out of dbg_init() (see
 * below) so it can be deferred to first VI instead of running at debugger
 * init. */
static void arm_watches(void)
{
    int i;
    for (i = 0; i < g_nwatch; i++) {
        if (g_watch[i].flags & M64P_BKP_FLAG_EXEC && g_defer_exec_watches)
            continue;
        arm_watch(i);
    }
    fflush(stdout);
}

static void arm_watch(int i)
{
    m64p_breakpoint bkp;
    int idx;

    if (g_watch[i].armed)
        return;
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
        g_watch[i].breakpoint_idx = idx;
        g_watch[i].armed = 1;
        printf("[watch] %s [0x%08x,0x%08x) flags=0x%x idx=%d\n",
               g_watch[i].label, g_watch[i].start, g_watch[i].end,
               bkp.flags, idx);
    }
}

static void arm_deferred_exec_watches(unsigned width, unsigned origin)
{
    int i;
    if (g_exec_watches_phase_armed || !g_defer_exec_watches)
        return;
    for (i = 0; i < g_n_pc_phase_log_origin; i++) {
        if (width == g_pc_phase_log[i].width &&
            origin == g_pc_phase_log[i].origin) {
            g_exec_watches_phase_armed = 1;
            printf("[phase-arm] width=%u origin=0x%08x\n", width, origin);
            for (i = 0; i < g_nwatch; i++)
                if (g_watch[i].flags & M64P_BKP_FLAG_EXEC)
                    arm_watch(i);
            fflush(stdout);
            return;
        }
    }
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
        count_post_value(g_post_value_pending_watch, g_post_value_pc_addr, value);
        g_post_value_pending_watch = -1;
        if (g_post_value_pending_target >= 0) {
            int target = g_post_value_pending_target;
            g_post_value_pending_target = -1;
            record_post_value_pc_detail(g_post_value_pc_addr, value,
                                        g_post_value_pending_vi,
                                        g_post_value_pending_width,
                                        g_post_value_pending_origin);
            record_post_value_requested_sequence(target, value,
                                                 g_post_value_pending_vi,
                                                 g_post_value_pending_width,
                                                 g_post_value_pending_origin);
            record_post_value_requested_class(target, value,
                                              g_post_value_pending_vi,
                                              g_post_value_pending_width,
                                              g_post_value_pending_origin);
            record_post_value_requested_row(target, value,
                                             g_post_value_pending_vi,
                                             g_post_value_pending_width,
                                             g_post_value_pending_origin);
        }
        pDebugSetRunState(M64P_DBG_RUNSTATE_RUNNING);
        pDebugStep();
        return;
    }

    pDebugBreakpointTriggeredBy(&flags, &accessed);
    access_flags = flags & (M64P_BKP_FLAG_READ | M64P_BKP_FLAG_WRITE);
    g_event_ordinal++;

    if ((access_flags & M64P_BKP_FLAG_WRITE) && pc_phase_log_match()) {
        int span_i;
        uint32_t physical = accessed & 0x1FFFFFFFu;
        for (span_i = 0; span_i < g_n_c904_input_spans; span_i++) {
            struct c904_input_span *span = &g_c904_input_spans[span_i];
            if (physical >= span->input && physical < span->input + 8u) {
                uint32_t instruction =
                    pDebugMemRead32(debug_rdram_addr(pc));
                unsigned source_reg = (instruction >> 16) & 31u;
                printf("[c904-input-writer] span=0x%08x..0x%08x width=%u origin=0x%08x addr=0x%08x pc=0x%08x source=0x%08x\n",
                       span->input, span->input + 8u, span->width,
                       span->origin, physical, pc, gpr32((int)source_reg));
                fflush(stdout);
                g_c904_input_writer_hits++;
                break;
            }
        }
    }

    if ((flags & M64P_BKP_FLAG_EXEC) && pc == VI_SWAP_PC &&
        pDebugMemRead32(VI_WIDTH_ADDR) == 640) {
        count_vi_swap_phase(pDebugMemRead32(VI_ORIGIN_ADDR),
                            (uint32_t)pDebugGetState(M64P_DBG_PREVIOUS_PC),
                            gpr32(4) & 0x1FFFFFFFu);
    }

    if ((flags & M64P_BKP_FLAG_EXEC) && pc == AI_SET_NEXT_PC)
        dump_ai_output();

    if (flags & M64P_BKP_FLAG_EXEC)
        dump_pc_field(pc);

    if (flags & M64P_BKP_FLAG_EXEC)
        dump_c904_witness(pc);

    if (flags & M64P_BKP_FLAG_EXEC)
        dump_pc_task(pc);

    if (flags & M64P_BKP_FLAG_EXEC)
        dump_boundary_join(pc);

    if ((flags & M64P_BKP_FLAG_EXEC) &&
        pc >= 0x80033C00u && pc < 0x80034100u)
        dump_pc_range_task(pc);

    if ((flags & M64P_BKP_FLAG_EXEC) && g_mode_dump_enabled &&
        pc == g_mode_dump_pc)
        dump_mode_descriptor(pc);

    if (flags & M64P_BKP_FLAG_EXEC)
        latch_post_swap_table(pc);

    if (flags & M64P_BKP_FLAG_EXEC)
        latch_vi_context_table(pc);

    if (!g_gpr_ctl_printed) {
        g_gpr_ctl_printed = 1;
        printf("[gpr-ctl] pc=0x%08x", pc);
        print_gpr_fields();
        printf(" flags=0x%x\n", flags);
        fflush(stdout);
    }

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
            if ((g_pc_hist_watch_mask & (UINT64_C(1) << i)) &&
                (access_flags & M64P_BKP_FLAG_WRITE)) {
                count_writer_pc(i, pc);
                if (g_n_pc_hist_phase > 0) {
                    unsigned width = pDebugMemRead32(VI_WIDTH_ADDR);
                    unsigned origin = pDebugMemRead32(VI_ORIGIN_ADDR);
                    for (int phase = 0; phase < g_n_pc_hist_phase; phase++) {
                        if (width == g_pc_hist_phase_width[phase] &&
                            origin == g_pc_hist_phase_origin[phase])
                            count_writer_pc_phase(phase, i, pc);
                    }
                }
            }
            if (g_ordinal_join_enabled &&
                (access_flags & M64P_BKP_FLAG_WRITE) &&
                i > 0 && pc_phase_log_match()) {
                if (g_n_ordinal_writes < MAX_ORDINAL_WRITES) {
                    struct ordinal_write_row *write =
                        &g_ordinal_writes[g_n_ordinal_writes++];
                    uint32_t instruction = pDebugMemRead32(pc);
                    uint32_t effective = gpr32((instruction >> 21) & 31u) +
                        (uint32_t)(int32_t)(int16_t)instruction;
                    write->watch = i;
                    write->pc = pc;
                    write->store_addr = accessed;
                    write->instruction = instruction;
                    write->effective_addr = effective;
                    write->source_reg = (instruction >> 16) & 31u;
                    write->source_value = gpr32(write->source_reg);
                    write->scalar_mask = ((effective & 0x1FFFFFFCu) ==
                                          (accessed & 0x1FFFFFFCu)) ?
                        scalar_store_mask(instruction, effective) : 0;
                    write->pre_store_word =
                        pDebugMemRead32(debug_rdram_addr(accessed & ~3u));
                    write->post_store_word = write->scalar_mask
                        ? ((write->pre_store_word & ~write->scalar_mask) |
                           (write->source_value & write->scalar_mask))
                        : 0;
                    write->width = pDebugMemRead32(VI_WIDTH_ADDR);
                    write->origin = pDebugMemRead32(VI_ORIGIN_ADDR);
                    write->event_ordinal = g_event_ordinal;
                } else {
                    g_ordinal_write_overflow++;
                }
            }
            if ((access_flags & M64P_BKP_FLAG_WRITE) &&
                (g_n_store_field_dump_pc > 0 || g_store_field_dump_all_mask != 0))
                dump_store_field(i, pc, accessed);
            if ((g_post_value_watch_mask & (UINT64_C(1) << i)) &&
                (access_flags & M64P_BKP_FLAG_WRITE) &&
                g_post_value_armed) {
                int target = post_value_requested_index(pc);
                int force_target = target >= 0;
                int sample_generic = g_post_value_stats[i].samples < MAX_POST_VALUE_SAMPLES ||
                    (!post_value_pc_seen(i, pc) &&
                     g_post_value_stats[i].n_pc < MAX_POST_VALUE_PCS);
                if (force_target || sample_generic) {
                    g_post_value_pending = 1;
                    g_post_value_pending_target = force_target ? target : -1;
                    g_post_value_pending_watch = i;
                    g_post_value_addr = accessed;
                    g_post_value_pc_addr = pc;
                    uint32_t instruction = pDebugMemRead32(pc);
                    /* The core reports a 4-byte memory transaction even for sb/sh. */
                    uint32_t effective = gpr32((instruction >> 21) & 31u) +
                        (uint32_t)(int32_t)(int16_t)instruction;
                    g_post_store_mask = ((effective & 0x1FFFFFFCu) ==
                                         (accessed & 0x1FFFFFFCu)) ?
                        scalar_store_mask(instruction, effective) : 0;
                    g_post_store_expected = scalar_store_expected(
                        g_post_store_mask, gpr32((instruction >> 16) & 31u));
                    g_post_value_pending_vi = g_vis;
                    g_post_value_pending_width = pDebugMemRead32(VI_WIDTH_ADDR);
                    g_post_value_pending_origin = pDebugMemRead32(VI_ORIGIN_ADDR);
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
            if (!getenv("RS64_DETAIL_HANGAR_READ") ||
                !(access_flags & M64P_BKP_FLAG_READ) ||
                (pDebugMemRead32(VI_WIDTH_ADDR) == 512u &&
                 pDebugMemRead32(VI_ORIGIN_ADDR) == 0x006AB400u)) {
                if (!(getenv("RS64_DETAIL_HANGAR_READ") &&
                      (access_flags & M64P_BKP_FLAG_READ) &&
                      g_detail_hangar_read_rows >= MAX_DETAIL_HANGAR_READ_ROWS)) {
                    detail_hit = 1;
                    if (getenv("RS64_DETAIL_HANGAR_READ") &&
                        (access_flags & M64P_BKP_FLAG_READ))
                        g_detail_hangar_read_rows++;
                }
            }
        if (g_first_watch == i && g_watch[i].hits == 1)
            detail_hit = 1;
    }
    /* Exec hits must print after the whole-RDRAM control fills --hit-cap.
     * Lifetime counts still go to the exec-prev histogram. */
    if ((flags & M64P_BKP_FLAG_EXEC) && g_exec_logged < EXEC_LOG_CAP) {
        detail_hit = 1;
        g_exec_logged++;
    }
    if ((flags & M64P_BKP_FLAG_EXEC) && !g_pc_phase_quiet && pc_phase_log_match())
        detail_hit = 1;
    if ((flags & M64P_BKP_FLAG_EXEC) && getenv("RS64_STACK_DUMP_PCS")) {
        char sb[24]; snprintf(sb, sizeof sb, "%08X", pc);
        if (strcasestr(getenv("RS64_STACK_DUMP_PCS"), sb)) detail_hit = 1;
    }
    if (!getenv("RS64_KEEP_POSITIVE_CONTROL") &&
        !g_positive_watch_removed && g_nwatch > 0 &&
        g_watch[0].write_hits == 10000) {
        int rc = pDebugBreakpointCommand(M64P_BKP_CMD_REMOVE_IDX,
                                          g_watch[0].breakpoint_idx, NULL);
        printf("[oracle] positive-control threshold reached: watch index 0 callbacks=%ld; removal rc=%d; watch index 1 remains armed\n",
               g_watch[0].write_hits, rc);
        fflush(stdout);
        g_positive_watch_removed = 1;
    }
    if (g_hits <= g_hit_cap || detail_hit) {
        unsigned int prev = (unsigned int)pDebugGetState(M64P_DBG_PREVIOUS_PC);
        printf("[hit] %s%s%s addr=0x%08x pc=0x%08x prev_pc=0x%08x t=%.1fs n=%ld",
               (flags & M64P_BKP_FLAG_WRITE) ? "w" : "",
               (flags & M64P_BKP_FLAG_READ)  ? "r" : "",
               (flags & M64P_BKP_FLAG_EXEC)  ? "x" : "",
               accessed, pc, prev, now_s() - g_t0, g_hits);
        if (flags & M64P_BKP_FLAG_EXEC) {
            unsigned width = pDebugMemRead32(VI_WIDTH_ADDR);
            unsigned origin = pDebugMemRead32(VI_ORIGIN_ADDR);
            print_gpr_fields();
            printf(" width=%u origin=0x%08x", width, origin);
            if (pc == 0x80019548u)
                printf(" w_a2p8=0x%08x",
                       pDebugMemRead32(debug_rdram_addr((gpr32(6) + 8) & ~3u)));
            if (pc == 0x80059D48u)
                printf(" w_a1p20=0x%08x",
                       pDebugMemRead32(debug_rdram_addr((gpr32(5) + 0x20) & ~3u)));
        }
        {   /* RS64_MEM_DUMP=hexvaddr:nwords: dump guest words at every printed hit */
            const char *m = getenv("RS64_MEM_DUMP");
            if (m) {
                uint32_t base = (uint32_t)strtoul(m, NULL, 16), nw = 8, o;
                const char *c = strchr(m, ':');
                if (c) nw = (uint32_t)strtoul(c + 1, NULL, 0);
                if (getenv("RS64_SRC_DUMP") && pc == 0x80034710u) { /* memcpy byte loop: v1-1 = src ptr */
                    uint32_t src = gpr32(3) - 1u;
                    printf(" ra=0x%08x src=0x%08x a2=0x%08x srcmem=", gpr32(31), src, gpr32(6));
                    for (o = 0; o < 8; o++)
                        printf("%08x,", pDebugMemRead32(debug_rdram_addr((src + o * 4) & 0x1FFFFFFFu)));
                }
                printf(" mem=");
                for (o = 0; o < nw && o < 64; o++)
                    printf("%08x,", pDebugMemRead32(debug_rdram_addr((base + o * 4) & 0x1FFFFFFFu)));
            }
        }
        {   /* RS64_STACK_DUMP_PCS=hexpc[,hexpc]: dump sp+0x18..0x90 words at those exec PCs */
            const char *e = getenv("RS64_STACK_DUMP_PCS");
            if (e) {
                char buf[128]; char *tok, *sv = NULL;
                strncpy(buf, e, sizeof buf - 1); buf[sizeof buf - 1] = 0;
                for (tok = strtok_r(buf, ",", &sv); tok; tok = strtok_r(NULL, ",", &sv)) {
                    if (tok[0] == '*' || (uint32_t)strtoul(tok, NULL, 16) == pc) {
                        uint32_t sp = gpr32(29), o;
                        printf(" sp=0x%08x stk=", sp);
                        for (o = 0x18; o < 0x90; o += 4)
                            printf("%08x,", pDebugMemRead32(debug_rdram_addr((sp + o) & 0x1FFFFFFFu)));
                    }
                }
            }
        }
        printf("\n");
        if (flags & M64P_BKP_FLAG_READ)
            printf("[read-value] addr=0x%08x value=0x%08x\n",
                   accessed, pDebugMemRead32(debug_rdram_addr(accessed & ~3u)));
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

    if (g_checkpoint_requested) {
        g_checkpoint_requested = 0;
        emit_checkpoint();
    }

    g_latched_phase_width = pDebugMemRead32(VI_WIDTH_ADDR);
    g_latched_phase_origin = pDebugMemRead32(VI_ORIGIN_ADDR);
    arm_deferred_exec_watches(g_latched_phase_width, g_latched_phase_origin);

    for (int watch = 0; watch < g_nwatch; watch++)
        capture_phase_snapshot(watch, g_latched_phase_width,
                               g_latched_phase_origin);

    if (g_post_swap_table_enabled) {
        width = pDebugMemRead32(VI_WIDTH_ADDR);
        origin = pDebugMemRead32(VI_ORIGIN_ADDR);
        join_post_swap_table(width, origin);
    }

    if (g_vi_context_table_enabled) {
        width = pDebugMemRead32(VI_WIDTH_ADDR);
        origin = pDebugMemRead32(VI_ORIGIN_ADDR);
        join_vi_context_table(width, origin);
    }

    if (g_n_pc_hist_phase > 0) {
        width = pDebugMemRead32(VI_WIDTH_ADDR);
        origin = pDebugMemRead32(VI_ORIGIN_ADDR);
        for (int phase = 0; phase < g_n_pc_hist_phase; phase++) {
            if (width == g_pc_hist_phase_width[phase] &&
                origin == g_pc_hist_phase_origin[phase])
                g_pc_hist_phase_vis[phase]++;
        }
    }

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

    if (g_post_value_watch_mask) {
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
                    printf("[oracle-status-poll] t=%6.1fs vi=%ld width=%u origin=0x%08x slot=%d addr=0x%08x word=0x%08x top=0x%02x low=0x%02x\n",
                           t, g_vis, width, origin, i, addr, word, status, word & 0xFFu);
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

static void add_pc_range_watch(const char *arg)
{
    char *copy = strdup(arg), *colon;
    uint32_t start, end;
    if (!copy) exit(2);
    colon = strchr(copy, ':');
    if (!colon) {
        fprintf(stderr, "[oracle] bad PC range '%s' (want START:END, END exclusive)\n", arg);
        free(copy);
        exit(2);
    }
    *colon++ = 0;
    start = (uint32_t)strtoul(copy, NULL, 0);
    end = (uint32_t)strtoul(colon, NULL, 0);
    free(copy);
    if (end <= start) {
        fprintf(stderr, "[oracle] bad PC range '%s' (want START:END, END exclusive)\n", arg);
        exit(2);
    }
    if (g_nwatch >= MAX_WATCHES) {
        fprintf(stderr, "[oracle] too many watches\n");
        exit(2);
    }
    g_watch[g_nwatch].start = start;
    g_watch[g_nwatch].end = end;
    g_watch[g_nwatch].flags = M64P_BKP_FLAG_EXEC;
    g_watch[g_nwatch].label = "pc-range";
    g_nwatch++;
}

static void usage(void)
{
    fprintf(stderr,
        "usage: rs64_oracle --rom PATH [options]\n"
        "  --watch-write A[:B]   log writes to physical [A,B), e.g. 0x1F3CC0:0x1F3CD0\n"
        "  --watch-read  A[:B]   log reads\n"
        "  --watch-rw    A[:B]   log both\n"
        "  --watch-pc    A[,B...] watch execution at guest PCs (prints $v0/$s1/$a0/$a2)\n"
        "  --watch-pc-range A:B watch execution across a guest PC range\n"
        "  --secs N              run for N seconds (default 120)\n"
        "  --hit-cap N           log at most N hits, then count silently (default 200)\n"
        "  --detail-watch N      always log hits for watch index N\n"
        "  --pc-phase-log ORIGIN log watched execs only at 640-width VI origin (repeatable)\n"
        "  --pc-phase-log-width ORIGIN:WIDTH log watched execs at an explicit VI bucket\n"
        "  --pc-field-dump A[,B...] dump phase-gated $s0/$s1 and pointed fields\n"
        "  --pc-field-dump-any-phase allow field rows before/after phase buckets\n"
        "  --boundary-join     join C950/C954/D78C/D790/DC38 to latest phase task\n"
        "  --c904-witness       dump phase-gated C904 entry and selected-word reader rows\n"
        "  --c904-task-join    join C904/C950 witnesses to latest phase task row\n"
        "  --store-field-dump W:A[,B...] dump phase-gated fields at exact writes on watch W\n"
        "  --store-field-dump-all W dump phase-gated fields at every write on watch W\n"
        "  --store-field-dump-any-phase allow store-field-dump rows in any VI phase\n"
        "  --pc-task-dump A   dump phase-gated OSTask fields at PC A\n"
        "  --pc-task-type N   OSTask type to dump (default 2=audio; 1=gfx; 0=any)\n"
        "  --pc-range-task-dump dump phase-gated $a0/task fields for the live range\n"
        "  --pc-task-join     join each field dump to the latest valid task row in its VI bucket\n"
        "  --ordinal-join     order exact target writes against nearest phase task rows\n"
        "  --pc-phase-quiet   suppress per-hit phase execution lines (keep bounded dumps)\n"
        "  --mode-dump-pc A     dump 640-wide mode descriptors for watched execution PC A\n"
        "  --post-swap-table-pc A join a 640-wide swap at A to the following VI callback\n"
        "  --post-swap-any-vi      allow the post-swap join to accept any next VI width/origin\n"
        "  --vi-context-table-pc A join __osViNext at 640-wide execution A to the following VI callback\n"
        "  --vi-context-any-vi     allow the VI context join to accept any next VI width/origin\n"
        "  --first-watch N       log the first hit for watch index N\n"
        "  --pc-hist-watch N     summarize writer PCs for watch index N (repeatable)\n"
        "  --pc-hist-phase ORIGIN[:WIDTH]  add a writer histogram bucket (default WIDTH=640)\n"
        "  --post-value-watch N  sample post-store words and final range summary\n"
        "  --phase-snapshot-watch N  capture exact nonzero bytes at target VI phases\n"
        "  --post-value-pc A[,B] force one post-store sample for writer PCs\n"
        "  --post-value-pc-detail  print every requested-writer post-store tuple\n"
        "  --post-value-pc-detail-phase ORIGIN:WIDTH  limit detail tuples to one VI phase\n"
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
        else if (!strcmp(argv[i], "--pc-phase-log") && i + 1 < argc) {
            char *spec = argv[++i], *tok, *save = NULL;
            for (tok = strtok_r(spec, ",", &save);
                 tok && g_n_pc_phase_log_origin < MAX_PC_PHASE_LOG_ORIGINS;
                 tok = strtok_r(NULL, ",", &save))
            {
                g_pc_phase_log[g_n_pc_phase_log_origin].origin =
                    to_phys((uint32_t)strtoul(tok, NULL, 0));
                g_pc_phase_log[g_n_pc_phase_log_origin].width = 640;
                g_n_pc_phase_log_origin++;
            }
        }
        else if (!strcmp(argv[i], "--pc-phase-log-width") && i + 1 < argc)
            add_pc_phase_log_width(argv[++i]);
        else if (!strcmp(argv[i], "--pc-field-dump") && i + 1 < argc)
            add_pc_field_dump_pcs(argv[++i]);
        else if (!strcmp(argv[i], "--pc-field-dump-any-phase"))
            g_pc_field_dump_any_phase = 1;
        else if (!strcmp(argv[i], "--boundary-join")) {
            g_boundary_join_enabled = 1;
            add_pc_watches("0x8009C950,0x8009C954,0x8009D78C,0x8009D790,0x8009DC38");
        }
        else if (!strcmp(argv[i], "--c904-witness")) {
            g_c904_witness_enabled = 1;
            add_pc_watches("0x8009C0E8,0x8009C904,0x8009C950");
        }
        else if (!strcmp(argv[i], "--c904-task-join"))
            g_c904_task_join_enabled = 1;
        else if (!strcmp(argv[i], "--store-field-dump") && i + 1 < argc)
            add_store_field_dump(argv[++i]);
        else if (!strcmp(argv[i], "--store-field-dump-all") && i + 1 < argc)
            add_store_field_dump_all(argv[++i]);
        else if (!strcmp(argv[i], "--store-field-dump-any-phase"))
            g_store_field_dump_any_phase = 1;
        else if (!strcmp(argv[i], "--pc-task-dump") && i + 1 < argc) {
            g_pc_task_dump_pc = (uint32_t)strtoul(argv[++i], NULL, 0);
            g_pc_task_dump_enabled = 1;
        }
        else if (!strcmp(argv[i], "--pc-task-join"))
            g_pc_task_join_enabled = 1;
        else if (!strcmp(argv[i], "--ordinal-join"))
            g_ordinal_join_enabled = 1;
        else if (!strcmp(argv[i], "--pc-phase-quiet"))
            g_pc_phase_quiet = 1;
        else if (!strcmp(argv[i], "--pc-task-type") && i + 1 < argc)
            g_pc_task_dump_type = (uint32_t)strtoul(argv[++i], NULL, 0);
        else if (!strcmp(argv[i], "--pc-range-task-dump"))
            g_pc_range_task_dump_enabled = 1;
        else if (!strcmp(argv[i], "--mode-dump-pc") && i + 1 < argc) {
            g_mode_dump_pc = (uint32_t)strtoul(argv[++i], NULL, 0);
            g_mode_dump_enabled = 1;
        }
        else if (!strcmp(argv[i], "--post-swap-table-pc") && i + 1 < argc) {
            g_post_swap_table_pc = (uint32_t)strtoul(argv[++i], NULL, 0);
            g_post_swap_table_enabled = 1;
        }
        else if (!strcmp(argv[i], "--post-swap-any-vi"))
            g_post_swap_any_vi = 1;
        else if (!strcmp(argv[i], "--vi-context-table-pc") && i + 1 < argc) {
            g_vi_context_table_pc = (uint32_t)strtoul(argv[++i], NULL, 0);
            g_vi_context_table_enabled = 1;
        }
        else if (!strcmp(argv[i], "--vi-context-any-vi"))
            g_vi_context_any_vi = 1;
        else if (!strcmp(argv[i], "--first-watch") && i + 1 < argc)
            g_first_watch = atoi(argv[++i]);
        else if (!strcmp(argv[i], "--pc-hist-watch") && i + 1 < argc) {
            int watch = atoi(argv[++i]);
            if (watch >= 0 && watch < MAX_WATCHES)
                g_pc_hist_watch_mask |= UINT64_C(1) << watch;
        }
        else if (!strcmp(argv[i], "--pc-hist-phase") && i + 1 < argc) {
            char *spec = argv[++i];
            char *colon = strchr(spec, ':');
            uint32_t width = 640;
            if (g_n_pc_hist_phase >= MAX_PC_HIST_PHASES) {
                fprintf(stderr, "[oracle] too many --pc-hist-phase buckets\n");
                return 2;
            }
            if (colon) {
                *colon = 0;
                width = (uint32_t)strtoul(colon + 1, NULL, 0);
                if (width == 0) {
                    fprintf(stderr, "[oracle] bad --pc-hist-phase width\n");
                    return 2;
                }
            }
            g_pc_hist_phase_origin[g_n_pc_hist_phase++] =
                to_phys((uint32_t)strtoul(spec, NULL, 0));
            g_pc_hist_phase_width[g_n_pc_hist_phase - 1] = width;
        }
        else if (!strcmp(argv[i], "--post-value-watch") && i + 1 < argc) {
            int watch = atoi(argv[++i]);
            if (watch >= 0 && watch < MAX_WATCHES)
                g_post_value_watch_mask |= UINT64_C(1) << watch;
        }
        else if (!strcmp(argv[i], "--phase-snapshot-watch") && i + 1 < argc) {
            int watch = atoi(argv[++i]);
            if (watch >= 0 && watch < MAX_WATCHES)
                g_phase_snapshot_watch_mask |= UINT64_C(1) << watch;
        }
        else if (!strcmp(argv[i], "--post-value-pc") && i + 1 < argc)
            add_post_value_pcs(argv[++i]);
        else if (!strcmp(argv[i], "--post-value-pc-detail"))
            g_post_value_pc_detail = 1;
        else if (!strcmp(argv[i], "--post-value-pc-detail-phase") && i + 1 < argc) {
            char *spec = argv[++i];
            char *colon = strchr(spec, ':');
            if (!colon || colon == spec || !colon[1]) {
                fprintf(stderr, "[oracle] bad --post-value-pc-detail-phase '%s' (want ORIGIN:WIDTH)\n", spec);
                return 2;
            }
            *colon = 0;
            g_post_value_pc_detail_origin = to_phys((uint32_t)strtoul(spec, NULL, 0));
            g_post_value_pc_detail_width = (uint32_t)strtoul(colon + 1, NULL, 0);
            if (!g_post_value_pc_detail_width) {
                fprintf(stderr, "[oracle] bad --post-value-pc-detail-phase width\n");
                return 2;
            }
            g_post_value_pc_detail_phase = 1;
        }
        else if (!strcmp(argv[i], "--watch-write") && i + 1 < argc)
            add_watch(argv[++i], M64P_BKP_FLAG_WRITE, "write");
        else if (!strcmp(argv[i], "--watch-read") && i + 1 < argc)
            add_watch(argv[++i], M64P_BKP_FLAG_READ, "read");
        else if (!strcmp(argv[i], "--watch-rw") && i + 1 < argc)
            add_watch(argv[++i], M64P_BKP_FLAG_READ | M64P_BKP_FLAG_WRITE, "rw");
        else if (!strcmp(argv[i], "--watch-pc") && i + 1 < argc)
            add_pc_watches(argv[++i]);
        else if (!strcmp(argv[i], "--watch-pc-range") && i + 1 < argc)
            add_pc_range_watch(argv[++i]);
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
    g_defer_exec_watches = g_n_pc_phase_log_origin > 0;
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
    SYM(pDebugGetCPUDataPtr, "DebugGetCPUDataPtr");
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

    signal(SIGUSR1, request_checkpoint);

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
    for (int i = 0; i < 3; i++)
        printf("[oracle] ai-output-summary bucket=%s calls=%ld rows=%ld nonzero_rows=%ld\n",
               g_ai_output[i].name, g_ai_output[i].calls, g_ai_output[i].rows,
               g_ai_output[i].nonzero_rows);
    if (g_post_value_watch_mask) {
        for (int watch = 0; watch < g_nwatch; watch++) {
            struct post_value_stats *stats;
            if (!(g_post_value_watch_mask & (UINT64_C(1) << watch)))
                continue;
            stats = &g_post_value_stats[watch];
            summarize_post_snapshot(watch);
            printf("[oracle] post-value watch=%d range=[0x%08x,0x%08x) samples=%ld unique=%d overflow=%ld\n",
                   watch, g_watch[watch].start, g_watch[watch].end,
                   stats->samples, stats->n_hist, stats->overflow);
            for (int j = 0; j < stats->n_hist; j++)
                printf("[oracle] post-value watch=%d value=0x%08x n=%ld\n",
                       watch, stats->hist[j].value, stats->hist[j].n);
            for (int j = 0; j < stats->n_pc; j++)
                printf("[oracle] post-value-pc watch=%d pc=0x%08x samples=%ld zero=%ld nonzero=%ld\n",
                       watch, stats->pc[j].pc, stats->pc[j].samples,
                       stats->pc[j].zero_words, stats->pc[j].nonzero_words);
            for (int j = 0; j < stats->n_pc; j++)
                printf("[oracle] post-store-scalar watch=%d pc=0x%08x samples=%ld zero=%ld nonzero=%ld mismatch=%ld unsupported=%ld\n",
                       watch, stats->pc[j].pc, stats->pc[j].scalar_samples,
                       stats->pc[j].scalar_zero, stats->pc[j].scalar_nonzero,
                       stats->pc[j].scalar_mismatch,
                       stats->pc[j].samples - stats->pc[j].scalar_samples);
            if (stats->pc_overflow)
                printf("[oracle] post-value-pc watch=%d overflow=%ld\n",
                       watch, stats->pc_overflow);
            if (stats->snapshot_valid)
                printf("[oracle] post-value snapshot watch=%d bytes=%lu nonzero=%lu fnv=0x%08x\n",
                       watch, stats->snapshot_bytes, stats->snapshot_nonzero,
                       stats->snapshot_fnv);
        }
        for (int j = 0; j < g_n_post_value_requested_pc; j++)
            printf("[oracle] post-target-summary pc=0x%08x seen=%d addr=0x%08x value=0x%08x\n",
                   g_post_value_requested_pc[j], g_post_value_requested_seen[j],
                   g_post_value_requested_addr[j], g_post_value_requested_value[j]);
        for (int j = 0; j < g_n_post_value_requested_pc; j++) {
            const char *class_name;
            for (int k = 0; k < 2; k++) {
                struct post_value_requested_class *stats =
                    &g_post_value_requested_classes[j][k];
                class_name = k == 0 ? "sentinel" : "non-sentinel";
                printf("[oracle] post-target-class pc=0x%08x class=%s samples=%ld "
                       "first_valid=%d first_vi=%ld first_addr=0x%08x "
                       "first_value=0x%08x last_valid=%d last_vi=%ld "
                       "last_addr=0x%08x last_value=0x%08x\n",
                       g_post_value_requested_pc[j], class_name, stats->samples,
                       stats->first.valid, stats->first.vi, stats->first.addr,
                       stats->first.value, stats->last.valid, stats->last.vi,
                       stats->last.addr, stats->last.value);
            }
        }
        for (int j = 0; j < g_n_post_value_requested_pc; j++) {
            printf("[oracle] post-target-rows pc=0x%08x n=%d/%d\n",
                   g_post_value_requested_pc[j],
                   g_n_post_value_requested_rows[j],
                   MAX_POST_VALUE_ROWS_PER_PC);
            for (int k = 0; k < g_n_post_value_requested_rows[j]; k++)
                printf("[oracle] post-target-row-final pc=0x%08x vi=%ld width=%u origin=0x%08x addr=0x%08x value=0x%08x\n",
                       g_post_value_requested_pc[j],
                       g_post_value_requested_rows[j][k].vi,
                       g_post_value_requested_rows[j][k].width,
                       g_post_value_requested_rows[j][k].origin,
                       g_post_value_requested_rows[j][k].addr,
                       g_post_value_requested_rows[j][k].value);
        }
        printf("[oracle] post-target-sequence n=%d/%d overflow=%ld\n",
               g_n_post_value_requested_sequence,
               MAX_POST_VALUE_SEQUENCE_ROWS,
               g_post_value_requested_sequence_overflow);
        for (int j = 0; j < g_n_post_value_requested_pc; j++)
            printf("[oracle] post-target-sequence-count pc=0x%08x seen=%ld\n",
                   g_post_value_requested_pc[j],
                   g_post_value_requested_sequence_count[j]);
        for (int j = 0; j < g_n_post_value_requested_sequence; j++)
            printf("[oracle] post-target-sequence-row ordinal=%ld pc=0x%08x vi=%ld addr=0x%08x value=0x%08x class=%s\n",
                   g_post_value_requested_sequence[j].ordinal,
                   g_post_value_requested_sequence[j].pc,
                   g_post_value_requested_sequence[j].vi,
                   g_post_value_requested_sequence[j].addr,
                   g_post_value_requested_sequence[j].value,
                   g_post_value_requested_sequence[j].sentinel ? "sentinel" : "non-sentinel");
    }
    for (int watch = 0; watch < g_nwatch; watch++) {
        if (!(g_phase_snapshot_watch_mask & (UINT64_C(1) << watch)))
            continue;
        for (int phase = 0; phase < 2; phase++)
            emit_phase_snapshot(watch, phase);
    }
    if (g_post_value_pc_detail) {
        for (int i = 0; i < g_n_post_value_pc_detail_rows; i++)
            printf("[oracle] post-value-pc-row pc=0x%08x vi=%ld width=%u origin=0x%08x addr=0x%08x value=0x%08x\n",
                   g_post_value_pc_detail_rows[i].pc,
                   g_post_value_pc_detail_rows[i].vi,
                   g_post_value_pc_detail_rows[i].width,
                   g_post_value_pc_detail_rows[i].origin,
                   g_post_value_pc_detail_rows[i].addr,
                   g_post_value_pc_detail_rows[i].value);
        if (g_post_value_pc_detail_overflow)
            printf("[oracle] post-value-pc-detail-overflow n=%ld\n",
                   g_post_value_pc_detail_overflow);
    }
    for (int i = 0; i < g_nwatch; i++)
        printf("[oracle] watch %s [0x%08x,0x%08x): %ld hit(s), %ld read(s), %ld write(s)\n",
               g_watch[i].label, g_watch[i].start, g_watch[i].end,
               g_watch[i].hits, g_watch[i].read_hits, g_watch[i].write_hits);
    for (int phase = 0; phase < g_n_pc_hist_phase; phase++) {
        printf("[oracle] pc-hist-phase origin=0x%08x width=%u vi=%ld\n",
               g_pc_hist_phase_origin[phase], g_pc_hist_phase_width[phase],
               g_pc_hist_phase_vis[phase]);
        for (int watch = 0; watch < g_nwatch; watch++) {
            if (!(g_pc_hist_watch_mask & (UINT64_C(1) << watch)))
                continue;
            printf("[oracle] writer-pc-phase origin=0x%08x width=%u watch=%d range=[0x%08x,0x%08x)\n",
                   g_pc_hist_phase_origin[phase], g_pc_hist_phase_width[phase], watch,
                   g_watch[watch].start, g_watch[watch].end);
            for (int i = 0; i < g_pc_hist_phase[phase][watch].n; i++)
                printf("[oracle] writer-pc-phase origin=0x%08x width=%u watch=%d pc=0x%08x n=%ld\n",
                       g_pc_hist_phase_origin[phase], g_pc_hist_phase_width[phase], watch,
                       g_pc_hist_phase[phase][watch].entries[i].pc,
                       g_pc_hist_phase[phase][watch].entries[i].n);
            if (g_pc_hist_phase[phase][watch].overflow)
                printf("[oracle] writer-pc-phase origin=0x%08x width=%u watch=%d overflow=%ld\n",
                       g_pc_hist_phase_origin[phase], g_pc_hist_phase_width[phase], watch,
                       g_pc_hist_phase[phase][watch].overflow);
        }
    }
    for (int watch = 0; watch < g_nwatch; watch++) {
        if (!(g_pc_hist_watch_mask & (UINT64_C(1) << watch)))
            continue;
        printf("[oracle] writer-pc watch=%d range=[0x%08x,0x%08x)\n",
               watch, g_watch[watch].start, g_watch[watch].end);
        for (int i = 0; i < g_n_writer_pc[watch]; i++)
            printf("[oracle] writer-pc pc=0x%08x n=%ld\n",
                   g_writer_pc[watch][i].pc, g_writer_pc[watch][i].n);
        if (g_writer_pc_overflow[watch])
            printf("[oracle] writer-pc overflow=%ld\n",
                   g_writer_pc_overflow[watch]);
    }
    for (int i = 0; i < g_n_pc_field_dump; i++) {
        struct pc_field_dump_bucket *bucket = &g_pc_field_dump[i];
        printf("[oracle] pc-field-summary pc=0x%08x rows=%d/%d hits=%ld overflow=%ld\n",
               bucket->pc, bucket->n_rows, MAX_PC_FIELD_DUMP_ROWS,
               bucket->hits, bucket->overflow);
        for (int j = 0; j < bucket->n_rows; j++)
            printf("[oracle] pc-field-row pc=0x%08x s0=0x%08x s1=0x%08x "
                   "source_word=0x%08x branch_selector=0x%08x "
                   "source_byte=0x%02x branch_state=0x%04x object=0x%08x "
                   "cursor=0x%08x selected_addr=0x%08x selected_word=0x%08x "
                   "state_18a=0x%04x state_18c=0x%04x n=%ld\n",
                   bucket->pc, bucket->rows[j].s0, bucket->rows[j].s1,
                   bucket->rows[j].source_word,
                   bucket->rows[j].branch_selector,
                   bucket->rows[j].source_byte,
                   bucket->rows[j].branch_state, bucket->rows[j].object,
                   bucket->rows[j].cursor, bucket->rows[j].selected_addr,
                   bucket->rows[j].selected_word, bucket->rows[j].state_18a,
                   bucket->rows[j].state_18c, bucket->rows[j].n);
    }
    if (g_c904_witness_enabled)
        printf("[oracle] c904-witness-summary hits=%ld overflow=%ld\n",
               g_c904_witness_hits, g_c904_witness_overflow);
    if (g_c904_task_join_enabled) {
        printf("[oracle] c904-task-join-summary matched=%ld unmatched=%ld "
               "rows=%d/%d overflow=%ld\n", g_c904_task_join_matched,
               g_c904_task_join_unmatched, g_n_c904_task_join_rows,
               MAX_C904_TASK_JOIN_ROWS, g_c904_task_join_overflow);
        for (int i = 0; i < g_n_c904_task_join_rows; i++) {
            struct c904_task_join_row *row = &g_c904_task_join_rows[i];
            printf("[oracle] c904-task-row pc=0x%08x width=%u origin=0x%08x "
                   "task_ptr=0x%08x data_ptr=0x%08x data_size=0x%08x "
                   "input=0x%08x input_w0=0x%08x input_w1=0x%08x "
                   "selected_addr=0x%08x selected_word=0x%08x payload=",
                   row->pc, row->width, row->origin, row->task_ptr,
                   row->data_ptr, row->data_size, row->input, row->input_w0,
                   row->input_w1, row->selected_addr, row->selected_word);
            for (int payload_i = 0; payload_i < 8; payload_i++)
                printf("%08x%s", row->payload[payload_i], payload_i == 7 ? "" : ",");
            printf(" n=%ld\n", row->n);
        }
    }
    if (g_boundary_join_enabled) {
        printf("[oracle] boundary-join-summary hits=%ld no_task=%ld rows=%d/%d overflow=%ld\n",
               g_boundary_join_hits, g_boundary_join_no_task,
               g_n_boundary_join_rows, MAX_BOUNDARY_JOIN_ROWS,
               g_boundary_join_overflow);
        for (int i = 0; i < g_n_boundary_join_rows; i++) {
            struct boundary_join_row *row = &g_boundary_join_rows[i];
            printf("[oracle] boundary-join-row pc=0x%08x width=%u origin=0x%08x "
                   "task_n=%ld task_ptr=0x%08x data_ptr=0x%08x data_size=0x%08x "
                   "event=%llu object=0x%08x cursor=0x%08x selected_addr=0x%08x "
                   "selected_word=0x%08x branch_state=0x%04x instruction=0x%08x "
                   "source_reg=%u source_value=0x%08x n=%ld\n",
                   row->pc, row->width, row->origin, row->task_n,
                   row->task_ptr, row->data_ptr, row->data_size,
                   (unsigned long long)row->event_ordinal, row->object,
                   row->cursor, row->selected_addr, row->selected_word,
                   row->branch_state, row->instruction, row->source_reg,
                   row->source_value, row->n);
        }
    }
    if (g_n_store_field_dump_pc > 0) {
        printf("[oracle] store-field-summary pcs=%d callbacks=%ld phase_hits=%ld "
               "rows=%d/%d overflow=%ld\n", g_n_store_field_dump_pc,
               g_store_field_dump_candidate_callbacks, g_store_field_dump_hits,
               g_n_store_field_dump_rows, MAX_STORE_FIELD_DUMP_ROWS,
               g_store_field_dump_overflow);
        for (int i = 0; i < g_n_store_field_dump_rows; i++) {
            struct store_field_dump_row *row = &g_store_field_dump_rows[i];
            printf("[oracle] store-field-row watch=%d pc=0x%08x "
                   "store_addr=0x%08x instruction=0x%08x effective_addr=0x%08x "
                   "source_reg=%u source_value=0x%08x scalar_mask=0x%08x "
                   "pre_store_word=0x%08x ra=0x%08x "
                   "a0=0x%08x a1=0x%08x a2=0x%08x t0=0x%08x t1=0x%08x "
                   "s0=0x%08x s1=0x%08x source_word=0x%08x source_byte=0x%02x "
                   "branch_selector=0x%08x branch_state=0x%04x n=%ld\n",
                   row->watch, row->pc, row->store_addr, row->instruction,
                   row->effective_addr, row->source_reg, row->source_value,
                   row->scalar_mask, row->pre_store_word, row->ra, row->a0,
                   row->a1, row->a2, row->t0, row->t1,
                   row->s0, row->s1, row->source_word, row->source_byte,
                   row->branch_selector, row->branch_state, row->n);
        }
    }
    if (g_pc_task_dump_enabled) {
        printf("[oracle] pc-task-summary pc=0x%08x want=%u rows=%d/%d "
               "phase_hits=%ld matched=%ld mismatch=%ld type2=%ld non_type2=%ld "
               "invalid=%ld overflow=%ld\n",
               g_pc_task_dump_pc, g_pc_task_dump_type, g_n_pc_task_dump_rows,
               MAX_PC_TASK_DUMP_ROWS, g_pc_task_dump_phase_hits,
               g_pc_task_dump_type2_rows, g_pc_task_dump_non_type2,
               g_pc_task_dump_type == 2 ? g_pc_task_dump_type2_rows : 0L,
               g_pc_task_dump_type == 2 ? g_pc_task_dump_non_type2 : 0L,
               g_pc_task_dump_invalid, g_pc_task_dump_overflow);
        {
            struct {
                uint32_t type;
                uint32_t task_ptr;
                uint32_t output_buff;
                uint32_t output_buff_size;
                long n;
            } uniq[64];
            int nuniq = 0;
            int ui, ri;
            for (ri = 0; ri < g_n_pc_task_dump_rows; ri++) {
                struct pc_task_dump_row *row = &g_pc_task_dump_rows[ri];
                for (ui = 0; ui < nuniq; ui++) {
                    if (uniq[ui].type == row->type &&
                        uniq[ui].task_ptr == row->task_ptr &&
                        uniq[ui].output_buff == row->output_buff &&
                        uniq[ui].output_buff_size == row->output_buff_size) {
                        uniq[ui].n++;
                        break;
                    }
                }
                if (ui == nuniq) {
                    if (nuniq < 64) {
                        uniq[nuniq].type = row->type;
                        uniq[nuniq].task_ptr = row->task_ptr;
                        uniq[nuniq].output_buff = row->output_buff;
                        uniq[nuniq].output_buff_size = row->output_buff_size;
                        uniq[nuniq].n = 1;
                        nuniq++;
                    }
                }
            }
            printf("[oracle] pc-task-unique n=%d cap=64\n", nuniq);
            for (ui = 0; ui < nuniq; ui++)
                printf("[oracle] pc-task-unique type=0x%x task_ptr=0x%08x "
                       "output_buff=0x%08x output_buff_size=0x%08x n=%ld\n",
                       uniq[ui].type, uniq[ui].task_ptr, uniq[ui].output_buff,
                       uniq[ui].output_buff_size, uniq[ui].n);
            for (ri = 0; ri < g_n_pc_task_dump_rows; ri++) {
                struct pc_task_dump_row *row = &g_pc_task_dump_rows[ri];
                printf("[oracle] pc-task-row n=%ld event=%llu width=%u origin=0x%08x "
                       "type=%u task_ptr=0x%08x data=0x%08x data_size=0x%08x "
                       "output=0x%08x output_size=0x%08x\n",
                       row->task_n, (unsigned long long)row->event_ordinal,
                       row->width, row->origin, row->type, row->task_ptr,
                       row->data_ptr, row->data_size, row->output_buff,
                       row->output_buff_size);
            }
        }
    }
    if (g_pc_range_task_dump_enabled) {
        printf("[oracle] pc-range-task-summary rows=%d/%d hits=%ld invalid=%ld overflow=%ld\n",
               g_n_pc_range_task_rows, MAX_PC_RANGE_TASK_ROWS,
               g_pc_range_task_hits, g_pc_range_task_invalid,
               g_pc_range_task_overflow);
        for (int i = 0; i < g_n_pc_range_task_rows; i++) {
            struct pc_range_task_row *row = &g_pc_range_task_rows[i];
            printf("[oracle] pc-range-task-row pc=0x%08x width=%u origin=0x%08x "
                   "a0=0x%08x a0_word=0x%08x output=0x%08x output_size=0x%08x "
                   "data=0x%08x data_size=0x%08x yield=0x%08x yield_size=0x%08x n=%ld\n",
                   row->pc, row->width, row->origin, row->a0, row->a0_word,
                   row->output_buff, row->output_buff_size, row->data_ptr,
                   row->data_size, row->yield_data_ptr, row->yield_data_size,
                   row->n);
        }
    }
    if (g_ordinal_join_enabled) {
        printf("[oracle] ordinal-join-summary writes=%d/%d overflow=%ld tasks=%d event=%llu\n",
               g_n_ordinal_writes, MAX_ORDINAL_WRITES, g_ordinal_write_overflow,
               g_n_pc_task_dump_rows, (unsigned long long)g_event_ordinal);
        for (int phase = 0; phase < g_n_pc_phase_log_origin; phase++) {
            for (int watch = 0; watch < g_nwatch; watch++) {
                long before = 0, after = 0, equal = 0, no_task = 0;
                long nearest_total = 0;
                for (int wi = 0; wi < g_n_ordinal_writes; wi++) {
                    struct ordinal_write_row *write = &g_ordinal_writes[wi];
                    uint64_t best_distance = UINT64_MAX;
                    struct pc_task_dump_row *best = NULL;
                    if (write->watch != watch ||
                        write->width != g_pc_phase_log[phase].width ||
                        write->origin != g_pc_phase_log[phase].origin)
                        continue;
                    for (int ti = 0; ti < g_n_pc_task_dump_rows; ti++) {
                        struct pc_task_dump_row *task = &g_pc_task_dump_rows[ti];
                        uint64_t distance;
                        if (task->width != write->width || task->origin != write->origin)
                            continue;
                        distance = task->event_ordinal > write->event_ordinal
                            ? task->event_ordinal - write->event_ordinal
                            : write->event_ordinal - task->event_ordinal;
                        if (distance < best_distance) {
                            best_distance = distance;
                            best = task;
                        }
                    }
                    if (!best)
                        no_task++;
                    else if (write->event_ordinal < best->event_ordinal)
                        before++;
                    else if (write->event_ordinal > best->event_ordinal)
                        after++;
                    else
                        equal++;
                    if (best)
                        nearest_total++;
                }
                if (before || after || equal || no_task)
                    printf("[oracle] ordinal-join phase=0x%08x:%u watch=%d "
                           "range=0x%08x..0x%08x nearest=%ld before=%ld after=%ld "
                           "equal=%ld no_task=%ld\n",
                           g_pc_phase_log[phase].origin,
                           g_pc_phase_log[phase].width, watch,
                           g_watch[watch].start, g_watch[watch].end,
                           nearest_total, before, after, equal, no_task);
            }
        }
        {
            static struct ordinal_writer_key keys[MAX_ORDINAL_WRITER_KEYS];
            int key_n = 0;
            long key_overflow = 0;
            memset(keys, 0, sizeof(keys));
            for (int phase = 0; phase < g_n_pc_phase_log_origin; phase++) {
                for (int wi = 0; wi < g_n_ordinal_writes; wi++) {
                    struct ordinal_write_row *write = &g_ordinal_writes[wi];
                    struct pc_task_dump_row *best = NULL;
                    uint64_t best_distance = UINT64_MAX;
                    int key_i;
                    if (write->width != g_pc_phase_log[phase].width ||
                        write->origin != g_pc_phase_log[phase].origin)
                        continue;
                    for (int ti = 0; ti < g_n_pc_task_dump_rows; ti++) {
                        struct pc_task_dump_row *task = &g_pc_task_dump_rows[ti];
                        uint64_t distance;
                        if (task->width != write->width || task->origin != write->origin)
                            continue;
                        distance = task->event_ordinal > write->event_ordinal
                            ? task->event_ordinal - write->event_ordinal
                            : write->event_ordinal - task->event_ordinal;
                        if (distance < best_distance) {
                            best_distance = distance;
                            best = task;
                        }
                    }
                    for (key_i = 0; key_i < key_n; key_i++) {
                        if (keys[key_i].width == write->width &&
                            keys[key_i].origin == write->origin &&
                            keys[key_i].watch == write->watch &&
                            keys[key_i].pc == write->pc &&
                            keys[key_i].effective_addr == write->effective_addr &&
                            keys[key_i].writer_class == ordinal_writer_class(write->pc) &&
                            keys[key_i].value_class == ordinal_value_class(write))
                            break;
                    }
                    if (key_i == key_n) {
                        if (key_n >= MAX_ORDINAL_WRITER_KEYS) {
                            key_overflow++;
                            continue;
                        }
                        keys[key_n].width = write->width;
                        keys[key_n].origin = write->origin;
                        keys[key_n].watch = write->watch;
                        keys[key_n].pc = write->pc;
                        keys[key_n].effective_addr = write->effective_addr;
                        keys[key_n].writer_class = ordinal_writer_class(write->pc);
                        keys[key_n].value_class = ordinal_value_class(write);
                        key_n++;
                    }
                    if (!best) keys[key_i].no_task++;
                    else if (write->event_ordinal < best->event_ordinal) {
                        keys[key_i].before++;
                        keys[key_i].nearest++;
                    } else if (write->event_ordinal > best->event_ordinal) {
                        keys[key_i].after++;
                        keys[key_i].nearest++;
                    } else {
                        keys[key_i].equal++;
                        keys[key_i].nearest++;
                    }
                }
            }
            printf("[oracle] ordinal-writer-join-summary keys=%d/%d overflow=%ld\n",
                   key_n, MAX_ORDINAL_WRITER_KEYS, key_overflow);
            for (int key_i = 0; key_i < key_n; key_i++) {
                struct ordinal_writer_key *key = &keys[key_i];
                printf("[oracle] ordinal-writer-join phase=0x%08x:%u watch=%d "
                       "pc=0x%08x class=%s value_class=%s effective=0x%08x nearest=%ld before=%ld "
                       "after=%ld equal=%ld no_task=%ld\n",
                       key->origin, key->width, key->watch, key->pc,
                       ordinal_writer_class_name(key->writer_class),
                       ordinal_value_class_name(key->value_class),
                       key->effective_addr, key->nearest, key->before,
                       key->after, key->equal, key->no_task);
            }
        }
        {
            static struct span_writer_key keys[MAX_SPAN_WRITER_KEYS];
            int key_n = 0;
            long key_overflow = 0;
            memset(keys, 0, sizeof(keys));
            for (int phase = 0; phase < g_n_pc_phase_log_origin; phase++) {
                for (int wi = 0; wi < g_n_ordinal_writes; wi++) {
                    struct ordinal_write_row *write = &g_ordinal_writes[wi];
                    struct pc_task_dump_row *best = NULL;
                    uint64_t best_distance = UINT64_MAX;
                    int writer_class, value_class, key_i;
                    if (write->width != g_pc_phase_log[phase].width ||
                        write->origin != g_pc_phase_log[phase].origin)
                        continue;
                    for (int ti = 0; ti < g_n_pc_task_dump_rows; ti++) {
                        struct pc_task_dump_row *task = &g_pc_task_dump_rows[ti];
                        uint64_t distance;
                        if (task->width != write->width || task->origin != write->origin)
                            continue;
                        distance = task->event_ordinal > write->event_ordinal
                            ? task->event_ordinal - write->event_ordinal
                            : write->event_ordinal - task->event_ordinal;
                        if (distance < best_distance) {
                            best_distance = distance;
                            best = task;
                        }
                    }
                    writer_class = ordinal_writer_class(write->pc);
                    value_class = ordinal_value_class(write);
                    for (key_i = 0; key_i < key_n; key_i++) {
                        if (keys[key_i].width == write->width &&
                            keys[key_i].origin == write->origin &&
                            keys[key_i].watch == write->watch &&
                            keys[key_i].writer_class == writer_class &&
                            keys[key_i].value_class == value_class)
                            break;
                    }
                    if (key_i == key_n) {
                        if (key_n >= MAX_SPAN_WRITER_KEYS) {
                            key_overflow++;
                            continue;
                        }
                        keys[key_n].width = write->width;
                        keys[key_n].origin = write->origin;
                        keys[key_n].watch = write->watch;
                        keys[key_n].writer_class = writer_class;
                        keys[key_n].value_class = value_class;
                        key_n++;
                    }
                    if (!best) {
                        keys[key_i].no_task++;
                        continue;
                    }
                    keys[key_i].joined++;
                    {
                        uint32_t addr = write->effective_addr & 0x1FFFFFFFu;
                        uint32_t base = best->data_ptr & 0x1FFFFFFFu;
                        uint64_t len = (uint64_t)best->data_size * 0xA10u;
                        uint32_t field = (base + 0x100u) & 0x1FFFFFFFu;
                        if (addr >= field && addr < field + 4u)
                            keys[key_i].in_plus_100++;
                        else if (len && addr >= base && (uint64_t)addr < (uint64_t)base + len)
                            keys[key_i].in_data_span++;
                        else
                            keys[key_i].outside++;
                    }
                }
            }
            printf("[oracle] span-writer-join-summary keys=%d/%d overflow=%ld\n",
                   key_n, MAX_SPAN_WRITER_KEYS, key_overflow);
            for (int key_i = 0; key_i < key_n; key_i++) {
                struct span_writer_key *key = &keys[key_i];
                printf("[oracle] span-writer-join phase=0x%08x:%u watch=%d class=%s "
                       "value_class=%s joined=%ld data_span=%ld plus_100=%ld "
                       "outside=%ld no_task=%ld\n",
                       key->origin, key->width, key->watch,
                       ordinal_writer_class_name(key->writer_class),
                       ordinal_value_class_name(key->value_class), key->joined,
                       key->in_data_span, key->in_plus_100, key->outside,
                       key->no_task);
            }
        }
        memset(g_published_word_stats, 0, sizeof(g_published_word_stats));
        for (int phase = 0; phase < g_n_pc_phase_log_origin; phase++) {
            for (int wi = 0; wi < g_n_ordinal_writes; wi++) {
                struct ordinal_write_row *write = &g_ordinal_writes[wi];
                struct pc_task_dump_row *best = NULL;
                uint64_t best_distance = UINT64_MAX;
                struct published_word_stats *stats;
                uint32_t addr, base;
                uint64_t len;
                int class_id, direction;
                if (write->width != g_pc_phase_log[phase].width ||
                    write->origin != g_pc_phase_log[phase].origin)
                    continue;
                for (int ti = 0; ti < g_n_pc_task_dump_rows; ti++) {
                    struct pc_task_dump_row *task = &g_pc_task_dump_rows[ti];
                    uint64_t distance;
                    if (task->width != write->width || task->origin != write->origin)
                        continue;
                    distance = task->event_ordinal > write->event_ordinal
                        ? task->event_ordinal - write->event_ordinal
                        : write->event_ordinal - task->event_ordinal;
                    if (distance < best_distance) {
                        best_distance = distance;
                        best = task;
                    }
                }
                if (!best) {
                    g_published_word_stats[phase][ordinal_writer_class(write->pc)][3].no_task++;
                    continue;
                }
                if (write->event_ordinal < best->event_ordinal)
                    direction = 0;
                else if (write->event_ordinal > best->event_ordinal)
                    direction = 1;
                else
                    direction = 2;
                class_id = ordinal_writer_class(write->pc);
                stats = &g_published_word_stats[phase][class_id][direction];
                stats->joined++;
                addr = write->effective_addr & 0x1FFFFFFFu;
                base = best->data_ptr & 0x1FFFFFFFu;
                len = (uint64_t)best->data_size * 0xA10u;
                if (!len || addr < base || (uint64_t)addr >= (uint64_t)base + len) {
                    stats->unsupported++;
                    continue;
                }
                stats->in_span++;
                if (!write->scalar_mask) {
                    stats->unsupported++;
                    continue;
                }
                {
                    uint32_t published = 0;
                    int published_i = -1;
                    for (int pi = 0; pi < 4; pi++) {
                        if ((addr & ~3u) == g_published_word_addrs[pi]) {
                            published_i = pi;
                            break;
                        }
                    }
                    if (published_i < 0 || !best->published_valid[published_i]) {
                        stats->unsupported++;
                        continue;
                    }
                    published = best->published_words[published_i];
                    if ((write->source_value & write->scalar_mask) ==
                        (published & write->scalar_mask))
                        stats->source_match++;
                    else
                        stats->source_mismatch++;
                    if (write->post_store_word == published)
                        stats->post_match++;
                    else
                        stats->post_mismatch++;
                }
            }
        }
        for (int phase = 0; phase < g_n_pc_phase_log_origin; phase++) {
            for (int class_id = 1; class_id <= 3; class_id++) {
                for (int direction = 0; direction < 4; direction++) {
                struct published_word_stats *stats = &g_published_word_stats[phase][class_id][direction];
                if (stats->joined || stats->no_task)
                    printf("[oracle] published-word phase=0x%08x:%u class=%s "
                           "direction=%s "
                           "joined=%ld in_span=%ld unsupported=%ld source_match=%ld "
                           "source_mismatch=%ld post_match=%ld post_mismatch=%ld no_task=%ld\n",
                           g_pc_phase_log[phase].origin, g_pc_phase_log[phase].width,
                           ordinal_writer_class_name(class_id),
                           direction == 0 ? "before" : direction == 1 ? "after" :
                           direction == 2 ? "equal" : "no-task",
                           stats->joined,
                           stats->in_span, stats->unsupported, stats->source_match,
                           stats->source_mismatch, stats->post_match,
                           stats->post_mismatch, stats->no_task);
                }
            }
        }
        for (int wi = 0; wi < g_n_ordinal_writes; wi++) {
            struct ordinal_write_row *write = &g_ordinal_writes[wi];
            printf("[oracle] ordinal-write watch=%d pc=0x%08x ordinal=%llu "
                   "width=%u origin=0x%08x store_addr=0x%08x "
                   "instruction=0x%08x effective_addr=0x%08x source_reg=%u "
                   "source_value=0x%08x scalar_mask=0x%08x pre_store_word=0x%08x\n",
                   write->watch, write->pc,
                   (unsigned long long)write->event_ordinal,
                   write->width, write->origin, write->store_addr,
                   write->instruction, write->effective_addr,
                   write->source_reg, write->source_value,
                   write->scalar_mask, write->pre_store_word);
        }
    }
    printf("[oracle] execution watch hits: %ld\n", g_pc_hits);
    for (int i = 0; i < g_n_exec_prev; i++)
        printf("[oracle] exec-prev pc=0x%08x prev=0x%08x n=%ld\n",
               g_exec_prev[i].pc, g_exec_prev[i].prev, g_exec_prev[i].n);
    if (g_exec_prev_overflow)
        printf("[oracle] exec-prev overflow=%ld (unique pairs truncated at %d)\n",
               g_exec_prev_overflow, MAX_EXEC_PREV);
    printf("[oracle] vi-swap-phase rows=%d/%d overflow=%ld pc=0x%08x width=640\n",
           g_n_vi_swap_phase, MAX_VI_SWAP_PHASE_ROWS,
           g_vi_swap_phase_overflow, VI_SWAP_PC);
    for (int i = 0; i < g_n_vi_swap_phase; i++)
        printf("[oracle] vi-swap-phase origin=0x%08x prev_pc=0x%08x a0_phys=0x%08x n=%ld\n",
               g_vi_swap_phase[i].origin, g_vi_swap_phase[i].prev_pc,
               g_vi_swap_phase[i].a0_phys, g_vi_swap_phase[i].n);
    if (g_mode_dump_enabled)
        printf("[oracle] mode-dump-pc=0x%08x width=640 rows=%ld/%d overflow=%ld\n",
               g_mode_dump_pc, g_mode_dump_rows, MAX_MODE_DUMP_ROWS,
               g_mode_dump_overflow);
    if (g_post_swap_table_enabled)
        printf("[oracle] post-swap-summary pc=0x%08x latched=%ld joined=%ld "
               "pending=%d dropped=%ld overflow=%ld rows-cap=%d\n",
               g_post_swap_table_pc, g_post_swap_latched, g_post_swap_joined,
               g_post_swap_pending.valid, g_post_swap_dropped,
               g_post_swap_overflow, MAX_MODE_DUMP_ROWS);
    if (g_vi_context_table_enabled)
        printf("[oracle] vi-context-summary pc=0x%08x latched=%ld joined=%ld "
               "pending=%d dropped=%ld overflow=%ld rows-cap=%d\n",
               g_vi_context_table_pc, g_vi_context_latched,
               g_vi_context_joined, g_vi_context_pending.valid,
               g_vi_context_dropped, g_vi_context_overflow,
               MAX_VI_CONTEXT_ROWS);
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
