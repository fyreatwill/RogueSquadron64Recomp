#!/usr/bin/env python3
"""s7414 class BX: FP compare (c.cond.fmt) + FP branch (bc1t/bc1f/bc1tl/bc1fl) emission semantics.
N64Recomp lowers c.cond.fmt to `c1cs = ctx->fS.<fl|d> OP ctx->fT.<fl|d>;` (operations.cpp table) into a function-local
`int c1cs = 0;`, and bc1x to `if (c1cs) {` / `if (!c1cs) {`. cfc1/ctc1 only touch the rounding mode (get/set_cop1_cs).
1. Harvest every c.cond site in ../N64Recomp/RecompiledFuncs: statement verbatim (skipping the CHECK_FR / PC-stamp
   pass-through prefixes), checked against the disasm (operator per cond, .fl for .s / .d for .d, fs/ft registers).
2. Each distinct form compiled verbatim against the real header (-O2, -DRS64_BYTE_WATCH, force header) and driven with
   an all-pairs special-value set (+-0, min/max denormal, min normal, +-1, 1+ulp, max, +-inf, qNaN, sNaN, -NaN) plus
   random pairs, vs the MIPS cond table (bit0 unordered, bit1 equal, bit2 less; the signalling half only adds the
   invalid trap, which the game never enables). Two host arms: FPCR.FZ=0 and FZ=1 (ROGUESQ_FTZ default on, s7405).
3. Positive control: per-op operator mutants (lt->ult `!(a>=b)`, le->ule `!(a>b)`, eq->ueq, ole->olt) must flag their
   own op only. The generator's latent table (un->False, ueq->==, ult-><, ...) is scored on a synthetic emission too.
4. Branch census: every bc1x lowering has the right polarity. Reaching-definition dataflow over each function's guest
   CFG (delay slots, likely-nullification, calls, jump tables): every bc1x must read a c1cs written by a c.cond in the
   same function with no call/ctc1 in between (CLEAN); ENTRY / CALL / CTC1 reach are listed.
Usage: tools/s7414_fp_compare.py [K]   rc 0 = H-equal + CONTROL PASS + all bc1x CLEAN, rc 3 otherwise."""
import os, re, sys, subprocess, tempfile, collections, shutil
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
INC = os.path.join(ROOT, 'lib/N64ModernRuntime/N64Recomp/include')
FORCE = os.path.join(ROOT, 'include/rsp_dpc_macros.h')
FUNCS = os.path.join(ROOT, '../N64Recomp/RecompiledFuncs')
CONDS = 'f un eq ueq olt ult ole ule sf ngle seq ngl lt nge le ngt'.split()
CC = {c: i for i, c in enumerate(CONDS)}
GEN_OP = {'f': '0', 'un': '0', 'eq': '==', 'ueq': '==', 'olt': '<', 'ult': '<', 'ole': '<=', 'ule': '<=',
          'sf': '0', 'ngle': '0', 'seq': '==', 'ngl': '==', 'lt': '<', 'nge': '<', 'le': '<=', 'ngt': '<='}  # operations.cpp
MUT = {'lt': lambda a, b: '!(%s >= %s)' % (a, b), 'le': lambda a, b: '!(%s > %s)' % (a, b),
       'eq': lambda a, b: '(%s == %s || %s != %s || %s != %s)' % (a, b, a, a, b, b), 'ole': lambda a, b: '%s < %s' % (a, b)}
OPN = {'==': 'eq', '<': 'lt', '<=': 'le'}
cpat = re.compile(r'^\s*// 0x([0-9A-F]{8}): (\S+)(?:\s+(.*?))?\s*$')
fnpat = re.compile(r'^(?:RECOMP_FUNC|static) void (\w+)\(uint8_t\* rdram, recomp_context\* ctx\) \{')  # fixup-renamed inner bodies are static
BR_COND = set('beq bne blez bgtz bltz bgez bc1t bc1f beql bnel blezl bgtzl bltzl bgezl bc1tl bc1fl bltzal bgezal'.split())
LIKELY = set('beql bnel blezl bgtzl bltzl bgezl bc1tl bc1fl'.split())
LINKB = {'bltzal', 'bgezal', 'bal'}
LABELS = {}
JT = {}   # (fn, jr addr) -> switch targets

def harvest():
    forms = collections.Counter(); obs = []; bad = []; br = collections.Counter(); brbad = []; funcs = {}
    for f in sorted(os.listdir(FUNCS)):
        if not f.endswith('.c'): continue
        lines = open(os.path.join(FUNCS, f), errors='replace').read().split('\n'); fn = None
        for i, line in enumerate(lines):
            mf = fnpat.match(line)
            if mf: fn = mf.group(1); funcs.setdefault(fn, {}); continue
            mj = re.match(r'^\s*switch \(jr_addend_([0-9A-F]{8}) >> 2\) \{', line)
            if mj and fn is not None:
                tg = set()
                for l2 in lines[i + 1:]:
                    mt = re.match(r'^\s*case \d+: goto L_([0-9A-F]{8});', l2)
                    if not mt: break
                    tg.add(int(mt.group(1), 16))
                JT[(fn, int(mj.group(1), 16))] = tg
            ml = re.match(r'^\s*L_([0-9A-F]{8}):', line)
            if ml and fn is not None: LABELS.setdefault(fn, set()).add(int(ml.group(1), 16))
            for mm in re.finditer(r'(?<!^)(?<=\S)\s*// 0x([0-9A-F]{8}): (\S+)(?:[ \t]+(.*?))?\s*$', line):
                if fn is not None and not line.lstrip().startswith('//'):
                    funcs[fn].setdefault(int(mm.group(1), 16), (mm.group(2), mm.group(3) or ''))   # mid-line disasm comment
            m = cpat.match(line)
            if not m or fn is None: continue
            addr = int(m.group(1), 16); op = m.group(2); args = m.group(3) or ''
            funcs[fn].setdefault(addr, (op, args))
            nxt = None
            for j in range(i + 1, min(i + 8, len(lines))):
                l = re.sub(r'/\*.*?\*/', '', lines[j]).strip()
                if not l or re.match(r'^L_[0-9A-F]{8}:$', l): continue
                if cpat.match(lines[j]): break
                if l.startswith('g_rs64_last_guest_pc = ') or re.match(r'CHECK_FR\(ctx, \d+\);$', l): continue
                if lines[j].strip().startswith('{ /* PATCH: s3288 viewer fade */'):   # pass-through logger, c1cs passed by value
                    obs.append((fn, '%08X' % int(m.group(1), 16)))
                    while j < len(lines) - 1 and lines[j].strip() != '}': j += 1
                    nxt = lines[j + 1].strip(); break
                nxt = l; break
            mc = re.match(r'c\.(\w+)\.([sd])$', op)
            if mc:
                cond, fmt = mc.groups(); ra = re.findall(r'\$f(\d+)', args)
                fld = 'fl' if fmt == 's' else 'd'
                want = None
                if len(ra) == 2 and GEN_OP[cond] not in ('0',):
                    want = 'c1cs = ctx->f%s.%s %s ctx->f%s.%s;' % (ra[0], fld, GEN_OP[cond], ra[1], fld)
                if nxt != want: bad.append((fn, '%08X' % addr, op, args, nxt)); continue
                forms[(cond, fmt, int(ra[0]), int(ra[1]), nxt)] += 1
            elif op in ('bc1t', 'bc1f', 'bc1tl', 'bc1fl'):
                want = 'if (c1cs) {' if op in ('bc1t', 'bc1tl') else 'if (!c1cs) {'
                if nxt != want: brbad.append((fn, '%08X' % addr, op, nxt))
                br[op] += 1
    harvest.obs = obs
    return forms, bad, br, brbad, funcs

C_HEAD = r'''
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "recomp.h"
uint32_t rs64_ram_top = 0x80800000u;
typedef int (*tfn)(recomp_context*);
typedef struct { tfn f; int cond, dbl, fs, ft; } T;
'''
C_MAIN = r'''
static uint64_t s = 0x9E3779B97F4A7C15ull;
static uint64_t rnd(void) { s ^= s << 13; s ^= s >> 7; s ^= s << 17; return s; }
static const uint32_t SV[] = {0,0x80000000u,1,0x007FFFFFu,0x00800000u,0x3F800000u,0xBF800000u,0x3F800001u,0x7F7FFFFFu,
  0x7F800000u,0xFF800000u,0x7FC00000u,0x7F800001u,0xFFC00001u,0x80000001u,0x3F7FFFFFu};
static const uint64_t DV[] = {0,0x8000000000000000ull,1,0x000FFFFFFFFFFFFFull,0x0010000000000000ull,0x3FF0000000000000ull,
  0xBFF0000000000000ull,0x3FF0000000000001ull,0x7FEFFFFFFFFFFFFFull,0x7FF0000000000000ull,0xFFF0000000000000ull,
  0x7FF8000000000000ull,0x7FF0000000000001ull,0xFFF8000000000001ull,0x8000000000000001ull,0x3FEFFFFFFFFFFFFFull};
#define NSV 16
static int isnan_s(uint32_t v) { return (v & 0x7F800000u) == 0x7F800000u && (v & 0x7FFFFFu); }
static int isnan_d(uint64_t v) { return (v & 0x7FF0000000000000ull) == 0x7FF0000000000000ull && (v & 0xFFFFFFFFFFFFFull); }
static int isden_s(uint32_t v) { return !(v & 0x7F800000u) && (v & 0x7FFFFFu); }
static int isden_d(uint64_t v) { return !(v & 0x7FF0000000000000ull) && (v & 0xFFFFFFFFFFFFFull); }
/* exact IEEE order on bit patterns (non-NaN): returns -1/0/1 */
static int ord_s(uint32_t a, uint32_t b) { if (!((a | b) & 0x7FFFFFFFu)) return 0; int64_t x = (a >> 31) ? -(int64_t)(a & 0x7FFFFFFFu) : a, y = (b >> 31) ? -(int64_t)(b & 0x7FFFFFFFu) : b; return x < y ? -1 : x > y; }
static int ord_d(uint64_t a, uint64_t b) { if (!((a | b) & 0x7FFFFFFFFFFFFFFFull)) return 0; __int128 x = (a >> 63) ? -(__int128)(a & 0x7FFFFFFFFFFFFFFFull) : (__int128)a, y = (b >> 63) ? -(__int128)(b & 0x7FFFFFFFFFFFFFFFull) : (__int128)b; return x < y ? -1 : x > y; }
static int model(int cond, int dbl, uint64_t a, uint64_t b) {
    int un = dbl ? (isnan_d(a) || isnan_d(b)) : (isnan_s((uint32_t)a) || isnan_s((uint32_t)b));
    if (un) return cond & 1;
    int o = dbl ? ord_d(a, b) : ord_s((uint32_t)a, (uint32_t)b);
    return ((cond & 4) && o < 0) || ((cond & 2) && o == 0);
}
static void setfz(int on) {
#if defined(__aarch64__)
    uint64_t r; __asm__ volatile("mrs %0, fpcr" : "=r"(r)); r = on ? (r | (1ull << 24)) : (r & ~(1ull << 24));
    __asm__ volatile("msr fpcr, %0" :: "r"(r));
#else
    (void)on;
#endif
}
static fpr* Fp(recomp_context* c, int i) { return &c->f0 + i; }
int main(int argc, char** argv) {
    int K = argc > 1 ? atoi(argv[1]) : 2000, fz = argc > 2 ? atoi(argv[2]) : 0;
    long long n[16][2] = {{0}}, mism[16][2] = {{0}}, mden[16][2] = {{0}}; int ex = 0;
    setfz(fz);
    for (int ti = 0; ti < NT; ti++) {
        const T* t = &TAB[ti];
        for (int k = 0; k < NSV * NSV + K; k++) {
            recomp_context c; memset(&c, 0, sizeof c);
            uint64_t a, b;
            if (k < NSV * NSV) { a = t->dbl ? DV[k / NSV] : SV[k / NSV]; b = t->dbl ? DV[k % NSV] : SV[k % NSV]; }
            else { a = rnd(); b = (k & 3) == 0 ? a : (k & 3) == 1 ? a + (rnd() & 3) - 1 : rnd(); if (!t->dbl) { a = (uint32_t)a; b = (uint32_t)b; if ((k & 3) == 1) b = (uint32_t)((uint32_t)a + (uint32_t)(rnd() & 3) - 1); } }
            for (int r = 0; r < 32; r++) Fp(&c, r)->u64 = rnd();
            if (t->dbl) { Fp(&c, t->fs)->u64 = a; Fp(&c, t->ft)->u64 = b; }
            else { Fp(&c, t->fs)->u32l = (uint32_t)a; Fp(&c, t->ft)->u32l = (uint32_t)b; }
            if (t->fs == t->ft) a = b;   /* same register: holds the last write */
            int got = t->f(&c), want = model(t->cond, t->dbl, a, b);
            int den = t->dbl ? (isden_d(a) || isden_d(b)) : (isden_s((uint32_t)a) || isden_s((uint32_t)b));
            n[t->cond][t->dbl]++;
            if (got != want) { if (den) mden[t->cond][t->dbl]++; else { mism[t->cond][t->dbl]++; if (ex++ < 6) printf("EX form=%d cond=%d dbl=%d a=%llx b=%llx got=%d want=%d\n", ti, t->cond, t->dbl, (unsigned long long)a, (unsigned long long)b, got, want); } }
        }
    }
    for (int c = 0; c < 16; c++) for (int d = 0; d < 2; d++) if (n[c][d]) printf("ROW %d %d n=%lld mism=%lld mden=%lld\n", c, d, n[c][d], mism[c][d], mden[c][d]);
    return 0;
}
'''

def build_run(forms, k, fz, tag, td, xform=None):
    src = os.path.join(td, 'f_%s.c' % tag); exe = os.path.join(td, 'x_%s' % tag)
    out = [C_HEAD]
    for i, (cond, fmt, fs, ft, stmt) in enumerate(forms):
        if xform: stmt = xform(cond, fmt, fs, ft, stmt)
        out.append('static int f%d(recomp_context* ctx) { int c1cs = 0; %s return c1cs; }\n' % (i, stmt))
    out.append('static const T TAB[] = {\n' + ''.join('{f%d,%d,%d,%d,%d},\n' % (i, CC[f[0]], f[1] == 'd', f[2], f[3])
                                                   for i, f in enumerate(forms)) + '};\n#define NT %d\n' % len(forms))
    out.append(C_MAIN); open(src, 'w').write(''.join(out))
    r = subprocess.run(['cc', '-O2', '-w', '-fno-strict-aliasing', '-DRS64_BYTE_WATCH', '-include', FORCE, '-I', INC, src, '-o', exe],
                       capture_output=True, text=True)
    if r.returncode: sys.exit('compile failed (%s):\n%s' % (tag, r.stderr[:3000]))
    pr = subprocess.run([exe, str(k), str(fz)], capture_output=True, text=True, env={})
    if pr.returncode: sys.exit('harness %s died rc=%d\n%s' % (tag, pr.returncode, pr.stdout[-2000:]))
    rows = {(CONDS[int(m.group(1))], 'sd'[int(m.group(2))]): tuple(int(m.group(x)) for x in (3, 4, 5))
            for m in re.finditer(r'ROW (\d+) (\d) n=(\d+) mism=(\d+) mden=(\d+)', pr.stdout)}
    return rows, pr.stdout

def branch_reach(funcs):
    """Forward dataflow of the c1cs source per guest instruction. Tokens: D = written by a c.cond, E = function-entry
    value (recomp: 0, guest: caller's), X = a call happened since (guest: callee's last compare), W = ctc1 since."""
    res = collections.Counter(); lst = []
    for fn, ins in funcs.items():
        if not ins: continue
        addrs = sorted(ins); aset = set(addrs); labels = sorted(LABELS.get(fn, set()) & aset)
        def tgt(args):
            m = re.search(r'L_([0-9A-F]{8})\s*$', args)
            return int(m.group(1), 16) if m else None
        def bsucc(b):
            op, args = ins[b]
            if op in BR_COND or op in LINKB or op == 'b':
                t = tgt(args); s = [] if op == 'b' or op == 'bal' else [b + 8]
                if t is not None and t in aset: s.append(t)
                return s
            if op == 'j':
                t = tgt(args); return [t] if t in aset else []   # j to a function = tail call -> exit
            if op == 'jal' or op == 'jalr': return [b + 8]
            if op == 'jr': return sorted(JT.get((fn, b), ()))  # jr $ra / indirect tail call = exit; jump table = its switch targets
            return None
        def is_br(a): return a in ins and bsucc(a) is not None
        def succ(a):
            if is_br(a - 4):
                s = bsucc(a - 4)
                if ins[a - 4][0] in LIKELY: s = [x for x in s if x != a - 4 + 8]
                return s
            op = ins[a][0]
            if op == 'break': return []
            if is_br(a):
                return [a + 4, a + 8] if op in LIKELY else [a + 4]
            return [a + 4]
        def call_at(a):   # call effect lands after the delay slot a (a-4 is the linking branch)
            return is_br(a - 4) and (ins[a - 4][0] in ('jal', 'jalr') or ins[a - 4][0] in LINKB)
        st = {addrs[0]: frozenset('E')}; work = [addrs[0]]
        while work:
            a = work.pop(); s = st[a]; op = ins[a][0]
            if op.startswith('c.'): s = frozenset('D')
            elif op == 'ctc1': s = frozenset('W')
            if call_at(a): s = frozenset('X')
            for b in succ(a):
                if b not in ins: continue
                o = st.get(b, frozenset()); nw = o | s
                if nw != o or b not in st: st[b] = nw; work.append(b)
        for a in addrs:
            if ins[a][0] in ('bc1t', 'bc1f', 'bc1tl', 'bc1fl'):
                s = st.get(a)
                if s is None: res['UNREACHED'] += 1; lst.append((fn, '%08X' % a, 'UNREACHED')); continue
                k = 'CLEAN' if s == frozenset('D') else '+'.join(sorted(s))
                res[k] += 1
                if k != 'CLEAN': lst.append((fn, '%08X' % a, k))
    return res, lst

def main():
    k = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
    forms, bad, br, brbad, funcs = harvest()
    fl = sorted(forms)
    per = collections.Counter(); [per.__setitem__((f[0], f[1]), per[(f[0], f[1])] + forms[f]) for f in fl]
    print('HARVEST c.cond sites=%d distinct forms=%d nonconforming=%d' % (sum(forms.values()), len(fl), len(bad)))
    for (c, f), v in sorted(per.items()): print('  c.%s.%s sites=%d forms=%d' % (c, f, v, sum(1 for x in fl if x[:2] == (c, f))))
    for b in bad[:10]: print('  NONCONF', b)
    print('BRANCH bc1x sites=%d %s polarity-bad=%d observer-prefixed=%s' % (sum(br.values()), dict(br), len(brbad), harvest.obs))
    for b in brbad[:10]: print('  BRBAD', b)
    td = tempfile.mkdtemp(prefix='s7414_'); ok = True
    for fz in (0, 1):
        rows, o = build_run(fl, k, fz, 'real%d' % fz, td)
        tm = sum(r[1] for r in rows.values()); tdn = sum(r[2] for r in rows.values()); tn = sum(r[0] for r in rows.values())
        print('ARM FZ=%d cases=%d mism=%d mism_denormal_only=%d' % (fz, tn, tm, tdn))
        for key, r in sorted(rows.items()): print('  c.%s.%s n=%d mism=%d mden=%d' % (key + r))
        for l in o.split('\n'):
            if l.startswith('EX'): print('  ' + l)
        if tm or (fz == 0 and tdn): ok = False
    # positive control: mutants per op on the real forms
    cok = True
    for op, mk in MUT.items():
        def xf(cond, fmt, fs, ft, stmt, op=op, mk=mk):
            if cond != op: return stmt
            fld = 'fl' if fmt == 's' else 'd'
            return 'c1cs = %s;' % mk('ctx->f%d.%s' % (fs, fld), 'ctx->f%d.%s' % (ft, fld))
        if not any(f[0] == op for f in fl): print('CONTROL %s: no sites' % op); continue
        rows, _ = build_run(fl, 200, 0, 'mut_' + op, td, xf)
        own = sum(r[1] for kk, r in rows.items() if kk[0] == op); other = sum(r[1] for kk, r in rows.items() if kk[0] != op)
        p = own > 0 and other == 0; cok &= p
        print('CONTROL mutant %s: own_mism=%d other_mism=%d %s' % (op, own, other, 'PASS' if p else 'FAIL'))
    # latent generator table: every cond, synthetic emission as operations.cpp would print it
    syn = []
    for c in CONDS:
        for f in 'sd':
            fld = 'fl' if f == 's' else 'd'
            st = 'c1cs = 0;' if GEN_OP[c] == '0' else 'c1cs = ctx->f2.%s %s ctx->f4.%s;' % (fld, GEN_OP[c], fld)
            syn.append((c, f, 2, 4, st))
    rows, _ = build_run(syn, 200, 0, 'latent', td)
    lat = sorted('%s.%s' % kk for kk, r in rows.items() if r[1])
    print('LATENT generator-table conds wrong on NaN (0 game sites unless listed above): %s' % ' '.join(lat))
    used_lat = [f for f in fl if '%s.%s' % (f[0], f[1]) in lat]
    print('LATENT used by game: %d forms' % len(used_lat))
    if used_lat: ok = False
    # dataflow positive control: planted CALL-cross, ENTRY-reach, ctc1, likely-delay-only compare, jump-table join
    P = {'s7414_plant_call': {0x100: ('c.lt.s', '$f0, $f2'), 0x104: ('jal', '0x80001000'), 0x108: ('nop', ''),
                              0x10C: ('bc1t', 'L_00000118'), 0x110: ('nop', ''), 0x114: ('nop', ''), 0x118: ('jr', '$ra'), 0x11C: ('nop', '')},
         's7414_plant_entry': {0x200: ('beq', '$a0, $zero, L_0000020C'), 0x204: ('nop', ''), 0x208: ('c.eq.s', '$f0, $f2'),
                               0x20C: ('bc1f', 'L_00000218'), 0x210: ('nop', ''), 0x214: ('nop', ''), 0x218: ('jr', '$ra'), 0x21C: ('nop', '')},
         's7414_plant_ctc1': {0x300: ('c.lt.s', '$f0, $f2'), 0x304: ('ctc1', '$t0, $FpcCsr'), 0x308: ('bc1t', 'L_00000314'),
                              0x30C: ('nop', ''), 0x310: ('nop', ''), 0x314: ('jr', '$ra'), 0x318: ('nop', '')},
         's7414_plant_likely': {0x400: ('beql', '$a0, $zero, L_0000040C'), 0x404: ('c.lt.s', '$f0, $f2'), 0x408: ('nop', ''),
                                0x40C: ('bc1t', 'L_00000418'), 0x410: ('nop', ''), 0x414: ('nop', ''), 0x418: ('jr', '$ra'), 0x41C: ('nop', '')},
         's7414_plant_clean': {0x500: ('c.lt.s', '$f0, $f2'), 0x504: ('nop', ''), 0x508: ('bc1t', 'L_00000514'),
                               0x50C: ('nop', ''), 0x510: ('nop', ''), 0x514: ('jr', '$ra'), 0x518: ('nop', '')}}
    pr, pl = branch_reach(P); pk = {fn: k for fn, a, k in pl}
    pexp = {'s7414_plant_call': 'X', 's7414_plant_entry': 'D+E', 's7414_plant_ctc1': 'W', 's7414_plant_likely': 'D+E'}
    rok = all(pk.get(f) == v for f, v in pexp.items()) and 's7414_plant_clean' not in pk
    print('CONTROL reach plants: %s %s' % (pk, 'PASS' if rok else 'FAIL')); cok &= rok
    res, lst = branch_reach(funcs)
    # UNREACHED = dead interior copy of a separately emitted function (size over-detection, e.g. tickCraftSelectScreen
    # holds handleCraftSelectInput's body; its jal goes to the real one). Score the twin site in the other function.
    kind = {(fn, a): k for fn, a, k in lst}
    lst2 = []
    for fn, a, k in lst:
        if k == 'UNREACHED':
            tw = [(f2, kind.get((f2, a), 'CLEAN')) for f2, ins in funcs.items() if f2 != fn and int(a, 16) in ins
                  and ins[int(a, 16)][0].startswith('bc1')]
            if tw and all(t[1] == 'CLEAN' for t in tw):
                res['UNREACHED'] -= 1; res['DEADDUP_TWIN_CLEAN'] += 1; k = 'DEADDUP twin=%s CLEAN' % tw[0][0]
        if k == 'E' and fn.startswith('data_gap_'):
            res['E'] -= 1; res['E_DATA_GAP'] += 1; k = 'E data_gap (0 static callers; entry-region bc1 = data)'
        lst2.append((fn, a, k))
    res = +res; lst = lst2
    print('REACH bc1x: %s' % dict(res))
    for l in lst[:40]: print('  REACH', l)
    clean = set(res) <= {'CLEAN', 'DEADDUP_TWIN_CLEAN', 'E_DATA_GAP'}
    shutil.rmtree(td, ignore_errors=True)
    print('VERDICT %s CONTROL %s REACH %s' % ('H-equal' if ok and not bad and not brbad else 'H-diff', 'PASS' if cok else 'FAIL',
                                          'CLEAN' if clean else 'NOT-CLEAN'))
    sys.exit(0 if ok and cok and clean and not bad and not brbad else 3)

if __name__ == '__main__': main()
