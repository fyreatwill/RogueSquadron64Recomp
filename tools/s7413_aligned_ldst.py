#!/usr/bin/env python3
"""s7413 class BW: aligned load/store macro semantics on the word-swizzled rdram.
recomp.h MEM_B (both the plain and the RS64_BYTE_WATCH variant -- the real build defines RS64_BYTE_WATCH), MEM_BU, MEM_H,
MEM_HU, MEM_W, LD/load_doubleword, SD, and include/rsp_dpc_macros.h MEM_WU. Guest byte a lives at host a^3, a guest
word is one native uint32.
1. Harvest every emitted lb lbu lh lhu lw lwu ld sb sh sw sd lwc1 ldc1 swc1 sdc1 site in ../N64Recomp/RecompiledFuncs
   with its lowering statement (the first line after the disasm comment that carries the op's macro). Forms whose
   statement only uses ctx/macros and the pass-through observers RS64_S5798_ST / rs64_s4307_synth_read (stubbed here)
   are compiled VERBATIM, one C function per distinct (operands, statement) form, against the real build header
   (-DRS64_BYTE_WATCH, -include include/rsp_dpc_macros.h, -O2). Every other site (guards, gates) is counted per op.
2. Each form runs K cases vs a byte-wise big-endian VR4300 model driven by the DISASM operands (rt, offset, base):
   random register file, random 64-byte memory image around the target, every legal alignment of the op, KSEG0 base.
   Loads: dest == sign/zero-extended BE value, every other GPR/FPR unchanged. Stores: exactly the op's width written,
   neighbour bytes and the whole 128 KB image unchanged (full compare per form).
3. Positive control: one mutant header per macro (swizzle ^3->^1, ^2->^0, sign<->zero extension, SD/LD hi/lo swap) on
   a deterministic per-op sample of forms must MISM in its own ops and nowhere else.
4. KSEG1: the macros subtract 0xFFFFFFFF80000000 only, so a 0xA0xxxxxx guest address maps to rdram+0x20000000+phys,
   which is the PROT_NONE part of librecomp's 4 GB reservation (not an alias). Measured here (address arithmetic only)
   and paired with a static census of lui 0xA000-0xBFFF constants and of $zero-base (absolute KUSEG/KSEG3) sites.
Usage: tools/s7413_aligned_ldst.py [K]   rc 0 = H-equal (0 MISM) + CONTROL PASS, rc 3 otherwise."""
import os, re, sys, subprocess, tempfile, collections, shutil
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
INC = os.path.join(ROOT, 'lib/N64ModernRuntime/N64Recomp/include')
FORCE = os.path.join(ROOT, 'include/rsp_dpc_macros.h')
FUNCS = os.path.join(ROOT, '../N64Recomp/RecompiledFuncs')
REGS = ['zero', 'at', 'v0', 'v1', 'a0', 'a1', 'a2', 'a3', 't0', 't1', 't2', 't3', 't4', 't5', 't6', 't7',
        's0', 's1', 's2', 's3', 's4', 's5', 's6', 's7', 't8', 't9', 'k0', 'k1', 'gp', 'sp', 'fp', 'ra']
RN = {n: i for i, n in enumerate(REGS)}; RN['s8'] = 30
OPS = 'lb lbu lh lhu lw lwu ld sb sh sw sd lwc1 ldc1 swc1 sdc1'.split()
OPID = {o: i for i, o in enumerate(OPS)}
MAC = {'lb': 'MEM_B(', 'lbu': 'MEM_BU(', 'lh': 'MEM_H(', 'lhu': 'MEM_HU(', 'lw': 'MEM_W(', 'lwu': 'MEM_WU(', 'ld': 'LD(',
       'sb': 'MEM_B(', 'sh': 'MEM_H(', 'sw': 'MEM_W(', 'sd': 'SD(', 'lwc1': 'MEM_W(', 'ldc1': 'LD(', 'swc1': 'MEM_W(',
       'sdc1': 'SD('}
OK_ID = set('ctx u32l u64 f_odd MEM_B MEM_BU MEM_H MEM_HU MEM_W MEM_WU LD SD U32 ADD32 uint32_t s4575_a '
            'rs64_s4307_synth_read rdram RS64_S5798_ST u'.split())

def harvest():
    cpat = re.compile(r'^\s*// 0x([0-9A-F]{8}): (\S+)\s+\$(\w+), (-?0x[0-9A-Fa-f]+|-?\d+)\(\$(\w+)\)\s*$')
    fnpat = re.compile(r'^RECOMP_FUNC void (\w+)\(')
    sites = []; impure = collections.Counter(); impure_ex = {}; zbase = []; zdest = 0; nomatch = []
    for f in sorted(os.listdir(FUNCS)):
        if not f.endswith('.c'): continue
        lines = open(os.path.join(FUNCS, f), errors='replace').read().split('\n'); fn = '?'
        for i, line in enumerate(lines):
            mf = fnpat.match(line)
            if mf: fn = mf.group(1); continue
            m = cpat.match(line)
            if not m or m.group(2) not in OPID: continue
            op = m.group(2); fp = op.endswith('c1')
            rt = int(m.group(3)[1:]) if fp else RN.get(m.group(3), -1)
            base = RN.get(m.group(5), -1); off = int(m.group(4), 0)
            if rt < 0 or base < 0: impure[op] += 1; continue
            if base == 0: zbase.append((fn, int(m.group(1), 16), op, off)); continue
            stmt = None; first = None; indiag = False
            for j in range(i + 1, min(i + 8, len(lines))):
                l = lines[j].strip()
                if cpat.match(lines[j]) or re.match(r'^\s*// 0x[0-9A-F]{8}:', lines[j]): break
                if l.startswith('// PATCH: write to $zero'): stmt = 'ZERO'; break
                if not l: continue
                if first is None: first = l
                if l.startswith('//') or l.startswith('/*'): continue
                lc = re.sub(r'/\*.*?\*/', '', l).strip()
                if indiag:
                    indiag = not lc.endswith((';', '}')); continue
                if l.startswith('if (__builtin_expect(g_rs64_store_diag, 0))'):
                    indiag = not lc.endswith((';', '}')); continue   # store observers gated off unless g_rs64_store_diag (may span lines)
                if l.startswith('g_rs64_last_guest_pc = ') or re.match(r'CHECK_FR\(ctx, \d+\);$', l):
                    continue     # pass-through prefixes (PC stamp; FR check, class BS s7409)
                if MAC[op] not in l: break   # anything else before the lowering = guarded/gated site
                code = re.sub(r'/\*.*?\*/', '', l).strip()
                ids = set(re.findall(r'[A-Za-z_]\w*', re.sub(r'\b0[xX][0-9A-Fa-f]+u?\b|\b\d+u?\b', ' ', code)))
                ids -= {'r%d' % k for k in range(32)} | {'f%d' % k for k in range(32)}
                if not (ids - OK_ID) and 'if' not in ids and code.startswith(('ctx->', 'MEM_', 'SD(', '{')) and code.endswith((';', '}')):
                    hx = ('-' if off < 0 else '') + '0X%X' % abs(off)
                    addr_ok = re.search(r'\(ctx->r%d, %s\)|\(%s, ctx->r%d\)|SD\([^;]*, %s, ctx->r%d\)|LD\(ctx->r%d, %s\)' % (base, hx, hx, base, hx, base, base, hx), code)
                    st = op[0] == 's'
                    if fp: dst = ('ctx->f%d.' % rt) if 'f_odd' not in code else ('ctx->f_odd[(%d - 1) * 2]' % rt)
                    elif not st: dst = 'ctx->r%d = ' % rt
                    elif op == 'sd': dst = 'SD(ctx->r%d, ' % rt if rt else 'SD(0, '
                    else: dst = '= ctx->r%d;' % rt if rt else '= 0;'
                    if addr_ok and dst in code: stmt = code
                    else: stmt = 'MISMATCH:' + code
                break
            if stmt == 'ZERO': zdest += 1; continue
            if stmt and stmt.startswith('MISMATCH:'):
                impure[op] += 1; nomatch.append((fn, m.group(1), op, stmt[9:][:100])); continue
            if stmt is None:
                impure[op] += 1; impure_ex.setdefault(op, (fn, m.group(1), (first or '')[:110])); continue
            fodd = -1
            mo = re.search(r'f_odd\[\((\d+) - 1\) \* 2\]', stmt)
            if mo: fodd = (int(mo.group(1)) - 1) * 2
            sites.append((op, rt, base, off, fodd, stmt))
    return sites, impure, impure_ex, zbase, zdest, nomatch

C_HEAD = r'''
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stddef.h>
#include "recomp.h"
#define RS64_S5798_ST(pc, off, base, w) ((void)0)
static void rs64_s4307_synth_read(uint8_t* r, uint32_t pc, uint32_t a, uint32_t v) { (void)r; (void)pc; (void)a; (void)v; }
uint32_t rs64_ram_top = 0x80800000u;
typedef void (*tfn)(recomp_context*, uint8_t*);
typedef struct { tfn f; int op, rt, base, off, fodd; } T;
'''
C_MAIN = r'''
#define MEMSZ 0x20000
static uint8_t host[MEMSZ], be[MEMSZ];
static uint64_t s = 0x9E3779B97F4A7C15ull;
static uint64_t rnd(void) { s ^= s << 13; s ^= s >> 7; s ^= s << 17; return s; }
static const int W[] = {1,1,2,2,4,4,8, 1,2,4,8, 4,8,4,8};
static const int ST[] = {0,0,0,0,0,0,0, 1,1,1,1, 0,0,1,1};
static uint64_t beval(int a, int w) { uint64_t v = 0; for (int i = 0; i < w; i++) v = (v << 8) | be[a + i]; return v; }
static void bestore(int a, int w, uint64_t v) { for (int i = 0; i < w; i++) be[a + i] = (uint8_t)(v >> (8 * (w - 1 - i))); }
static int64_t sxw(uint64_t v, int w) { int sh = 64 - 8 * w; return (int64_t)(v << sh) >> sh; }
static gpr* G(recomp_context* c, int i) { return &c->r0 + i; }
static fpr* Fp(recomp_context* c, int i) { return &c->f0 + i; }
static uint32_t fodd_buf[64], fodd_ref[64];
int main(int argc, char** argv) {
    int K = argc > 1 ? atoi(argv[1]) : 40;
    long long n[15] = {0}, mism[15] = {0}, stray[15] = {0}; int ex = 0;
    for (int ti = 0; ti < NT; ti++) {
        const T* t = &TAB[ti]; int w = W[t->op]; if (getenv("S7413_TRACE")) { printf("AT %d\n", ti); fflush(stdout); }
        memset(host, 0, MEMSZ); memset(be, 0, MEMSZ);
        for (int k = 0; k < K; k++) {
            recomp_context c, c0; uint64_t* q = (uint64_t*)&c;
            for (size_t i = 0; i < offsetof(recomp_context, f_odd) / 8; i++) q[i] = rnd();
            c.r0 = 0; c.f_odd = fodd_buf; c.status_reg = 0; c.mips3_float_mode = 0;
            for (int i = 0; i < 64; i++) fodd_ref[i] = fodd_buf[i] = (uint32_t)rnd();
            int a = 0x10000 + (int)(rnd() % (64 / w)) * w;           /* every legal alignment */
            for (int i = a - 32; i < a + 40; i++) { be[i] = (uint8_t)rnd(); host[i ^ 3] = be[i]; }
            if (t->base) *G(&c, t->base) = 0xFFFFFFFF80000000ull + (uint64_t)(int64_t)(a - t->off);
            c0 = c;
            uint64_t sv = 0;                                          /* store source value, from disasm rt */
            if (ST[t->op]) {
                if (t->op >= 13) sv = t->fodd >= 0 ? fodd_buf[t->fodd] : (w == 4 ? Fp(&c, t->rt)->u32l : Fp(&c, t->rt)->u64);
                else sv = t->rt ? *G(&c, t->rt) : 0;
                bestore(a, w, sv);
            }
            t->f(&c, host);
            int bad = 0;
            if (!ST[t->op]) {
                uint64_t v = beval(a, w);
                if (t->op <= 6) {   /* GPR loads: lb lbu lh lhu lw lwu ld */
                    uint64_t want = (t->op == 1 || t->op == 3 || t->op == 5 || t->op == 6) ? v : (uint64_t)sxw(v, w);
                    *G(&c0, t->rt) = want;
                } else if (t->fodd >= 0) fodd_ref[t->fodd] = (uint32_t)v;
                else if (w == 4) Fp(&c0, t->rt)->u32l = (uint32_t)v;
                else Fp(&c0, t->rt)->u64 = v;
                bad = memcmp(&c, &c0, offsetof(recomp_context, f_odd)) != 0 || memcmp(fodd_buf, fodd_ref, sizeof fodd_buf) != 0;
            } else bad = memcmp(&c, &c0, offsetof(recomp_context, f_odd)) != 0;
            for (int i = a - 32; i < a + 40; i++) if (host[i ^ 3] != be[i]) bad = 1;
            n[t->op]++; if (bad) { mism[t->op]++; if (ex++ < 6) printf("EX form=%d op=%d rt=%d base=%d off=%d a=0x%X\n", ti, t->op, t->rt, t->base, t->off, a); }
        }
        for (int i = 0; i < MEMSZ; i++) if (host[i ^ 3] != be[i]) { stray[t->op]++; break; }
    }
    for (int k = 0; k < 15; k++) printf("ROW %d n=%lld mism=%lld stray=%lld\n", k, n[k], mism[k], stray[k]);
    /* KSEG1: where do the macros put a 0xA0xxxxxx guest address? (address arithmetic only, no access) */
    { gpr b = 0xFFFFFFFFA0010000ull; uint8_t* rdram = host;
      printf("KSEG1 MEM_W off=0x%llX MEM_B off=0x%llX (phys 0x10000)\n",
             (unsigned long long)((uint8_t*)&MEM_W(0, b) - rdram), (unsigned long long)((uint8_t*)&MEM_B(0, b) - rdram)); }
    return 0;
}
'''

def build_run(sites, incdir, force, k, tag, td, bw=True):
    src = os.path.join(td, 'f_%s.c' % tag); exe = os.path.join(td, 'x_%s' % tag)
    out = [C_HEAD]
    for i, s in enumerate(sites): out.append('static void f%d(recomp_context* ctx, uint8_t* rdram) { %s }\n' % (i, s[5]))
    out.append('static const T TAB[] = {\n' + ''.join('{f%d,%d,%d,%d,%d,%d},\n' % (i, OPID[s[0]], s[1], s[2], s[3], s[4])
                                                   for i, s in enumerate(sites)) + '};\n#define NT %d\n' % len(sites))
    out.append(C_MAIN)
    open(src, 'w').write(''.join(out))
    r = subprocess.run(['cc', '-O2', '-w', '-fno-strict-aliasing'] + (['-DRS64_BYTE_WATCH'] if bw else []) + ['-include', force, '-I', incdir,
                        src, '-o', exe], capture_output=True, text=True)
    if r.returncode: sys.exit('compile failed (%s):\n%s' % (tag, r.stderr[:3000]))
    pr = subprocess.run([exe, str(k)], capture_output=True, text=True, env={}); o = pr.stdout
    if pr.returncode: sys.exit('harness %s died rc=%d (last form %s)\n%s' % (tag, pr.returncode, re.findall(r'AT (\d+)', o)[-1:], o[-2000:]))
    rows = {OPS[int(m.group(1))]: tuple(int(m.group(x)) for x in (2, 3, 4)) for m in re.finditer(r'ROW (\d+) n=(\d+) mism=(\d+) stray=(\d+)', o)}
    return rows, o

MUTANTS = [  # name, file ('h' recomp.h / 'f' force header), regex old, new, own ops
    ('MEM_B ^3->^1', 'h', r'(define MEM_B\(offset, reg\) \\\n.*?)\^ 3\)', r'\1^ 1)', {'lb', 'sb'}),
    ('MEM_BU ^3->^1', 'h', r'(define MEM_BU\(offset, reg\) \\\n.*?)\^ 3\)', r'\1^ 1)', {'lbu'}),
    ('MEM_H ^2->^0', 'h', r'(define MEM_H\(offset, reg\) \\\n.*?)\^ 2\)', r'\1^ 0)', {'lh', 'sh'}),
    ('MEM_HU zext->sext', 'h', r'(define MEM_HU\(offset, reg\) \\\n\s*\(\*\()uint16_t', r'\1int16_t', {'lhu'}),
    ('MEM_W sext->zext', 'h', r'(define MEM_W\(offset, reg\) \\\n\s*\(\*\()int32_t', r'\1uint32_t', {'lw'}),
    ('MEM_WU zext->sext', 'f', r'(define MEM_WU\(offset, reg\) \\\n\s*\(\*\()uint32_t', r'\1int32_t', {'lwu'}),
    ('SD hi/lo swap', 'h', r'(define SD\(val, offset, reg\) \{ \\\n.*?\(offset\) )\+ 4(.*?\(offset\) )\+ 0', r'\1+ 0\2+ 4', {'sd', 'sdc1'}),
    ('LD hi/lo swap', 'h', r'MEM_W\(reg, offset \+ 4\);\n(\s*uint64_t hi = .*?)MEM_W\(reg, offset \+ 0\)', r'MEM_W(reg, offset + 0);\n\1MEM_W(reg, offset + 4)', {'ld', 'ldc1'}),
]

def mutant(i, td):
    name, which, old, new, own = MUTANTS[i]
    d = os.path.join(td, 'mut%d' % i); os.makedirs(d, exist_ok=True)
    h = open(os.path.join(INC, 'recomp.h')).read(); f = open(FORCE).read()
    if which == 'h': h, c = re.subn(old, new, h, flags=re.S)
    else: f, c = re.subn(old, new, f, flags=re.S)
    assert c >= 1, name
    open(os.path.join(d, 'recomp.h'), 'w').write(h); open(os.path.join(d, 'force.h'), 'w').write(f)
    return d, os.path.join(d, 'force.h'), c

def kseg1_census():
    lui = re.compile(r'// 0x([0-9A-F]{8}): lui\s+\$\w+, (0x[0-9A-Fa-f]+)')
    fnpat = re.compile(r'^RECOMP_FUNC void (\w+)\(')
    out = collections.defaultdict(collections.Counter)
    for f in sorted(os.listdir(FUNCS)):
        if not f.endswith('.c'): continue
        fn = '?'
        for line in open(os.path.join(FUNCS, f), errors='replace'):
            m = fnpat.match(line)
            if m: fn = m.group(1); continue
            m = lui.search(line)
            if m:
                v = int(m.group(2), 16)
                if 0xA000 <= v <= 0xBFFF:
                    cls = ('kseg1_rdram' if v < 0xA080 else 'kseg1_mmio' if 0xA3F0 <= v < 0xA480 else
                           'pi_rom_0xB0' if v >> 8 == 0xB0 else 'hi_byte_0x%02X' % (v >> 8))
                    out[cls][fn] += 1
    return out

def main():
    k = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    td = tempfile.mkdtemp(prefix='s7413_'); rc = 0
    sites, impure, impure_ex, zbase, zdest, nomatch = harvest()
    tot = collections.Counter(s[0] for s in sites)
    uniq = sorted(set(sites), key=lambda s: (OPID[s[0]], s[5]))
    print('== harvest: %d pure sites, %d distinct forms; %d impure (guarded/gated) sites; %d $zero-dest; %d $zero-base'
          % (len(sites), len(uniq), sum(impure.values()), zdest, len(zbase)))
    for op in OPS: print('  %-5s pure %-6d impure %d' % (op, tot[op], impure[op]))
    print('  operand-mismatch (macro line found but operands differ from disasm): %d' % len(nomatch))
    for x in nomatch[:8]: print('    %s 0x%s %s: %s' % x)
    for op, e in sorted(impure_ex.items()): print('  impure e.g. %s %s 0x%s: %s' % (op, e[0], e[1], e[2]))
    rows, o = build_run(uniq, INC, FORCE, k, 'real', td)
    print('== sweep: real header (RS64_BYTE_WATCH), K=%d cases per form' % k)
    for op in OPS:
        if op in rows and rows[op][0]: print('  %-5s n=%-8d mism=%d stray=%d' % ((op,) + rows[op]))
    for l in o.splitlines():
        if l.startswith(('EX', 'KSEG1')): print('  ' + l)
    if any(r[1] or r[2] for r in rows.values()): rc = 3
    bsites = [s for s in uniq if s[0] in ('lb', 'sb')]
    r2, _ = build_run(bsites, INC, FORCE, k, 'plainB', td, bw=False)
    print('== plain MEM_B (no RS64_BYTE_WATCH): lb n=%d mism=%d, sb n=%d mism=%d' % (r2['lb'][0], r2['lb'][1] + r2['lb'][2], r2['sb'][0], r2['sb'][1] + r2['sb'][2]))
    if r2['lb'][1] + r2['lb'][2] + r2['sb'][1] + r2['sb'][2]: rc = 3
    print('== positive control: mutant headers on a per-op sample (<=400 forms/op)')
    samp = []; per = collections.Counter()
    for s in uniq:
        if per[s[0]] < 400: samp.append(s); per[s[0]] += 1
    ctl = True
    for i, m in enumerate(MUTANTS):
        d, fh, c = mutant(i, td)
        r, _ = build_run(samp, d, fh, max(8, k // 4), 'm%d' % i, td)
        own = sum(r[o_][1] for o_ in m[4] if o_ in r); other = sum(v[1] + v[2] for o_, v in r.items() if o_ not in m[4])
        ownall = all(r.get(o_, (0, 1))[1] > 0 for o_ in m[4] if per[o_])
        ok = own > 0 and ownall and other == 0; ctl &= ok
        print('  %-18s (%d edit) own %s mism=%d, other mism=%d -> %s' % (m[0], c, '/'.join(sorted(m[4])), own, other, 'ok' if ok else 'FAIL'))
    print('CONTROL', 'PASS' if ctl else 'FAIL')
    if not ctl: rc = 3
    print('== $zero-base (absolute 16-bit address = KUSEG 0x0000-0x7FFF or KSEG3 0xFFFF8000+: TLB-mapped on hardware)')
    zf = collections.Counter(z[0] for z in zbase)
    for fn, c in zf.most_common():
        eg = ', '.join(['%s %d @0x%08X' % (z[2], z[3], z[1]) for z in zbase if z[0] == fn][:3])
        print('  %s x%d e.g. %s' % (fn, c, eg))
    print('== lui 0xA000-0xBFFF census (KSEG1 constants)')
    kc = kseg1_census()
    print('  kseg1_rdram (0xA000-0xA07F, the only class the non-aliased mapping could hurt): %d sites' % sum(kc.get('kseg1_rdram', {}).values()))
    for cls, fc in sorted(kc.items()):
        print('  %s: %d sites in %d fns: %s' % (cls, sum(fc.values()), len(fc), ', '.join('%s x%d' % x for x in fc.most_common(6))))
    print('VERDICT', 'H-equal' if rc == 0 else 'MISMATCH')
    shutil.rmtree(td, ignore_errors=True)
    return rc

if __name__ == '__main__':
    sys.exit(main())
