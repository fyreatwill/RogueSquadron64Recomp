#!/usr/bin/env python3
"""s7407 class BQ: host replacements of guest math (libm / IDO compiler-runtime) contract.
1. Census: every <name>_recomp in librecomp/src or src/ whose name is math-shaped (libm or __ll_/__ull_/di3/_to_ helpers),
   joined with the ELF (defined? address), guest call sites (jal/j), N64Recomp reimplemented_funcs / ignored_funcs membership,
   and the caller functions. Also lists guest libm symbols (sinf, sqrtf, ...) and whether any is replaced.
2. Sweep: for every replacement that is LIVE (ELF body + reimplemented + >=1 call) the host body is extracted verbatim from
   math_routines.cpp into a harness and run against a C transcription of the retail MIPS body (sw a0-a3 / ld / ddiv(u) /
   dmultu / break 7 / break 6 / dsll32-dsra32 split) over an edge cross product + random pairs with garbage upper register
   halves. Retail break = TRAP row (retail faults; host continues) counted apart from MISMATCH.
3. Positive control: the same harness with -DPERTURB (host result ^ 1) must report mismatches for every live helper.
Usage: tools/s7407_libm_census.py [disasm=/tmp/s7419_canon.dis] [--n N]   rc 0 = H-equal + control PASS, rc 3 otherwise."""
import re, sys, os, glob, subprocess, collections, tempfile
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
DIS = next((a for a in sys.argv[1:] if not a.startswith('--') and not a.isdigit()), '/tmp/s7419_canon.dis')
if DIS == '/tmp/s7419_canon.dis':
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); __import__('s7419_canon_dis').ensure(DIS)
N = int(sys.argv[sys.argv.index('--n') + 1]) if '--n' in sys.argv else 4000000
SYML = os.path.join(ROOT, '../N64Recomp/src/symbol_lists.cpp')
MATHSRC = os.path.join(ROOT, 'lib/N64ModernRuntime/librecomp/src/math_routines.cpp')
MATHNAME = re.compile(r'^(__u?ll_|__\w*di3$|__f_to_|__d_to_|__u?ll_to_|sinf?$|cosf?$|tanf?$|sqrtf?$|atan2?f?$|powf?$|'
                      r'expf?$|logf?$|floorf?$|ceilf?$|fabsf?$|fmodf?$|guSqrtf$|sins$|coss$|__sinf$|__cosf$)')
LIBM = 'sinf cosf sqrtf atan2f atanf tanf powf expf logf floorf ceilf fabsf fmodf sin cos sqrt atan2 guSqrtf sins coss ' \
       '__sinf __cosf guAtan2F'.split()


def lists():
    t = open(SYML).read()
    out = {}
    for nm in ('reimplemented_funcs', 'ignored_funcs', 'renamed_funcs'):
        m = re.search(nm + r'\s*\{(.*?)\n\};', t, re.S)
        out[nm] = set(re.findall(r'"(\w+)"', m.group(1))) if m else set()
    return out


def replacements():
    out = {}
    for f in glob.glob(os.path.join(ROOT, 'lib/N64ModernRuntime/librecomp/src/*.cpp')) + \
            glob.glob(os.path.join(ROOT, 'src/**/*.cpp'), recursive=True):
        for m in re.finditer(r'void\s+(\w+)_recomp\s*\(', open(f, errors='replace').read()):
            out.setdefault(m.group(1), os.path.relpath(f, ROOT))
    return out


def disasm():
    defs, calls, cur = {}, collections.defaultdict(list), None
    for ln in open(DIS, errors='replace'):
        m = re.match(r'^([0-9a-f]{8}) <(\w+)>:', ln)
        if m:
            cur = m.group(2); defs[cur] = m.group(1); continue
        m = re.match(r'^\s*([0-9a-f]+):\s+(jal|j)\s+[0-9a-f]+ <(\w+)(\+0x[0-9a-f]+)?>', ln)
        if m and not m.group(4):
            calls[m.group(3)].append((m.group(1), m.group(2), cur))
    return defs, calls


HARNESS = r'''
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <cstdlib>
typedef uint64_t gpr;
typedef union { double d; struct { float fl; float fh; }; uint32_t u32l; uint64_t u64; } fpr;
typedef struct { gpr r2, r3, r4, r5, r6, r7; fpr f0, f12; } recomp_context;
%(host)s
// retail transcription: sw a0..a3 -> ld 0(sp)/8(sp); result split by dsll32/dsra32 (both halves sign-extended)
enum { OK = 0, TRAP7 = 7, TRAP6 = 6 };
static uint64_t ld_pair(gpr hi, gpr lo) { return ((uint64_t)(uint32_t)hi << 32) | (uint32_t)lo; }
static int retail(int op, gpr a0, gpr a1, gpr a2, gpr a3, gpr *v0, gpr *v1) {
    uint64_t x = ld_pair(a0, a1), y = ld_pair(a2, a3), r;
    switch (op) {
    case 0: if (!y) return TRAP7; r = x / y; break;                          // __ull_div  ddivu mflo
    case 1: if (!y) return TRAP7; r = x %% y; break;                         // __ull_rem  ddivu mfhi
    case 2: if (!y) return TRAP7;                                            // __ll_div   ddiv  mflo
            if (y == ~0ull && x == 0x8000000000000000ull) return TRAP6; r = (uint64_t)((int64_t)x / (int64_t)y); break;
    case 3: r = x * y; break;                                                // __ll_mul   dmultu mflo
    default: return -1;
    }
    *v0 = (gpr)(int64_t)(int32_t)(r >> 32); *v1 = (gpr)(int64_t)(int32_t)r; return OK;
}
typedef void (*hf)(uint8_t *, recomp_context *);
static hf H[4] = { __ull_div_recomp, __ull_rem_recomp, __ll_div_recomp, __ll_mul_recomp };
static const char *NM[4] = { "__ull_div", "__ull_rem", "__ll_div", "__ll_mul" };
static uint64_t s = 0x9E3779B97F4A7C15ull;
static uint64_t rnd() { s ^= s << 13; s ^= s >> 7; s ^= s << 17; return s; }
static uint64_t rmag() { uint64_t v = rnd(); int b = rnd() %% 65; return b == 64 ? v : (v & ((1ull << b) - 1)); }
static long long mis[4], trap[4], n[4];
static void one(int op, uint64_t x, uint64_t y) {
    gpr a0 = (x >> 32) | (rnd() << 32), a1 = (uint32_t)x | (rnd() << 32);   // garbage upper halves: sw drops them
    gpr a2 = (y >> 32) | (rnd() << 32), a3 = (uint32_t)y | (rnd() << 32);
    gpr v0, v1; int t = retail(op, a0, a1, a2, a3, &v0, &v1); n[op]++;
    recomp_context c; memset(&c, 0, sizeof c); c.r4 = a0; c.r5 = a1; c.r6 = a2; c.r7 = a3; H[op](nullptr, &c);
#ifdef PERTURB
    c.r3 ^= 1;
#endif
    if (t) { trap[op]++; if (trap[op] <= 2) printf("TRAP%%d %%s x=%%016llx y=%%016llx host=%%08x%%08x\n", t, NM[op],
        (unsigned long long)x, (unsigned long long)y, (unsigned)c.r2, (unsigned)c.r3); return; }
    if (c.r2 != v0 || c.r3 != v1) { if (++mis[op] <= 3) printf("MISMATCH %%s x=%%016llx y=%%016llx retail=%%016llx:%%016llx "
        "host=%%016llx:%%016llx\n", NM[op], (unsigned long long)x, (unsigned long long)y, (unsigned long long)v0,
        (unsigned long long)v1, (unsigned long long)c.r2, (unsigned long long)c.r3); }
}
int main(int argc, char **argv) {
    long long N = argc > 1 ? atoll(argv[1]) : 1000000;
    static const uint64_t E0[] = { 0, 1, 2, 3, 4, 7, 8, 10, 16, 0x7FFFFFFF, 0x80000000, 0xFFFFFFFF, 0x100000000ull,
        0x7FFFFFFFFFFFFFFFull, 0x8000000000000000ull, 0x8000000000000001ull, ~0ull, ~1ull, 0xFFFFFFFF00000000ull,
        0x00000001FFFFFFFFull, 46875000ull * 3, 62500000ull };
    int ne = sizeof E0 / sizeof E0[0];
    for (int op = 0; op < 4; op++) {
        for (int i = 0; i < ne; i++) for (int j = 0; j < ne; j++) one(op, E0[i], E0[j]);
        for (long long k = 0; k < N; k++) one(op, rmag(), rmag());
        printf("ROW %%s n=%%lld mismatch=%%lld trap=%%lld\n", NM[op], n[op], mis[op], trap[op]);
    }
    return 0;
}
'''


def host_src():
    t = open(MATHSRC).read()
    inl = re.search(r'(static inline uint64_t rs64_udiv64.*?\n\}\n)', t, re.S)
    fn = []
    for m in re.finditer(r'extern "C" void (\w+)_recomp\(uint8_t \* rdram, recomp_context \* ctx\) \{.*?\n\}\n', t, re.S):
        if m.group(1) in ('__ull_div', '__ull_rem', '__ll_div', '__ll_mul'):
            fn.append(m.group(0).replace('extern "C" ', 'static '))
    return inl.group(1) + '\n'.join(fn)


def sweep(perturb):
    d = tempfile.mkdtemp(prefix='s7407_')
    src, exe = os.path.join(d, 'h.cpp'), os.path.join(d, 'h')
    open(src, 'w').write(HARNESS % {'host': host_src()})
    cc = ['clang++', '-std=c++17', '-O2', '-w', src, '-o', exe] + (['-DPERTURB'] if perturb else [])
    subprocess.run(cc, check=True)
    return subprocess.run([exe, str(N)], capture_output=True, text=True, check=True).stdout


def main():
    L, R = lists(), replacements()
    defs, calls = disasm()
    print('== census: math-shaped host replacements')
    print('%-13s %-10s %-5s %-5s %-6s %s' % ('name', 'elf_def', 'reimp', 'ignor', 'calls', 'callers / src'))
    live = []
    for nm in sorted(n for n in R if MATHNAME.match(n)):
        c = calls.get(nm, [])
        st = 'LIVE' if nm in defs and nm in L['reimplemented_funcs'] and c else 'DEAD'
        if st == 'LIVE': live.append(nm)
        print('%-13s %-10s %-5s %-5s %-6d %s %s [%s]' % (nm, defs.get(nm, '-'), int(nm in L['reimplemented_funcs']),
              int(nm in L['ignored_funcs']), len(c), st, ','.join(sorted({x[2] for x in c})) or '-', R[nm]))
    print('== guest libm symbols (recompiled from retail unless replaced)')
    for nm in LIBM:
        if nm in defs:
            print('  %-10s %s calls=%d replaced=%d' % (nm, defs[nm], len(calls.get(nm, [])), int(nm in R)))
    nohost = [n for n in L['reimplemented_funcs'] if MATHNAME.match(n) and n not in R and n in defs and calls.get(n)]
    print('== reimplemented+called but no host body:', nohost or 'none')
    print('== sweep (host body text from math_routines.cpp vs retail MIPS transcription), N=%d per helper' % N)
    out = sweep(False); print(out.rstrip())
    ctl = sweep(True)
    rows = dict((m.group(1), (int(m.group(2)), int(m.group(3)))) for m in
                re.finditer(r'ROW (\w+) n=\d+ mismatch=(\d+) trap=(\d+)', out))
    crow = dict((m.group(1), int(m.group(2))) for m in re.finditer(r'ROW (\w+) n=\d+ mismatch=(\d+)', ctl))
    cpass = len(crow) == 4 and all(v > 0 for v in crow.values())
    print('CONTROL perturbed host (r3^=1): ' + ' '.join('%s=%d' % kv for kv in sorted(crow.items())) +
          (' -> PASS' if cpass else ' -> FAIL'))
    bad = [k for k, (mm, _) in rows.items() if mm]
    uncov = [n for n in live if n not in rows]
    verdict = 'H-diverge ' + ','.join(bad) if bad else ('UNCOVERED ' + ','.join(uncov) if uncov else 'H-equal')
    print('VERDICT live=%s %s (TRAP rows: retail break 7/6 faults, host returns MIPS ddiv values)' % (','.join(live), verdict))
    return 0 if cpass and verdict == 'H-equal' and not nohost else 3


if __name__ == '__main__':
    sys.exit(main())
