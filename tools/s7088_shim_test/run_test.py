#!/usr/bin/env python3
"""s7088 host test for hand-written shims: compiles the REAL shim text (extracted from lib/) against a
minimal recomp_context and checks it against references transcribed from the ROM / the o32 ABI.

1. osAiSetFrequency arithmetic (ai.cpp s7088-begin..end) vs a step-by-step transcription of the ROM
   function at 0x80029D20 (float div, +0.5, cvt.w.s truncate incl. its overflow fixup, <132 -> -1,
   clock / (s32)dacRate), freq 1..400000 plus edge values. The pre-s7088 integer formula is the
   positive control: it must disagree on >0 inputs.
2. __ull_div/__ull_rem/__ll_div/__ll_mul/__udivdi3 etc. (math_routines.cpp, real text): 64-bit
   join of a0:a1 / a2:a3 (hi first) from sign-extended 32-bit GPRs and split into v0:v1, each
   sign-extended, for operands with bit 31 set in either half. Negative control: a copy with the
   low word unmasked must fail.
3. osSetTimer countdown join and osGetTime split lines (ultra_translation.cpp, real text).
"""
import os, re, subprocess, sys, tempfile
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
L = os.path.join(ROOT, 'lib/N64ModernRuntime/librecomp/src')

def body_of(text, name):
    m = re.search(r'extern "C" void ' + name + r'_recomp\s*\([^)]*\)\s*\{', text)
    i = m.end() - 1; d = 0; j = i
    while True:
        d += {'{': 1, '}': -1}.get(text[j], 0)
        if d == 0: break
        j += 1
    return text[m.start():j + 1]

ai = open(os.path.join(L, 'ai.cpp')).read()
helper = ai[ai.index('// s7088-begin'):ai.index('// s7088-end')]
math = open(os.path.join(L, 'math_routines.cpp')).read()
names = re.findall(r'extern "C" void ([A-Za-z0-9_]+)_recomp', math)
mathsrc = '\n'.join(body_of(math, n) for n in names)
ut = open(os.path.join(L, 'ultra_translation.cpp')).read()
cd_line = re.search(r'uint64_t countdown = [^;]+;', ut).group(0)
gt_body = body_of(ut, 'osGetTime')

def gen(mathtext):
    return r'''
#include <stdint.h>
#include <stdio.h>
#include <string.h>
typedef uint64_t gpr;
typedef union { double d; float fl; uint64_t u64; } fpr; typedef struct { gpr r0,r1,r2,r3,r4,r5,r6,r7; fpr f0,f12,f14; } recomp_context;
static uint64_t g_time;
static uint64_t osGetTime(void){ return g_time; }
#define extern
#define C_ "C"
''' + helper.replace('static inline', 'static') + '\n#undef extern\n' + \
    re.sub(r'extern "C" ', '', mathtext) + '\n' + re.sub(r'extern "C" ', '', gt_body) + r'''
static int32_t rom_aifreq(uint32_t freq, int32_t clock) {
    float f8 = (float)(int32_t)freq, f6 = (float)clock;          /* cvt.s.w x2 */
    if ((int32_t)freq < 0) f8 = f8 + 4294967296.0f;              /* bgez skip, add 2^32 */
    volatile float q = f6 / f8; volatile float f12 = q + 0.5f;   /* div.s, add.s */
    uint32_t a1;
    if (f12 >= 2147483648.0f || f12 != f12) {                     /* cvt.w.s invalid -> fixup path */
        volatile float g = f12 - 2147483648.0f;
        if (g >= 2147483648.0f || g != g) a1 = 0xFFFFFFFFu; else a1 = (uint32_t)(int32_t)g | 0x80000000u;
    } else { a1 = (uint32_t)(int32_t)f12; if ((int32_t)a1 < 0) a1 = 0xFFFFFFFFu; }
    if (a1 < 132u) return -1;
    return clock / (int32_t)a1;
}
static uint32_t old_aifreq(uint32_t freq){ uint32_t d=(48681812u+(freq/2u))/freq; return 48681812u/d; }
#define SX(x) ((gpr)(int64_t)(int32_t)(uint32_t)(x))
static int fails;
#define CK(c, ...) do { if (!(c)) { if (fails++ < 10) printf(__VA_ARGS__); } } while (0)
int main(void) {
    int n = 0, oldd = 0;
    for (uint32_t f = 1; f <= 400000u; f++) {
        if (f >= 368u) { int32_t r = rom_aifreq(f, 48681812); oldd += (r >= 0 && (uint32_t)r != old_aifreq(f)); }
        int32_t a = rs64_ai_set_frequency_retail(f, 48681812u), b = rom_aifreq(f, 48681812); n++;
        CK(a == b, "aifreq %u shim %d rom %d\n", f, a, b);
    }
    printf("aifreq: %d inputs, shim==rom except %d; old integer formula differs on %d (positive control %s)\n",
           n, fails, oldd, oldd > 0 ? "PASS" : "FAIL");
    int af = fails; fails = 0;
    static const uint64_t V[] = {0,1,2,3,7,10,0x7FFFFFFFull,0x80000000ull,0xFFFFFFFFull,0x100000000ull,
        0x80000000FFFFFFFFull,0xFFFFFFFF80000000ull,0x123456789ABCDEF0ull,0xFEDCBA9876543210ull,
        0x7FFFFFFFFFFFFFFFull,0x8000000000000000ull,0xFFFFFFFFFFFFFFFFull,0x00000001DEADBEEFull};
    int nv = sizeof V / sizeof V[0], cases = 0;
    for (int i = 0; i < nv; i++) for (int j = 0; j < nv; j++) {
        uint64_t a = V[i], b = V[j]; recomp_context c;
#define LOAD() memset(&c,0,sizeof c); c.r4=SX(a>>32); c.r5=SX(a); c.r6=SX(b>>32); c.r7=SX(b)
#define OUT(exp, nm) do { uint64_t e=(exp); cases++; CK(c.r2==SX(e>>32)&&c.r3==SX(e), nm " a=%llx b=%llx got %llx:%llx\n", \
        (unsigned long long)a,(unsigned long long)b,(unsigned long long)c.r2,(unsigned long long)c.r3); } while(0)
        LOAD(); __ll_mul_recomp(0,&c); OUT(a*b, "__ll_mul");
        if (b) { LOAD(); __ull_div_recomp(0,&c); OUT(a/b, "__ull_div");
                 LOAD(); __ull_rem_recomp(0,&c); OUT(a%b, "__ull_rem");
                 if (!((int64_t)a==INT64_MIN && (int64_t)b==-1)) { LOAD(); __ll_div_recomp(0,&c); OUT((uint64_t)((int64_t)a/(int64_t)b), "__ll_div"); } }
        /* osSetTimer countdown join (real line) */
        { gpr r6=SX(a>>32), r7=SX(a); struct { gpr r6,r7; } ctx_s={r6,r7}, *ctx=&ctx_s; ''' + cd_line + r''' cases++;
          CK(countdown==a, "countdown a=%llx got %llx\n",(unsigned long long)a,(unsigned long long)countdown); }
        /* osGetTime split (real body) */
        g_time = a; memset(&c,0,sizeof c); osGetTime_recomp(0,&c); cases++;
        CK(c.r2==SX(a>>32)&&c.r3==SX(a), "osGetTime %llx\n",(unsigned long long)a);
    }
    printf("64-bit shapes: %d cases, %d mismatches\n", cases, fails);
    return (af || fails || !oldd) ? 1 : 0;
}
'''

def build_run(src, tag):
    d = tempfile.mkdtemp(prefix='s7088_')
    c = os.path.join(d, 't.c'); open(c, 'w').write(src)
    exe = os.path.join(d, 't')
    subprocess.check_call(['cc', '-O2', '-w', '-ffp-contract=off', c, '-o', exe])
    r = subprocess.run([exe], capture_output=True, text=True)
    print(f'--- {tag}\n{r.stdout.strip()}\nrc={r.returncode}')
    return r.returncode

rc = build_run(gen(mathsrc), 'real shim text')
neg = mathsrc.replace('((ctx->r5 << 0) & 0xFFFFFFFFu)', '(ctx->r5 << 0)')
assert neg != mathsrc
nrc = build_run(gen(neg), 'negative control: a1 low-word masks removed')
print('RESULT', 'PASS' if rc == 0 and nrc != 0 else 'FAIL')
sys.exit(0 if rc == 0 and nrc != 0 else 1)
