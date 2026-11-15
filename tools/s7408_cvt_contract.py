#!/usr/bin/env python3
"""s7408 class BR: recompiler FP->int conversion contract (recomp.h TRUNC_W/L_S/D, CVT_W/L_S/D).
1. Census: count every conversion macro / libm rounding call emitted in ../N64Recomp/RecompiledFuncs, per macro and per
   guest function (CVT_* sites listed with PC + function), and whether the CVT_L_S macro (stray ';') is ever emitted.
2. Sweep: the REAL recomp.h (included, not transcribed) compiled with the game's compiler at -O2; every one of the 2^32
   float bit patterns through TRUNC_W_S and CVT_W_S (host rounding = nearest and = toward-zero, the two guest RMs this
   game uses: libultra FCSR=0x01000800 and guPerspectiveF's ctc1 1), and 2^28 strided + edge doubles through TRUNC_W_D /
   CVT_W_D, vs a VR4300 model: in range -> trunc / round-per-RM; NaN, inf or a rounded value outside int32 -> UNIMPL
   (retail raises the unimplemented-operation exception: the game faults). Rows: EQ (in range, identical), MISM (in
   range, differs: must be 0), UNIMPL split by host value: SAT (int32 saturation / NaN->0), WRAP (low 32 bits of a 64-bit
   result), OTHER.
3. Positive control: -DPERTURB (host result + 1 for |x| in [1000,1001)) must show MISM > 0 for every macro.
Usage: tools/s7408_cvt_contract.py   rc 0 = in-range EQ everywhere + control PASS, rc 3 otherwise."""
import os, re, sys, subprocess, tempfile, collections
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
INC = os.path.join(ROOT, 'lib/N64ModernRuntime/N64Recomp/include')
FUNCS = os.path.join(ROOT, '../N64Recomp/RecompiledFuncs')

C = r'''
#include "recomp.h"
#include <fenv.h>
#include <stdio.h>
#include <string.h>
#ifdef PERTURB
#define PT(x, r) ((fabs((double)(x)) >= 1000.0 && fabs((double)(x)) < 1001.0) ? (r) + 1 : (r))
#else
#define PT(x, r) (r)
#endif
typedef struct { unsigned long long eq, mism, sat, wrap, other, unimpl; long long ex_x; int ex_h, ex_m; } row;
static void cls(row* r, double x, int32_t h, int rmz, int is_cvt) {
    /* VR4300 model */
    double rv = is_cvt ? (rmz ? trunc(x) : nearbyint(x)) : trunc(x);  /* nearbyint under FE_TONEAREST = ties-even */
    int oor = (x != x) || isinf(x) || rv < -2147483648.0 || rv > 2147483647.0;
    if (!oor) { if (h == (int32_t)rv) r->eq++; else { if (!r->mism) { r->ex_m = (int32_t)rv; r->ex_h = h; memcpy(&r->ex_x, &x, 8); } r->mism++; } return; }
    r->unimpl++;
    int32_t sat = (x != x) ? 0 : (rv < 0 ? INT32_MIN : INT32_MAX);
    int32_t wrap = (x != x || isinf(x) || fabs(rv) >= 9.2e18) ? 0x7fffffff : (int32_t)(uint32_t)(uint64_t)(int64_t)rv;
    if (h == sat) r->sat++; else if (h == wrap) r->wrap++; else r->other++;
}
static void pr(const char* n, row* r) {
    double ex; memcpy(&ex, &r->ex_x, 8);
    printf("ROW %s eq=%llu mism=%llu unimpl=%llu sat=%llu wrap=%llu other=%llu ex_x=%.9g ex_host=%d ex_model=%d\n", n, r->eq, r->mism,
        r->unimpl, r->sat, r->wrap, r->other, ex, r->ex_h, r->ex_m);
}
__attribute__((noinline)) static int32_t h_tws(float v) { return PT(v, TRUNC_W_S(v)); }
__attribute__((noinline)) static int32_t h_cws(float v) { return PT(v, CVT_W_S(v)); }
__attribute__((noinline)) static int32_t h_twd(double v) { return PT(v, TRUNC_W_D(v)); }
__attribute__((noinline)) static int32_t h_cwd(double v) { return PT(v, CVT_W_D(v)); }
static void dsweep(row* t, row* c, int rmz) {
    /* doubles: every 2^-? step near the int32 boundaries and ties, plus a 2^28 stride over the bit space */
    static const double edge[] = {2147483647.0, 2147483647.49, 2147483647.5, 2147483647.51, 2147483647.99, 2147483648.0,
        2147483648.5, -2147483648.0, -2147483648.49, -2147483648.5, -2147483648.51, -2147483648.99, -2147483649.0, 0.5, 1.5, 2.5,
        -0.5, -1.5, 4294967296.0, 4294967295.5, 1e10, -1e10, 1e300, -1e300, 9.3e18, -9.3e18, 1000.5, -1000.5};
    for (unsigned i = 0; i < sizeof edge / sizeof edge[0]; i++) for (int s = -4096; s <= 4096; s++) {
        double x = nextafter(edge[i], 0) ; x = edge[i]; for (int k = 0; k < (s < 0 ? -s : s); k++) x = nextafter(x, s < 0 ? -INFINITY : INFINITY);
        cls(t, x, h_twd(x), 1, 0); cls(c, x, h_cwd(x), rmz, 1);
    }
    for (uint64_t u = 0; u < (1ull << 28); u++) {
        uint64_t b = (u << 36) | ((u * 0x9E3779B97F4A7C15ull) >> 28); double x; memcpy(&x, &b, 8);
        cls(t, x, h_twd(x), 1, 0); cls(c, x, h_cwd(x), rmz, 1);
    }
    for (int i = -3000000; i <= 3000000; i++) { double x = i * 0.25 + 1000.0 * (i & 1); cls(t, x, h_twd(x), 1, 0); cls(c, x, h_cwd(x), rmz, 1); }
}
int main(void) {
    for (int rmz = 0; rmz < 2; rmz++) {
        fesetround(rmz ? FE_TOWARDZERO : FE_TONEAREST);
        row tws = {0}, cws = {0}, twd = {0}, cwd = {0};
        uint32_t u = 0;
        do { float x; memcpy(&x, &u, 4); cls(&tws, x, h_tws(x), 1, 0); cls(&cws, x, h_cws(x), rmz, 1); } while (++u != 0);
        dsweep(&twd, &cwd, rmz);
        char n[64];
        if (!rmz) { pr("TRUNC_W_S", &tws); pr("TRUNC_W_D", &twd); }
        snprintf(n, sizeof n, "CVT_W_S/rm%s", rmz ? "Z" : "N"); pr(n, &cws);
        snprintf(n, sizeof n, "CVT_W_D/rm%s", rmz ? "Z" : "N"); pr(n, &cwd);
    }
    fesetround(FE_TONEAREST);
    return 0;
}
'''


def census():
    pc_re = re.compile(r'^\s*// 0x([0-9A-F]{8}):')
    fn_re = re.compile(r'^RECOMP_FUNC void (\w+)\(')
    mac = re.compile(r'\b(CVT_[WL]_[SD]|TRUNC_[WL]_[SD]|ROUND_[WL]_[SD]|FLOOR_[WL]_[SD]|CEIL_[WL]_[SD]|l?lroundf?|do_cvt_\w+)\(')
    tot = collections.Counter(); perfn = collections.defaultdict(collections.Counter); cvt = []
    for name in sorted(os.listdir(FUNCS)):
        if not name.endswith('.c'): continue
        pc = fn = None
        for ln in open(os.path.join(FUNCS, name), errors='replace'):
            m = pc_re.match(ln)
            if m: pc = m.group(1)
            m = fn_re.match(ln)
            if m: fn = m.group(1)
            for mm in mac.finditer(ln):
                k = mm.group(1); tot[k] += 1; perfn[k][fn] += 1
                if k.startswith('CVT_'): cvt.append((k, pc, fn))
    print('CENSUS', ' '.join('%s=%d' % kv for kv in sorted(tot.items())))
    for k in sorted(perfn):
        print('CENSUS-FN %s funcs=%d top=%s' % (k, len(perfn[k]), ','.join('%s:%d' % x for x in perfn[k].most_common(5))))
    for k, pc, fn in cvt: print('CVT-SITE %s pc=0x%s fn=%s' % (k, pc, fn))
    print('CENSUS CVT_L_S emitted=%d (stray-; macro reachable only if >0)' % tot['CVT_L_S'])
    return tot


def sweep(perturb):
    with tempfile.TemporaryDirectory() as d:
        src = os.path.join(d, 'h.c'); exe = os.path.join(d, 'h')
        open(src, 'w').write(C)
        cmd = ['cc', '-O2', '-ffp-contract=off', '-I' + INC, src, '-o', exe, '-lm'] + (['-DPERTURB'] if perturb else [])
        subprocess.run(cmd, check=True)
        return subprocess.run([exe], capture_output=True, text=True, check=True).stdout


def rows(txt):
    out = {}
    for ln in txt.splitlines():
        if ln.startswith('ROW '):
            f = ln.split(); out[f[1]] = dict(kv.split('=', 1) for kv in f[2:])
    return out


def main():
    census()
    base = sweep(False); print(base, end='')
    ctl = rows(sweep(True))
    b = rows(base)
    ok = all(int(r['mism']) == 0 for r in b.values())
    cok = all(int(r['mism']) > 0 for r in ctl.values())
    for k, r in ctl.items(): print('CONTROL %s mism=%s' % (k, r['mism']))
    print('VERDICT in-range %s; control %s' % ('EQ (mism=0 all rows)' if ok else 'MISMATCH', 'PASS' if cok else 'FAIL'))
    return 0 if ok and cok else 3


if __name__ == '__main__':
    sys.exit(main())
