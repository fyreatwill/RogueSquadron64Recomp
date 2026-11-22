#!/usr/bin/env python3
"""s7415 class BY: FP arithmetic + FP move emission semantics.
N64Recomp lowers add/sub/mul/div.{s,d} to `ctx->fD.fl = ctx->fS.fl + ctx->fT.fl;` / MUL_S / DIV_S (recomp.h: plain C * /),
neg/abs/sqrt to `-x` / fabsf / sqrtf, mov to a float copy, mfc1 to `(int32_t)u32l`, mtc1 to `u32l = rT`, each preceded by
CHECK_FR and (arith/neg/abs/sqrt) NAN_CHECK(input) = assert(val == val).
1. Harvest every site in ../N64Recomp/RecompiledFuncs; statement + NAN_CHECK operand list checked against the disasm.
2. Each distinct statement compiled verbatim (game flags: -O2 -g -std=gnu17 -fno-strict-aliasing, -DRS64_BYTE_WATCH,
   force header) and driven with all-pairs special values + random/near-cancel/tiny/huge pairs, vs an exact-rational
   IEEE-754 RNE model (fractions.Fraction, written here, no host FP). Two host arms: FPCR.FZ=0 and FZ=1 (ARM flush:
   subnormal inputs of arith ops -> signed 0, tiny-before-rounding results -> signed 0). Stray-write check on the whole ctx.
   NaN results: class `nan` (bit payload differences counted apart; the VR4300 raises on NaN operands, see 4).
3. Positive control: mutants (add->sub, div via reciprocal, neg as 0-x, abs via compare, sqrt*(1+ulp), mfc1 zero-extend,
   mtc1 64-bit write, mov via double, add.d through float) must flag; neutral rewrites (mul.s via double) must not.
4. Object census of the real build: fused multiply-add instructions (fp contraction) and ___assert_rtn calls (NAN_CHECK /
   CHECK_FR live in this Debug build); runtime NAN_CHECK fires across scratch/agent/soak_results.
Usage: tools/s7415_fp_arith.py [K]   rc 0 = H-equal + CONTROL PASS, rc 3 otherwise."""
import os, re, sys, subprocess, tempfile, collections, random, struct, glob
from fractions import Fraction as Fr
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
INC = os.path.join(ROOT, 'lib/N64ModernRuntime/N64Recomp/include')
FORCE = os.path.join(ROOT, 'include/rsp_dpc_macros.h')
FUNCS = os.path.join(ROOT, '../N64Recomp/RecompiledFuncs')
GPR = 'zero at v0 v1 a0 a1 a2 a3 t0 t1 t2 t3 t4 t5 t6 t7 s0 s1 s2 s3 s4 s5 s6 s7 t8 t9 k0 k1 gp sp fp ra'.split()
GN = {n: i for i, n in enumerate(GPR)}; GN['s8'] = 30
BIN = {'add': '{0} + {1}', 'sub': '{0} - {1}', 'mul': 'MUL_{F}({0}, {1})', 'div': 'DIV_{F}({0}, {1})'}
UN = {'neg': '-{0}', 'abs': 'fabs{f}({0})', 'sqrt': 'sqrt{f}({0})', 'mov': '{0}'}
OPS = set(['%s.%s' % (o, t) for o in list(BIN) + list(UN) for t in 'sd'] + ['mfc1', 'mtc1', 'dmfc1', 'dmtc1'])
KINDS = sorted(OPS - {'dmfc1', 'dmtc1'})
cpat = re.compile(r'^\s*// 0x([0-9A-F]{8}): (\S+)(?:\s+(.*?))?\s*$')
midpat = re.compile(r'\S\s*// 0x([0-9A-F]{8}): (\S+)')

def expect(op, args):
    fr = [int(x) for x in re.findall(r'\$f(\d+)', args)]
    if op in ('mfc1', 'mtc1'):
        g = re.findall(r'\$(\w+)', args); rt = GN.get(g[0]); fs = fr[0]
        fv = 'ctx->f_odd[(%d - 1) * 2]' % fs if fs & 1 else 'ctx->f%d.u32l' % fs   # odd FPR: FR=0 high word via f_odd (class BS)
        if op == 'mfc1': return ['ctx->r%d = (int32_t)%s;' % (rt, fv)] if rt else None, []
        return ['%s = %s;' % (fv, 'ctx->r%d' % rt if rt else '0')], []
    o, t = op.split('.'); fld = 'fl' if t == 's' else 'd'; R = lambda i: 'ctx->f%d.%s' % (i, fld)
    if o in BIN:
        return ['%s = %s;' % (R(fr[0]), BIN[o].format(R(fr[1]), R(fr[2]), F=t.upper()))], [R(fr[1]), R(fr[2])]
    nc = [] if o == 'mov' else [R(fr[1])]
    return ['%s = %s;' % (R(fr[0]), UN[o].format(R(fr[1]), f='f' if t == 's' else ''))], nc

GENLINES = set()
def harvest():
    obs = collections.Counter(); sites = collections.Counter(); forms = collections.Counter(); bad = []; patch = []; mid = collections.Counter()
    for f in sorted(os.listdir(FUNCS)):
        if not f.endswith('.c'): continue
        L = open(os.path.join(FUNCS, f), errors='replace').read().split('\n')
        for i, line in enumerate(L):
            for mm in midpat.finditer(line):
                if mm.group(2) in OPS and not line.lstrip().startswith('//'): mid[mm.group(2)] += 1
            m = cpat.match(line)
            if not m or m.group(2) not in OPS: continue
            op, args = m.group(2), m.group(3) or ''; sites[op] += 1
            want, wnc = expect(op, args); nc = []; st = None
            for j in range(i + 1, min(i + 10, len(L))):
                l = re.sub(r'/\*.*?\*/', '', L[j]).strip()
                if cpat.match(L[j]): break
                while True:
                    mn = re.match(r'NAN_CHECK\((ctx->f\d+\.(?:fl|d))\);\s*', l)
                    if not mn: break
                    nc.append(mn.group(1)); l = l[mn.end():]
                if l.startswith('rs64_s2179_vec3_word(') or (l.startswith('U32(ctx->f') and 'PATCH: s2181' in L[j]):
                    obs[op] += 1; continue   # s2181 pass-through logger: reads fS/fT u32l by value
                if not l or re.match(r'^L_[0-9A-F]{8}:$', l) or re.match(r'CHECK_FR\(ctx, \d+\);$', l) \
                        or l.startswith('g_rs64_last_guest_pc = '): continue
                st = l; raw = L[j]; break
            if want is None:   # mfc1 to $zero: nothing architectural
                if st and re.match(r'ctx->r0 = ', st): bad.append((f, m.group(1), op, args, st))
                continue
            if st in want and nc == wnc: forms[(op, st)] += 1; GENLINES.add((f, j + 1)); continue
            if st and 'PATCH' in raw and nc == wnc: patch.append((f, m.group(1), op, args, raw.strip())); continue
            bad.append((f, m.group(1), op, args, '%s | nc=%s want %s' % (st, nc, wnc)))
    harvest.obs = obs
    return sites, forms, bad, patch, mid

# ---------------- exact IEEE model ----------------
FMT = {'s': (24, -126, 127, 8, 32), 'd': (53, -1022, 1023, 11, 64)}
def dec(bits, t):
    p, emin, emax, eb, w = FMT[t]; s = bits >> (w - 1); e = (bits >> (p - 1)) & ((1 << eb) - 1); m = bits & ((1 << (p - 1)) - 1)
    if e == (1 << eb) - 1: return ('nan', s, None) if m else ('inf', s, None)
    v = Fr(m, 1) * Fr(2) ** (emin - p + 1) if e == 0 else Fr(m + (1 << (p - 1))) * Fr(2) ** (e - emax - p + 1)
    return ('num', s, v)
def ilog2(m):
    E = m.numerator.bit_length() - m.denominator.bit_length()
    while Fr(2) ** E > m: E -= 1
    while Fr(2) ** (E + 1) <= m: E += 1
    return E
def enc_parts(s, n, e, t):   # n integer significand at scale 2^(e-p+1)
    p, emin, emax, eb, w = FMT[t]
    if n == 1 << p: n >>= 1; e += 1
    if e > emax: return (s << (w - 1)) | (((1 << eb) - 1) << (p - 1))
    if n < 1 << (p - 1): return (s << (w - 1)) | n
    return (s << (w - 1)) | ((e + emax) << (p - 1)) | (n - (1 << (p - 1)))
def rnd(s, m, t, fz):
    p, emin, emax, eb, w = FMT[t]
    if m == 0: return s << (w - 1)
    E = ilog2(m)
    if fz and E < emin: return s << (w - 1)
    e = max(E, emin); q = m / Fr(2) ** (e - p + 1); n = q.numerator // q.denominator; r = q - n
    if r > Fr(1, 2) or (r == Fr(1, 2) and n & 1): n += 1
    return enc_parts(s, n, e, t)
def rsqrt(m, t):
    p, emin, emax, eb, w = FMT[t]
    E = ilog2(m) // 2; R = m / Fr(2) ** (2 * (E - p + 1))
    from math import isqrt
    n = isqrt(R.numerator // R.denominator)
    if R > (Fr(n) + Fr(1, 2)) ** 2: n += 1
    return enc_parts(0, n, E, t)
NANB = {'s': 0x7FBFFFFF, 'd': 0x7FF7FFFFFFFFFFFF}   # MIPS default NaN (sentinel; only the NaN class is scored)
def ftz_in(x, t):
    p, emin, emax, eb, w = FMT[t]
    return x & (1 << (w - 1)) if x & (((1 << eb) - 1) << (p - 1)) == 0 else x
def model(op, a, b, fz):
    if op == 'mfc1': a &= 0xFFFFFFFF; return a | (0xFFFFFFFF00000000 if a >> 31 else 0)
    if op == 'mtc1': return a & 0xFFFFFFFF
    o, t = op.split('.'); p, emin, emax, eb, w = FMT[t]; S = 1 << (w - 1)
    if o == 'mov': return a
    if o == 'neg': return a ^ S if dec(a, t)[0] != 'nan' else NANB[t]
    if o == 'abs': return a & (S - 1) if dec(a, t)[0] != 'nan' else NANB[t]
    if fz: a = ftz_in(a, t); b = ftz_in(b, t)
    ka, sa, va = dec(a, t); kb, sb, vb = dec(b, t); INF = lambda s: (s << (w - 1)) | (((1 << eb) - 1) << (p - 1))
    if o == 'sqrt':
        if ka == 'nan': return NANB[t]
        if ka == 'num' and va == 0: return a
        if sa: return NANB[t]
        return a if ka == 'inf' else rsqrt(va, t)
    if ka == 'nan' or kb == 'nan': return NANB[t]
    if o == 'sub': o = 'add'; sb ^= 1
    if o == 'add':
        if ka == 'inf' and kb == 'inf': return INF(sa) if sa == sb else NANB[t]
        if ka == 'inf': return INF(sa)
        if kb == 'inf': return INF(sb)
        x = (-va if sa else va) + (-vb if sb else vb)
        if x == 0: return S if (va == 0 and vb == 0 and sa and sb) else 0
        return rnd(1 if x < 0 else 0, abs(x), t, fz)
    s = sa ^ sb
    if o == 'mul':
        if (ka == 'inf' and kb == 'num' and vb == 0) or (kb == 'inf' and ka == 'num' and va == 0): return NANB[t]
        if 'inf' in (ka, kb): return INF(s)
        return rnd(s, va * vb, t, fz)
    if o == 'div':
        if ka == 'inf' and kb == 'inf': return NANB[t]
        if ka == 'num' and kb == 'num' and va == 0 and vb == 0: return NANB[t]
        if ka == 'inf': return INF(s)
        if kb == 'inf': return s << (w - 1)
        if vb == 0: return INF(s)
        return rnd(s, va / vb, t, fz)

SV = {'s': [0, 0x80000000, 1, 0x80000001, 0x007FFFFF, 0x00800000, 0x00800001, 0x3F800000, 0xBF800000, 0x3F800001, 0x3F7FFFFF,
            0x40000000, 0x7F7FFFFF, 0xFF7FFFFF, 0x7F800000, 0xFF800000, 0x7FC00000, 0x7F800001, 0x7FBFFFFF, 0xFFC00001,
            0x1F800000, 0x5F800000, 0x00400000, 0x34000000],
      'd': [0, 1 << 63, 1, (1 << 63) | 1, 0x000FFFFFFFFFFFFF, 0x0010000000000000, 0x0010000000000001, 0x3FF0000000000000,
            0xBFF0000000000000, 0x3FF0000000000001, 0x3FEFFFFFFFFFFFFF, 0x4000000000000000, 0x7FEFFFFFFFFFFFFF,
            0xFFEFFFFFFFFFFFFF, 0x7FF0000000000000, 0xFFF0000000000000, 0x7FF8000000000000, 0x7FF0000000000001,
            0x7FF7FFFFFFFFFFFF, 0xFFF8000000000001, 0x1FF0000000000000, 0x5FF0000000000000, 0x0008000000000000,
            0x3CB0000000000000]}
def vectors(kind, K, R):
    if kind in ('mfc1', 'mtc1'):
        base = [0, 1, 0x7FFFFFFF, 0x80000000, 0xFFFFFFFF, 0xFFFFFFFF00000000, 0x123456789ABCDEF0, 0x00000000FFFFFFFF]
        return [(a, 0) for a in base + [R.getrandbits(64) for _ in range(K)]]
    o, t = kind.split('.'); w = FMT[t][4]; sv = SV[t]; M = (1 << w) - 1
    if o in UN: return [(a, 0) for a in sv + [R.getrandbits(w) for _ in range(K)] + [R.getrandbits(w) & (M >> 2) for _ in range(K // 4)]]
    out = [(a, b) for a in sv for b in sv]
    for k in range(K):
        a = R.getrandbits(w); c = k % 5
        if c == 0: b = R.getrandbits(w)
        elif c == 1: b = (a ^ (1 << (w - 1))) + R.randint(-3, 3) & M        # near-cancellation
        elif c == 2: b = a + R.randint(-3, 3) & M
        elif c == 3: a &= M >> 3; b = R.getrandbits(w) & (M >> 3)            # tiny: subnormal results
        else: b = R.getrandbits(w - 2) | (R.getrandbits(2) << (w - 2))
        out.append((a, b))
    return out

C_HEAD = r'''
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "recomp.h"
uint32_t rs64_ram_top = 0x80800000u;
typedef void (*tfn)(recomp_context*);
typedef struct { tfn f; int kind, d, s, t, ctl; const char* name; } T;
'''
C_MAIN = r'''
static uint64_t sd = 0x9E3779B97F4A7C15ull;
static uint64_t xr(void) { sd ^= sd << 13; sd ^= sd >> 7; sd ^= sd << 17; return sd; }
static void setfz(int on) {
    uint64_t r; __asm__ volatile("mrs %0, fpcr" : "=r"(r)); r = on ? (r | (1ull << 24)) : (r & ~(1ull << 24));
    __asm__ volatile("msr fpcr, %0" :: "r"(r));
}
static int isnan_b(uint64_t v, int dbl) { return dbl ? ((v & 0x7FF0000000000000ull) == 0x7FF0000000000000ull && (v & 0xFFFFFFFFFFFFFull))
                                                 : ((v & 0x7F800000u) == 0x7F800000u && (v & 0x7FFFFFu)); }
static fpr* Fp(recomp_context* c, int i) { return &c->f0 + i; }
static uint32_t* W(recomp_context* c, int i) { return (i & 1) ? &Fp(c, i - 1)->u32h : &Fp(c, i)->u32l; }   /* FR=0 32-bit view */
int main(int argc, char** argv) {
    int fz = atoi(argv[2]); FILE* fp = fopen(argv[1], "rb"); uint32_t nk; fread(&nk, 4, 1, fp);
    uint32_t cnt[64]; uint64_t* V[64];
    for (uint32_t k = 0; k < nk; k++) { fread(&cnt[k], 4, 1, fp); V[k] = malloc(cnt[k] * 48ull); fread(V[k], 48, cnt[k], fp); }
    setfz(fz);
    for (int ti = 0; ti < NT; ti++) {
        const T* t = &TAB[ti]; int K = t->kind; int dbl = KDBL[K], cls = KCLS[K];  /* cls 0 arith,1 bitwise-fp,2 mfc1,3 mtc1 */
        long n = 0, mism = 0, nanp = 0, stray = 0, nanok = 0; char ex[200] = "";
        for (uint32_t v = 0; v < cnt[K]; v++) {
            uint64_t* r = V[K] + v * 6; uint64_t a = r[0], b = r[1];
            recomp_context c; memset(&c, 0, sizeof c);
            for (int i = 0; i < 32; i++) { Fp(&c, i)->u64 = xr(); (&c.r0)[i] = xr(); }
            c.r0 = 0; c.f_odd = &c.f0.u32h; c.mips3_float_mode = 0;
            if (cls == 2) *W(&c, t->s) = (uint32_t)a;
            else if (cls == 3) { if (t->s) (&c.r0)[t->s] = a; }
            else if (dbl) { Fp(&c, t->s)->u64 = a; if (t->t >= 0) Fp(&c, t->t)->u64 = b; }
            else { Fp(&c, t->s)->u32l = (uint32_t)a; if (t->t >= 0) Fp(&c, t->t)->u32l = (uint32_t)b; }
            int bb = t->t >= 0 && t->t == t->s;
            uint64_t want = r[2 + (fz ? 2 : 0) + bb]; if (cls == 3 && t->s == 0) want = 0;   /* mtc1 $zero */
            recomp_context c0 = c; t->f(&c);
            uint64_t got; recomp_context c1 = c;
            if (cls == 2) { got = (&c.r0)[t->d]; (&c1.r0)[t->d] = (&c0.r0)[t->d]; }
            else if (cls == 3) { got = *W(&c, t->d); *W(&c1, t->d) = *W(&c0, t->d); }
            else if (dbl) { got = Fp(&c, t->d)->u64; Fp(&c1, t->d)->u64 = Fp(&c0, t->d)->u64; }
            else { got = Fp(&c, t->d)->u32l; Fp(&c1, t->d)->u32l = Fp(&c0, t->d)->u32l; }
            n++;
            if (memcmp(&c0, &c1, sizeof c0)) { stray++; continue; }
            if (got == want) continue;
            if (cls != 2 && cls != 3 && KSTRICT[K] == 0 && isnan_b(want, dbl) && isnan_b(got, dbl)) { nanp++; continue; }
            mism++; if (!ex[0]) snprintf(ex, sizeof ex, "a=%llx b=%llx want=%llx got=%llx", (unsigned long long)a, (unsigned long long)b,
                                         (unsigned long long)want, (unsigned long long)got);
        }
        printf("%d|%d|%ld|%ld|%ld|%ld|%s\n", ti, t->ctl, n, mism, nanp, stray, ex);
    }
    return 0;
}
'''
MUTANTS = [   # (kind, statement, must_flag)
    ('add.s', 'ctx->f0.fl = ctx->f2.fl - ctx->f4.fl;', 1),
    ('div.s', 'ctx->f0.fl = ctx->f2.fl * (1.0f / ctx->f4.fl);', 1),
    ('neg.s', 'ctx->f0.fl = 0.0f - ctx->f2.fl;', 1),
    ('abs.s', 'ctx->f0.fl = ctx->f2.fl < 0 ? -ctx->f2.fl : ctx->f2.fl;', 1),
    ('sqrt.s', 'ctx->f0.fl = sqrtf(ctx->f2.fl) * 1.0000001f;', 1),
    ('mfc1', 'ctx->r2 = (uint32_t)ctx->f4.u32l;', 1),
    ('mtc1', 'ctx->f4.u64 = ctx->r2;', 1),
    ('mov.s', 'ctx->f0.fl = ctx->f2.fl + 0.0f;', 1),   # (float)(double)x is folded by clang -> no-op, so not a control
    ('add.d', 'ctx->f0.d = (double)(float)(ctx->f2.d + ctx->f4.d);', 1),
    ('mul.d', 'ctx->f0.d = ctx->f2.d * ctx->f4.d * (1.0 + 0x1p-52);', 1),
    ('mul.s', 'ctx->f0.fl = (float)((double)ctx->f2.fl * (double)ctx->f4.fl);', 0),    # neutral: exact product, one rounding
    ('add.s', 'ctx->f0.fl = (float)((double)ctx->f2.fl + (double)ctx->f4.fl);', 0),   # neutral: double rounding innocuous
]
def regs(kind, st):
    if kind == 'mfc1': m = re.match(r'ctx->r(\d+) = .*ctx->f(?:_odd\[\()?(\d+)', st); return int(m.group(1)), int(m.group(2)), -1
    if kind == 'mtc1':
        m = re.match(r'ctx->f(?:_odd\[\()?(\d+)\S* (?:- 1\) \* 2\] )?= (?:ctx->r(\d+)|0)', st); return int(m.group(1)), int(m.group(2) or 0), -1
    f = [int(x) for x in re.findall(r'ctx->f(\d+)', st)]
    return f[0], f[1], (f[2] if kind.split('.')[0] in BIN and len(f) > 2 else -1)

FUSED = re.compile(r'\t(fn?m(?:add|sub))\t')
def scan_obj(o, genlines):
    """fused FP instructions in object o, each attributed (DWARF line) to a generated guest-op statement or to other code."""
    out = subprocess.run(['objdump', '-d', '-l', '--no-show-raw-insn', o], capture_output=True, text=True).stdout
    src = None; gen = []; oth = collections.Counter()
    for line in out.split('\n'):
        if line.startswith('; /'): src = line[2:].strip(); continue
        if FUSED.search(line):
            f, _, ln = (src or '?:0').rpartition(':'); key = (os.path.basename(f), int(ln or 0))
            if key in genlines: gen.append(key)
            else: oth[key] += 1
    rel = subprocess.run(['objdump', '-r', o], capture_output=True, text=True).stdout
    return gen, oth, len(re.findall(r'___assert_rtn', rel))
def objcensus(genlines):
    objs = sorted(glob.glob(os.path.join(ROOT, 'build/CMakeFiles/RecompiledFuncs.dir/**/*.o'), recursive=True))
    gen = []; oth = collections.Counter(); asrt = 0
    for o in objs:
        g, t, a = scan_obj(o, genlines); gen += g; oth.update(t); asrt += a
    return len(objs), gen, oth, asrt
def scanner_control():
    """positive control for the object scan: a mul+add statement under the game flags must show one fused op on a known line."""
    d = tempfile.mkdtemp(prefix='s7415c_'); c = os.path.join(d, 'ctl.c'); o = os.path.join(d, 'ctl.o')
    open(c, 'w').write('#include "recomp.h"\nvoid ctl(recomp_context* ctx) {\n    ctx->f0.fl = ctx->f2.fl * ctx->f4.fl + ctx->f6.fl;\n}\n'
                       'void ctl2(recomp_context* ctx) {\n    ctx->f0.fl = MUL_S(ctx->f2.fl, ctx->f4.fl);\n    ctx->f0.fl = ctx->f0.fl + ctx->f6.fl;\n}\n')
    subprocess.run(['cc', '-g', '-std=gnu17', '-O2', '-w', '-fno-strict-aliasing', '-DRS64_BYTE_WATCH', '-include', FORCE, '-I', INC, '-c', c, '-o', o], check=True)
    g, t, a = scan_obj(o, {('ctl.c', 3), ('ctl.c', 6), ('ctl.c', 7)})
    return collections.Counter(g)

def soakcensus():
    hit = collections.Counter(); nlog = 0
    # s7804: retained soak logs are zstd'd over time (*.log.zst); the raw-only glob silently skipped them
    from rs64_zopen import zopen
    logs = glob.glob(os.path.join(ROOT, 'scratch/agent/soak_results/*.log')) + glob.glob(os.path.join(ROOT, 'build/*.log'))
    logs += [z for z in glob.glob(os.path.join(ROOT, 'scratch/agent/soak_results/*.log.zst')) if not os.path.exists(z[:-4])]
    for p in logs:
        nlog += 1
        try: s = zopen(p).read()
        except Exception: continue
        for m in re.finditer(r'Assertion failed: \((.*?)\)', s): hit[m.group(1)] += 1
    return nlog, hit

def main():
    K = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
    sites, forms, bad, patch, mid = harvest()
    print('[s7415] sites per op:', ' '.join('%s=%d' % kv for kv in sorted(sites.items())))
    print('[s7415] distinct forms %d, unmatched %d, PATCH pass-through %d, mid-line disasm comments %s' % (len(forms), len(bad), len(patch), dict(mid)))
    for b in bad[:12]: print('  BAD', b)
    print('[s7415] s2181 logger pass-through lines skipped: %s' % dict(harvest.obs))
    for p in patch: print('  PATCH', p)
    R = random.Random(7415); vec = {}; tmp = tempfile.mkdtemp(prefix='s7415_')
    blob = [struct.pack('<I', len(KINDS))]
    for k in KINDS:
        rows = []
        for a, b in vectors(k, K, R):
            rows.append((a, b, model(k, a, b, 0), model(k, b, b, 0), model(k, a, b, 1), model(k, b, b, 1)))
        blob.append(struct.pack('<I', len(rows)) + b''.join(struct.pack('<6Q', *r) for r in rows))
        vec[k] = len(rows)
    vf = os.path.join(tmp, 'vec.bin'); open(vf, 'wb').write(b''.join(blob))
    tab = [(k, st, -1) for (k, st) in sorted(forms)] + [(k, st, f) for (k, st, f) in MUTANTS]
    src = [C_HEAD]
    src.append('static const int KDBL[] = {%s};' % ','.join('1' if k.endswith('.d') else '0' for k in KINDS))
    src.append('static const int KCLS[] = {%s};' % ','.join('2' if k == 'mfc1' else '3' if k == 'mtc1' else '1' if k.split('.')[0] in ('mov',) else '0' for k in KINDS))
    src.append('static const int KSTRICT[] = {%s};' % ','.join('1' if k.startswith('mov') else '0' for k in KINDS))
    for i, (k, st, c) in enumerate(tab): src.append('__attribute__((noinline)) static void F%d(recomp_context* ctx) { %s }' % (i, st))
    src.append('static const T TAB[] = {')
    for i, (k, st, c) in enumerate(tab):
        d, s, t = regs(k, st); src.append('{F%d,%d,%d,%d,%d,%d,0},' % (i, KINDS.index(k), d, s, t, c))
    src.append('};\n#define NT %d' % len(tab)); src.append(C_MAIN)
    cf = os.path.join(tmp, 'h.c'); open(cf, 'w').write('\n'.join(src)); exe = os.path.join(tmp, 'h')
    r = subprocess.run(['cc', '-g', '-std=gnu17', '-O2', '-w', '-fno-strict-aliasing', '-DRS64_BYTE_WATCH', '-include', FORCE, '-I', INC, cf, '-o', exe],
                       capture_output=True, text=True)
    if r.returncode: print(r.stderr[:3000]); return 3
    agg = {}; ctl_ok = True; eq = True
    for fz in (0, 1):
        pr = subprocess.run([exe, vf, str(fz)], capture_output=True, text=True)
        if pr.returncode: print('harness rc', pr.returncode, pr.stderr[:500]); return 3
        per = collections.defaultdict(lambda: [0, 0, 0, 0, 0, '']);
        for line in pr.stdout.split('\n'):
            if not line: continue
            ti, ctl, n, mi, nanp, stray, ex = line.split('|', 6); ti = int(ti); ctl = int(ctl); k, st, _ = tab[ti]
            n, mi, nanp, stray = int(n), int(mi), int(nanp), int(stray)
            if ctl >= 0:
                flagged = (mi + stray) > 0
                ok = flagged == bool(ctl); ctl_ok &= ok if fz == 0 else True
                if fz == 0: print('  CONTROL %-6s %-4s %-70s mism=%d stray=%d %s' % (k, 'PASS' if ok else 'FAIL', st[:70], mi, stray, ex[:80]))
                continue
            p = per[k]; p[0] += 1; p[1] += n; p[2] += mi; p[3] += nanp; p[4] += stray
            if mi and not p[5]: p[5] = '%s :: %s' % (st, ex)
        print('[s7415] FZ=%d arm (model FZ=%d):' % (fz, fz))
        for k in KINDS:
            if k not in per: print('   %-7s 0 forms' % k); continue
            p = per[k]; print('   %-7s forms=%4d cases=%9d mism=%d nan_payload=%d stray=%d %s' % (k, p[0], p[1], p[2], p[3], p[4], p[5][:140]))
            if p[2] or p[4]: eq = False
    sc = scanner_control()
    print('[s7415] object-scan control: one-statement mul+add -> fused %d; two generated statements (MUL_S; +) -> fused %d'
          % (sc[('ctl.c', 3)], sc[('ctl.c', 6)] + sc[('ctl.c', 7)]))
    if sc[('ctl.c', 3)] < 1: ctl_ok = False
    no, gen, oth, asrt = objcensus(GENLINES)
    print('[s7415] object census: %d objs, fused ops on generated guest-op lines %d %s, on other (patch/helper) lines %d in %d lines, '
          '___assert_rtn relocs %d' % (no, len(gen), gen[:6], sum(oth.values()), len(oth), asrt))
    for k, v in oth.most_common(8): print('     other %s:%d x%d' % (k[0], k[1], v))
    if gen: eq = False
    nl, hit = soakcensus()
    print('[s7415] runtime: %d logs, NAN_CHECK fires %d, all assert fires %s' % (nl, hit.get('val == val', 0), dict(hit)))
    print('CONTROL', 'PASS' if ctl_ok else 'FAIL')
    print('VERDICT', 'H-equal' if eq and not bad else 'H-differs')
    return 0 if (ctl_ok and eq and not bad) else 3
if __name__ == '__main__': sys.exit(main())
