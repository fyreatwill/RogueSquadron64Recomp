#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-rsp-cxd4/vu/vu.h"

u32 inst_word;
void message(const char *body) { (void)body; }

#include "/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-rsp-cxd4/vu/vu.c"
#include "/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-rsp-cxd4/vu/add.c"
#include "/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-rsp-cxd4/vu/divide.c"
#include "/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-rsp-cxd4/vu/logical.c"
#include "/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-rsp-cxd4/vu/multiply.c"
#include "/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-rsp-cxd4/vu/select.c"

static void put_acc(const uint16_t *h, const uint16_t *m, const uint16_t *l) {
    for (int i = 0; i < 8; ++i) {
        VACC_H[i] = (int16_t)h[i];
        VACC_M[i] = (int16_t)m[i];
        VACC_L[i] = (int16_t)l[i];
    }
}

static int run_op(const char *name, const uint16_t *vs, const uint16_t *vt,
                  uint16_t *out) {
    i16 a[8], b[8];
    for (int i = 0; i < 8; ++i) { a[i] = (i16)vs[i]; b[i] = (i16)vt[i]; }
#define OP_VOID(n) if (strcmp(name, #n) == 0) { n(a, b); goto done; }
    OP_VOID(VMULF) OP_VOID(VMACF) OP_VOID(VMUDL) OP_VOID(VMUDM) OP_VOID(VMUDN) OP_VOID(VMUDH)
    OP_VOID(VMADL) OP_VOID(VMADM) OP_VOID(VMADN) OP_VOID(VMADH)
#undef OP
#undef OP_VOID
    return 0;
done:
    for (int i = 0; i < 8; ++i) out[i] = (uint16_t)V_result[i];
    return 1;
}

int main(void) {
    char line[4096];
    unsigned long rows = 0, fd57 = 0, compared = 0, mismatch = 0, malformed = 0;
    uint16_t next_h[8], next_m[8], next_l[8];
    int have_prev = 0;
    while (fgets(line, sizeof line, stdin)) {
        char name[16], fields[9][256];
        int vd;
        int n = sscanf(line,
            "[spike-vu8] %15s vd=v%d vs=%255s vte=%255s H=%255s M=%255s L=%255s pvd=%255s post=%255s",
            name, &vd, fields[0], fields[1], fields[2], fields[3], fields[4], fields[5], fields[6]);
        if (n != 9) continue;
        uint16_t vs[8], vt[8], h[8], m[8], l[8], post[8], out[8];
        char *all[] = { fields[0], fields[1], fields[2], fields[3], fields[4], fields[5], fields[6] };
        for (int f = 0; f < 7; ++f) {
            char *p = all[f];
            for (int i = 0; i < 8; ++i) {
                char *end = NULL;
                unsigned long x = strtoul(p, &end, 16);
                if (end == p || x > 0xFFFF) { ++malformed; goto next_line; }
                ((uint16_t *[7]){vs, vt, h, m, l, out, post})[f][i] = (uint16_t)x;
                p = end;
                if (i != 7) { if (*p != ',') { ++malformed; goto next_line; } ++p; }
            }
        }
        put_acc(h, m, l);
        if (have_prev) {
            for (int i = 0; i < 8; ++i) {
                if (h[i] == next_h[i] && m[i] == next_m[i] && l[i] == next_l[i]) ++compared;
                else { ++mismatch; if (mismatch < 8) fprintf(stderr, "acc mismatch row=%lu lane=%d got=%04X.%04X.%04X log=%04X.%04X.%04X\n", rows + 1, i, next_h[i], next_m[i], next_l[i], h[i], m[i], l[i]); }
            }
        }
        put_acc(h, m, l);
        if (!run_op(name, vs, vt, out)) continue;
        ++rows;
        for (int i = 0; i < 8; ++i) { next_h[i] = (uint16_t)VACC_H[i]; next_m[i] = (uint16_t)VACC_M[i]; next_l[i] = (uint16_t)VACC_L[i]; if (out[i] == 0xFD57) { ++fd57; fprintf(stderr, "cxd4 fd57 row=%lu lane=%d op=%s result=%04X\n", rows, i, name, out[i]); } }
        have_prev = 1;
next_line:;
    }
    printf("rows=%lu accCompared=%lu accMismatches=%lu fd57=%lu malformed=%lu\n", rows, compared, mismatch, fd57, malformed);
    return rows && fd57 && compared ? 0 : 1;
}
