#!/usr/bin/env python3
"""s4916: add --slot-peek-pc A to tools/oracle/rs64_oracle.c (idempotent).
At each phase-gated exec of A, samples arbiter slot bytes 0x80128EA8..B7 and flag bytes
0x8011A8C8/9; prints the first 48 raw rows and a unique-row histogram at shutdown."""
import sys

p = sys.argv[1] if len(sys.argv) > 1 else 'tools/oracle/rs64_oracle.c'
t = open(p).read()
if 'slot_peek' in t:
    sys.exit(0)
code = r'''
/* s4916: --slot-peek-pc A (see tools/apply_s4916_slot_peek.py) */
#define SLOT_PEEK_ROWS 64
static uint32_t g_slot_peek_pc;
static int g_slot_peek_n;
static unsigned char g_slot_peek_row[SLOT_PEEK_ROWS][18];
static long g_slot_peek_cnt[SLOT_PEEK_ROWS];
static long g_slot_peek_hits, g_slot_peek_overflow;
static void slot_peek(uint32_t pc)
{
    unsigned char r[18];
    int i;
    if (!g_slot_peek_pc || pc != g_slot_peek_pc)
        return;
    if (!pc_phase_log_match())
        return;
    for (i = 0; i < 16; i++)
        r[i] = (unsigned char)debug_mem_u8(0x80128EA8u + i);
    r[16] = (unsigned char)debug_mem_u8(0x8011A8C8u);
    r[17] = (unsigned char)debug_mem_u8(0x8011A8C9u);
    if (g_slot_peek_hits < 48) {
        printf("[slot-peek] #%ld ", g_slot_peek_hits);
        for (i = 0; i < 18; i++) printf("%02x ", r[i]);
        printf("\n");
    }
    g_slot_peek_hits++;
    for (i = 8; i < 16; i++) r[i] = 0; /* bytes 8..15 are timestamps/pointers in retail: mask for the histogram */
    for (i = 0; i < g_slot_peek_n; i++)
        if (!memcmp(g_slot_peek_row[i], r, 18)) { g_slot_peek_cnt[i]++; return; }
    if (g_slot_peek_n >= SLOT_PEEK_ROWS) { g_slot_peek_overflow++; return; }
    memcpy(g_slot_peek_row[g_slot_peek_n], r, 18);
    g_slot_peek_cnt[g_slot_peek_n++] = 1;
}
'''
def rep(a, b):
    global t
    assert a in t, a
    t = t.replace(a, b, 1)

rep('static void dump_pc_field(uint32_t pc)\n{', code + '\nstatic void dump_pc_field(uint32_t pc)\n{')
rep('        dump_pc_field(pc);\n', '        dump_pc_field(pc);\n    if (flags & M64P_BKP_FLAG_EXEC)\n        slot_peek(pc);\n')
rep('        else if (!strcmp(argv[i], "--pc-field-dump-any-phase"))',
    '''        else if (!strcmp(argv[i], "--slot-peek-pc") && i + 1 < argc) {
            unsigned int spc = 0;
            sscanf(argv[++i], "%x", &spc);
            g_slot_peek_pc = spc;
        }
        else if (!strcmp(argv[i], "--pc-field-dump-any-phase"))''')
rep('    for (int i = 0; i < g_n_pc_field_dump; i++) {\n        struct pc_field_dump_bucket *bucket',
    r'''    if (g_slot_peek_pc) {
        printf("[oracle] slot-peek-summary pc=0x%08x hits=%ld unique=%d overflow=%ld\n",
               g_slot_peek_pc, g_slot_peek_hits, g_slot_peek_n, g_slot_peek_overflow);
        for (int j = 0; j < g_slot_peek_n; j++) {
            printf("[oracle] slot-peek-row n=%ld ", g_slot_peek_cnt[j]);
            for (int k = 0; k < 18; k++) printf("%02x ", g_slot_peek_row[j][k]);
            printf("\n");
        }
    }
    for (int i = 0; i < g_n_pc_field_dump; i++) {
        struct pc_field_dump_bucket *bucket''')
open(p, 'w').write(t)
