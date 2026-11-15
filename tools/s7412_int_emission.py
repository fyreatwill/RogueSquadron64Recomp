#!/usr/bin/env python3
"""s7412 class BV: integer emission semantics on 64-bit GPRs.
s7085 (tools/s7085_int_test) checked hand-written macro rows per op. This checks every EMITTED site instead:
1. Sweep: every distinct (disassembly operands, emitted C statement) pair for the integer ALU / shift / set / mul-div /
   hi-lo / 64-bit ops in ../N64Recomp/RecompiledFuncs is pasted VERBATIM into one C file, compiled against the real build
   recomp.h (+ forced include/rsp_dpc_macros.h) at -O2, and run on random register files against an independent VR4300
   model (C, written from the manual) driven only by the operands parsed from the disassembly comment.
   Input classes, reported separately per op:
     can  every source register canonical (sign-extended 32-bit), divisors never 0 / never INT_MIN/-1 (defined rows)
     nc   sources random 64-bit. For 64-bit ops (slt/sltu/and/or/dsll...) this is DEFINED behaviour. For 32-bit ops the
          manual leaves it UNDEFINED; the model then uses ares' VR4300 rules (addu: s32(rs.u32+rt.u32), sra: s32(rt.s64>>sa),
          mult: s32 operands) - single-source, informational.
     div0 32-bit div/divu by 0 and div INT_MIN/-1 (C UB in the emitted text; s7085 census says every live site is
          break-7 guarded or constant-divisor - reported, not failed).
     ovf  add/addi/sub/dadd/daddi/dsub rows whose result overflows (hardware traps; emitted code wraps) - reported.
2. Positive control: mutant headers (ADD32 without truncation, S32 zero-extending, SIGNED unsigned) and mutant statement
   texts (sllv '& 31' -> '& 63', dsll32 '+ 32' -> '+ 0') must each show can-class mismatches in the ops they touch.
3. Census: linear per-function dataflow of possibly non-canonical GPR values (producers ld/ldl/ldr/lwu/dsll*/dsrl*/dsra*/
   daddu/daddiu/dsubu/dadd(i)/dsub/dmfc1/mfhi-mflo after a 64-bit mul/div, propagated through and/or/xor/nor/andi/ori/
   xori/movz-like moves) into a 32-bit consumer. Each hit is listed; the sweep's nc row for that op says whether recomp
   agrees with the (ares) hardware model there.
Usage: tools/s7412_int_emission.py [cases_per_stmt]   rc 0 = H-equal (can 0 MISM, nc 0 MISM on 64-bit ops) + CONTROL PASS."""
import os, re, sys, subprocess, tempfile, collections, shutil
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
INC = os.path.join(ROOT, 'lib/N64ModernRuntime/N64Recomp/include')
FORCE = os.path.join(ROOT, 'include/rsp_dpc_macros.h')
FUNCS = os.path.join(ROOT, '../N64Recomp/RecompiledFuncs')

REGS = ['zero', 'at', 'v0', 'v1', 'a0', 'a1', 'a2', 'a3', 't0', 't1', 't2', 't3', 't4', 't5', 't6', 't7',
        's0', 's1', 's2', 's3', 's4', 's5', 's6', 's7', 't8', 't9', 'k0', 'k1', 'gp', 'sp', 'fp', 'ra']
RN = {n: i for i, n in enumerate(REGS)}; RN['s8'] = 30
R3 = 'addu subu and or xor nor slt sltu daddu dsubu dadd dsub add sub'.split()
SHI = 'sll srl sra dsll dsrl dsra dsll32 dsrl32 dsra32'.split()
SHV = 'sllv srlv srav dsllv dsrlv dsrav'.split()
IMM = 'addiu addi slti sltiu andi ori xori daddiu daddi'.split()
MD = 'mult multu div divu dmult dmultu ddiv ddivu'.split()
HL = 'mfhi mflo mthi mtlo'.split()
OPS = R3 + SHI + SHV + IMM + MD + HL + ['lui', 'negu']
OPID = {o: i for i, o in enumerate(OPS)}
W64 = set('and or xor nor slt sltu daddu dsubu dadd dsub dsll dsrl dsra dsll32 dsrl32 dsra32 dsllv dsrlv dsrav andi ori xori '
          'slti sltiu daddiu daddi dmult dmultu ddiv ddivu mfhi mflo mthi mtlo'.split())   # defined on any 64-bit input
OK_ID = set('ctx lo hi result SIGNED ADD32 SUB32 S32 U32 S64 U64 DDIV DDIVU DMULT DMULTU'.split())

def parse_operands(op, s):
    t = [x.strip() for x in s.split(',')]
    reg = lambda x: RN[x.lstrip('$')]
    num = lambda x: int(x, 0)
    rd = rs = rt = imm = sa = 0
    if op in R3: rd, rs, rt = reg(t[0]), reg(t[1]), reg(t[2])
    elif op in SHI: rd, rt, sa = reg(t[0]), reg(t[1]), num(t[2])
    elif op in SHV: rd, rt, rs = reg(t[0]), reg(t[1]), reg(t[2])
    elif op in IMM: rd, rs, imm = reg(t[0]), reg(t[1]), num(t[2])
    elif op in MD:
        if len(t) == 3: t = t[1:]
        rs, rt = reg(t[0]), reg(t[1])
    elif op in ('mfhi', 'mflo'): rd = reg(t[0])
    elif op in ('mthi', 'mtlo'): rs = reg(t[0])
    elif op == 'lui': rd, imm = reg(t[0]), num(t[1])
    elif op == 'negu': rd, rt = reg(t[0]), reg(t[1])
    return rd, rs, rt, imm, sa

def harvest():
    cpat = re.compile(r'^\s*// 0x([0-9A-F]{8}): (\S+)\s+(.*?)\s*$')
    sites = []; impure = collections.Counter(); impure_ex = {}
    for f in sorted(os.listdir(FUNCS)):
        if not f.endswith('.c'): continue
        lines = open(os.path.join(FUNCS, f), errors='replace').read().split('\n')
        for i, line in enumerate(lines):
            m = cpat.match(line)
            if not m or m.group(2) not in OPID: continue
            op = m.group(2)
            try: fields = parse_operands(op, m.group(3))
            except (KeyError, ValueError, IndexError): impure[op] += 1; continue
            stmt = None; first = None; zero = False
            for j in range(i + 1, min(i + 6, len(lines))):
                l = lines[j].strip()
                if cpat.match(lines[j]): break
                if l.startswith('// PATCH: write to $zero'): zero = True; break
                if l.startswith('g_rs64_last_guest_pc') or not l: continue
                if first is None: first = l
                if l.startswith('//') or l.startswith('/*'): continue   # lowering commented out by a fixup patch
                ids = set(re.findall(r'[A-Za-z_]\w*', re.sub(r'\b0[xX][0-9A-Fa-f]+\b|\b\d+\b', ' ', l)))
                ids -= {'r%d' % k for k in range(32)}
                if not (ids - OK_ID) and '{' not in l and 'goto' not in l and '=' in l or l.startswith(('DDIV', 'DMULT')):
                    stmt = l; break        # diagnostic prefixes (bcmp observers, traces) are skipped, the lowering follows
            if stmt is None:
                if zero or (first is None and fields[0] == 0 and op not in MD and op not in ('mthi', 'mtlo')): continue
                impure[op] += 1; impure_ex.setdefault(op, (m.group(1), (first or '')[:120])); continue
            sites.append((op, fields, stmt, int(m.group(1), 16)))
    return sites, impure, impure_ex

C_HEAD = r'''
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include "recomp.h"
uint32_t rs64_ram_top = 0x80800000u;
void rs64_g1d_blk_unaligned(char k, uint32_t a, uint32_t b, uint32_t c) { (void)k; (void)a; (void)b; (void)c; }
void rs64_floor_writer_unaligned(char k, uint32_t a, uint32_t b, uint32_t c) { (void)k; (void)a; (void)b; (void)c; }
typedef void (*tfn)(gpr*, uint64_t*, uint64_t*);
typedef struct { tfn f; int op, rd, rs, rt; int64_t imm; int sa; uint32_t pc; } T;
'''
C_MAIN = r'''
static uint64_t s = 0x9E3779B97F4A7C15ull;
static uint64_t rnd(void) { s ^= s << 13; s ^= s >> 7; s ^= s << 17; return s; }
static int64_t sx(uint64_t v) { return (int64_t)(int32_t)(uint32_t)v; }
static int canon(uint64_t v) { return (uint64_t)sx(v) == v; }
static const uint64_t EDGE[] = {0, 1, 2, 31, 32, 63, 0x7FFF, 0x8000, 0xFFFF, 0x7FFFFFFF, 0xFFFFFFFF80000000ull,
    0xFFFFFFFFFFFFFFFFull, 0xFFFFFFFFFFFF8000ull, 0x10000, 0xFFFFFFFFFFFFFFFEull};
static uint64_t rcan(void) { uint64_t r = rnd(); return (r & 7) == 0 ? EDGE[(r >> 3) % 15] : (uint64_t)sx(rnd() >> (r & 31)) ; }
static uint64_t rnc(void) { uint64_t r = rnd(); return (r & 7) == 0 ? (EDGE[(r >> 3) % 15] ^ (1ull << (32 + (r >> 8) % 32))) : rnd(); }
enum { CAN, NC, DIV0, OVF, NCLS };
/* VR4300 model; returns class override (DIV0/OVF) or -1 */
static int ref(const T* t, uint64_t* R, uint64_t* lo, uint64_t* hi) {
    uint64_t rs = R[t->rs], rt = R[t->rt], v = 0; int w = 1, cls = -1; int64_t im = t->imm;
    switch (t->op) {
#define OPC(name) case OP_##name:
    OPC(addu) v = sx((uint32_t)rs + (uint32_t)rt); break;
    OPC(add) v = sx((uint32_t)rs + (uint32_t)rt); if ((int64_t)sx(rs) + (int64_t)sx(rt) != (int64_t)v) cls = OVF; break;
    OPC(subu) v = sx((uint32_t)rs - (uint32_t)rt); break;
    OPC(sub) v = sx((uint32_t)rs - (uint32_t)rt); if ((int64_t)sx(rs) - (int64_t)sx(rt) != (int64_t)v) cls = OVF; break;
    OPC(negu) v = sx(0u - (uint32_t)rt); break;
    OPC(and) v = rs & rt; break; OPC(or) v = rs | rt; break; OPC(xor) v = rs ^ rt; break; OPC(nor) v = ~(rs | rt); break;
    OPC(slt) v = (int64_t)rs < (int64_t)rt; break; OPC(sltu) v = rs < rt; break;
    OPC(daddu) v = rs + rt; break; OPC(dsubu) v = rs - rt; break;
    OPC(dadd) v = rs + rt; if (__builtin_add_overflow((int64_t)rs, (int64_t)rt, &(int64_t){0})) cls = OVF; break;
    OPC(dsub) v = rs - rt; if (__builtin_sub_overflow((int64_t)rs, (int64_t)rt, &(int64_t){0})) cls = OVF; break;
    OPC(sll) v = sx((uint32_t)rt << t->sa); break;
    OPC(srl) v = sx((uint32_t)rt >> t->sa); break;
    OPC(sra) v = sx((uint64_t)((int64_t)rt >> t->sa)); break;
    OPC(dsll) v = rt << t->sa; break; OPC(dsrl) v = rt >> t->sa; break; OPC(dsra) v = (uint64_t)((int64_t)rt >> t->sa); break;
    OPC(dsll32) v = rt << (t->sa + 32); break; OPC(dsrl32) v = rt >> (t->sa + 32); break;
    OPC(dsra32) v = (uint64_t)((int64_t)rt >> (t->sa + 32)); break;
    OPC(sllv) v = sx((uint32_t)rt << (rs & 31)); break;
    OPC(srlv) v = sx((uint32_t)rt >> (rs & 31)); break;
    OPC(srav) v = sx((uint64_t)((int64_t)rt >> (rs & 31))); break;
    OPC(dsllv) v = rt << (rs & 63); break; OPC(dsrlv) v = rt >> (rs & 63); break;
    OPC(dsrav) v = (uint64_t)((int64_t)rt >> (rs & 63)); break;
    OPC(addiu) v = sx((uint32_t)rs + (uint32_t)(int16_t)im); break;
    OPC(addi) v = sx((uint32_t)rs + (uint32_t)(int16_t)im); if ((int64_t)sx(rs) + (int16_t)im != (int64_t)v) cls = OVF; break;
    OPC(daddiu) v = rs + (uint64_t)(int64_t)(int16_t)im; break;
    OPC(daddi) v = rs + (uint64_t)(int64_t)(int16_t)im; if (__builtin_add_overflow((int64_t)rs, (int64_t)(int16_t)im, &(int64_t){0})) cls = OVF; break;
    OPC(slti) v = (int64_t)rs < (int64_t)(int16_t)im; break;
    OPC(sltiu) v = rs < (uint64_t)(int64_t)(int16_t)im; break;
    OPC(andi) v = rs & (uint16_t)im; break; OPC(ori) v = rs | (uint16_t)im; break; OPC(xori) v = rs ^ (uint16_t)im; break;
    OPC(lui) v = sx((uint32_t)(uint16_t)im << 16); break;
    OPC(mult) { int64_t p = (int64_t)(int32_t)rs * (int64_t)(int32_t)rt; *lo = sx(p); *hi = sx((uint64_t)p >> 32); w = 0; break; }
    OPC(multu) { uint64_t p = (uint64_t)(uint32_t)rs * (uint32_t)rt; *lo = sx(p); *hi = sx(p >> 32); w = 0; break; }
    OPC(div) { int32_t a = (int32_t)rs, b = (int32_t)rt; w = 0;
        if (b == 0) { *lo = a < 0 ? 1 : (uint64_t)-1; *hi = sx(a); cls = DIV0; }
        else if (a == INT32_MIN && b == -1) { *lo = sx(a); *hi = 0; cls = DIV0; }
        else { *lo = sx(a / b); *hi = sx(a % b); } break; }
    OPC(divu) { uint32_t a = (uint32_t)rs, b = (uint32_t)rt; w = 0;
        if (b == 0) { *lo = (uint64_t)-1; *hi = sx(a); cls = DIV0; } else { *lo = sx(a / b); *hi = sx(a % b); } break; }
    OPC(dmult) { __int128 p = (__int128)(int64_t)rs * (int64_t)rt; *lo = (uint64_t)p; *hi = (uint64_t)(p >> 64); w = 0; break; }
    OPC(dmultu) { unsigned __int128 p = (unsigned __int128)rs * rt; *lo = (uint64_t)p; *hi = (uint64_t)(p >> 64); w = 0; break; }
    OPC(ddiv) { int64_t a = (int64_t)rs, b = (int64_t)rt; w = 0;
        if (b == 0) { *lo = a < 0 ? 1 : (uint64_t)-1; *hi = (uint64_t)a; }
        else if ((uint64_t)a == 1ull << 63 && b == -1) { *lo = (uint64_t)a; *hi = 0; }
        else { *lo = (uint64_t)(a / b); *hi = (uint64_t)(a % b); } break; }
    OPC(ddivu) { w = 0; if (rt == 0) { *lo = (uint64_t)-1; *hi = rs; } else { *lo = rs / rt; *hi = rs % rt; } break; }
    OPC(mfhi) v = *hi; break; OPC(mflo) v = *lo; break;
    OPC(mthi) *hi = rs; w = 0; break; OPC(mtlo) *lo = rs; w = 0; break;
    }
    if (w && t->rd) R[t->rd] = v;
    return cls;
}
static const char* CLN[NCLS] = {"can", "nc", "div0", "ovf"};
int main(int argc, char** argv) {
    long n = argc > 1 ? atol(argv[1]) : 256;
    static unsigned long long cnt[NOPS][NCLS], bad[NOPS][NCLS]; static int shown[NOPS][NCLS];
    for (int k = 0; k < NT; k++) {
        const T* t = &TAB[k];
        for (long i = 0; i < n; i++) {
            int want_nc = i & 1;
            uint64_t A[32], B[32], la = rnd(), ha = rnd();
            for (int r = 0; r < 32; r++) A[r] = want_nc ? rnc() : rcan();
            if (!want_nc && (i & 6) == 2 && t->op == OP_div) A[t->rt] = (i & 8) ? 0 : (uint64_t)-1, A[t->rs] = (i & 8) ? A[t->rs] : 0xFFFFFFFF80000000ull;
            if (!want_nc && (i & 6) == 2 && t->op == OP_divu) A[t->rt] = 0;
            if (!want_nc && (t->op == OP_mfhi || t->op == OP_mflo)) { la = sx(la); ha = sx(ha); }
            A[0] = 0;
            for (int r = 0; r < 32; r++) B[r] = A[r];
            uint64_t lb = la, hb = ha;
            int cls = ref(t, A, &la, &ha);
            t->f(B, &lb, &hb); B[0] = 0;
            if (cls < 0) cls = want_nc ? NC : CAN;
            if (want_nc && cls == CAN) cls = NC;
            int diff = lb != la || hb != ha;
            for (int r = 0; r < 32; r++) diff |= A[r] != B[r];
            cnt[t->op][cls]++;
            if (diff) { bad[t->op][cls]++;
                if (shown[t->op][cls]++ < 2) printf("EX %s %s pc=0x%08X rs=%016llx rt=%016llx want rd=%016llx lo=%016llx hi=%016llx got rd=%016llx lo=%016llx hi=%016llx\n",
                    OPN[t->op], CLN[cls], t->pc, (unsigned long long)B[t->rs], (unsigned long long)B[t->rt],
                    (unsigned long long)A[t->rd], (unsigned long long)la, (unsigned long long)ha,
                    (unsigned long long)B[t->rd], (unsigned long long)lb, (unsigned long long)hb); }
            (void)canon;
        }
    }
    for (int o = 0; o < NOPS; o++) for (int c = 0; c < NCLS; c++)
        if (cnt[o][c]) printf("ROW %s %s n=%llu mism=%llu\n", OPN[o], CLN[c], cnt[o][c], bad[o][c]);
    return 0;
}
'''

def gen(uniq, stmt_mut=None):
    out = [C_HEAD]
    out.append('enum {' + ', '.join('OP_%s' % o for o in OPS) + ', NOPS};')
    out.append('static const char* OPN[] = {' + ', '.join('"%s"' % o for o in OPS) + '};')
    tab = []
    for k, (op, f, stmt, pc) in enumerate(uniq):
        body = re.sub(r'ctx->r(\d+)', r'R[\1]', stmt)
        if stmt_mut: body = stmt_mut(op, body)
        out.append('static void t%d(gpr* R, uint64_t* L, uint64_t* H) { uint64_t lo = *L, hi = *H, result = 0; (void)result; %s *L = lo; *H = hi; }' % (k, body))
        rd, rs, rt, imm, sa = f
        tab.append('{t%d, OP_%s, %d, %d, %d, %dll, %d, 0x%08Xu}' % (k, op, rd, rs, rt, imm, sa, pc))
    out.append('static const T TAB[] = {\n' + ',\n'.join(tab) + '};\n#define NT %d' % len(tab))
    out.append(C_MAIN)
    return '\n'.join(out)

def build_run(src_txt, incdir, n, tag, td):
    src = os.path.join(td, tag + '.c'); exe = os.path.join(td, 'x_' + tag)
    open(src, 'w').write(src_txt)
    r = subprocess.run(['cc', '-O2', '-w', '-fno-strict-aliasing', '-include', FORCE, '-I', incdir, src, '-o', exe],
                       capture_output=True, text=True)
    if r.returncode: sys.exit('compile failed (%s):\n%s' % (tag, r.stderr[:3000]))
    out = subprocess.run([exe, str(n)], capture_output=True, text=True).stdout
    rows = {(m.group(1), m.group(2)): (int(m.group(3)), int(m.group(4))) for m in re.finditer(r'ROW (\S+) (\S+) n=(\d+) mism=(\d+)', out)}
    return rows, [l for l in out.splitlines() if l.startswith('EX')]

def hdr_mutant(td, name, old, new):
    d = os.path.join(td, 'm_' + name); os.makedirs(d, exist_ok=True)
    txt = open(os.path.join(INC, 'recomp.h')).read()
    assert old in txt, name
    open(os.path.join(d, 'recomp.h'), 'w').write(txt.replace(old, new, 1))
    return d

PRODUCE = set('ld ldl ldr lld lwu dsll dsll32 dsllv dsrl dsrlv dsra dsrav daddu daddiu dsubu dadd daddi dsub dmfc1'.split())
PROP = set('and or xor nor ori xori'.split())   # andi: zero-extended 16-bit result, always canonical
CONS32 = set('addu addiu subu add addi sub negu sll srl sra sllv srlv srav mult multu div divu'.split())

def census():
    """Linear per-function scan; flags reset at function entry, v0/v1 cleared at calls. Returns hits and counts."""
    cpat = re.compile(r'^\s*// 0x([0-9A-F]{8}): (\S+)\s+(.*?)\s*$'); fnpat = re.compile(r'^(?:__attribute__\(\(weak\)\) )?RECOMP_FUNC void (\w+)\(')  # s7420: weak-aware
    hits = []; prod = collections.Counter(); divs = []
    for f in sorted(os.listdir(FUNCS)):
        if not f.endswith('.c'): continue
        nc = set(); hilo64 = False; fn = '?'
        for line in open(os.path.join(FUNCS, f), errors='replace'):
            m = fnpat.match(line)
            if m: fn = m.group(1); nc = set(); hilo64 = False; continue
            m = cpat.match(line)
            if not m: continue
            pc, op, ops = int(m.group(1), 16), m.group(2), m.group(3)
            t = [x.strip().lstrip('$') for x in re.split(r'[,()]', ops) if x.strip()]
            regs = [RN[x] for x in t if x in RN]
            if op in ('jal', 'jalr'): nc -= {2, 3}; continue
            if op in ('dmult', 'dmultu', 'ddiv', 'ddivu'): hilo64 = True; continue
            if op in ('mult', 'multu', 'div', 'divu'):
                srcs = regs[-2:]
                if op in ('div', 'divu'): divs.append((fn, pc, op, ops))
                if any(r in nc for r in srcs): hits.append((fn, pc, op, ops, [REGS[r] for r in srcs if r in nc]))
                hilo64 = False; continue
            if not regs: continue
            dst = regs[0]
            if dst == 0: continue
            if op in ('mfhi', 'mflo'):
                (nc.add if hilo64 else nc.discard)(dst); continue
            srcs = regs[1:]
            if op in ('sw', 'sd', 'sh', 'sb', 'swl', 'swr', 'sdl', 'sdr', 'mtc1', 'dmtc1', 'beq', 'bne', 'beql', 'bnel',
                      'blez', 'bgtz', 'bltz', 'bgez', 'blezl', 'bgtzl', 'bltzl', 'bgezl', 'jr', 'mthi', 'mtlo', 'sc', 'scd',
                      'tge', 'tne', 'tltu', 'tlt', 'tgeu', 'teq', 'cache', 'mtc0', 'dmtc0', 'ctc1', 'ctc0', 'mtc2', 'swc1',
                      'sdc1', 'swc2', 'sdc2', 'lwc1', 'ldc1', 'lwc2', 'bgezal', 'bltzal'):
                continue
            if op in PRODUCE:
                if op in ('dsrl32',): pass
                nc.add(dst); prod[op] += 1; continue
            if op == 'dsrl32' or op == 'dsra32':
                # dsrl32 sa>=1 and dsra32 any sa yield a canonical value; dsrl32 by 0 may not
                sa = int(t[-1], 0)
                (nc.add if (op == 'dsrl32' and sa == 0) else nc.discard)(dst)
                if op == 'dsrl32' and sa == 0: prod[op] += 1
                continue
            if op in PROP:
                (nc.add if any(r in nc for r in srcs) else nc.discard)(dst); continue
            if op in CONS32 and any(r in nc for r in srcs):
                hits.append((fn, pc, op, ops, [REGS[r] for r in srcs if r in nc]))
            nc.discard(dst)   # every other writer (lw, lui, slt, 32-bit ALU, mfc1 ...) yields a canonical value
    return hits, prod, divs

def div_guards(_divs):
    """Per div/divu site, inside its own function's instruction list (overlays share VRAM, so never look up by PC
    globally): a 'break' within the next 6 insns (IDO/GCC break-7 guard: retail traps before lo/hi are read), or the
    divisor loaded as a nonzero immediate in the previous 3, or neither (= a C-UB divisor-0 hazard to read by hand)."""
    cpat = re.compile(r'^\s*// 0x([0-9A-F]{8}): (\S+)\s+(.*?)\s*$'); fnpat = re.compile(r'^(?:__attribute__\(\(weak\)\) )?RECOMP_FUNC void (\w+)\(')  # s7420: weak-aware
    out = collections.Counter(); bare = []
    def scan(fn, seq):
        for i, (pc, op, ops) in enumerate(seq):
            if op not in ('div', 'divu'): continue
            rt = [x.strip().lstrip('$') for x in ops.split(',')][-1]
            nxa = seq[i + 1:i + 7]; prv = seq[max(0, i - 3):i]
            if any(o == 'break' for _, o, _ in nxa): out['break-guarded'] += 1; continue
            if rt == 'at' or any(o in ('addiu', 'ori', 'addi') and a.split(',')[0].strip().lstrip('$') == rt and '$zero' in a
                                 and not a.rstrip().endswith(' 0x0') for _, o, a in prv):
                out['const-divisor'] += 1; bare.append((fn, pc, op, ops, 'const')); continue
            out['UNGUARDED'] += 1; bare.append((fn, pc, op, ops, 'none'))
    for f in sorted(os.listdir(FUNCS)):
        if not f.endswith('.c'): continue
        fn = None; seq = []; seen = set()
        for line in open(os.path.join(FUNCS, f), errors='replace'):
            m = fnpat.match(line)
            if m:
                if fn: scan(fn, seq)
                fn = m.group(1); seq = []; seen = set(); continue
            m = cpat.match(line)
            if m and fn:
                pc = int(m.group(1), 16)
                if pc in seen: continue        # delay-slot instructions are printed twice
                seen.add(pc); seq.append((pc, m.group(2), m.group(3)))
        if fn: scan(fn, seq)
    return out, bare

def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 256
    sites, impure, impure_ex = harvest()
    seen = {}; per_op = collections.Counter(s[0] for s in sites)
    for s in sites: seen.setdefault((s[0], s[1], s[2]), s)
    uniq = list(seen.values())
    print('== harvest: %d pure sites, %d distinct (operands, statement) forms, %d impure/patched sites skipped' % (len(sites), len(uniq), sum(impure.values())))
    for op, c in sorted(impure.items()): print('  skipped %s x%d e.g. %s' % (op, c, impure_ex.get(op, ('-', 'unparsed'))))
    td = tempfile.mkdtemp(prefix='s7412_')
    rows, ex = build_run(gen(uniq), INC, n, 'real', td)
    print('== sweep: real build header, %d cases per distinct form' % n)
    rc = 0
    for op in OPS:
        r = {c: rows[(op, c)] for c in ('can', 'nc', 'div0', 'ovf') if (op, c) in rows}
        if not r: continue
        print('  %-7s sites=%-6d ' % (op, per_op[op]) + ' '.join('%s %d/%d' % (c, mm, cn) for c, (cn, mm) in r.items()) +
              ('  [nc defined]' if op in W64 else '  [nc undefined: ares model]'))
        if r.get('can', (0, 0))[1]: rc = 3
        if op in W64 and r.get('nc', (0, 0))[1]: rc = 3
    for l in ex[:30]: print('  ' + l)
    print('== positive control')
    muts = [('add32_notrunc', ('hdr', '((gpr)(int32_t)((a) + (b)))', '((gpr)((a) + (b)))'), {'addu', 'addiu'}),
            ('s32_zext', ('hdr', '#define S32(val) \\\n    ((int32_t)(val))', '#define S32(val) \\\n    ((uint32_t)(val))'), {'sll', 'lui', 'mult'}),
            ('signed_unsigned', ('hdr', '#define SIGNED(val) \\\n    ((int64_t)(val))', '#define SIGNED(val) \\\n    ((uint64_t)(val))'), {'slt', 'slti', 'dsra32'}),
            ('sllv_and63', ('stmt', 'sllv', '& 31', '& 63'), {'sllv'}),
            ('dsll32_plus0', ('stmt', 'dsll32', '+ 32', '+ 0'), {'dsll32'})]
    ctl = True
    for name, spec, want in muts:
        if spec[0] == 'hdr':
            txt = open(os.path.join(INC, 'recomp.h')).read()
            if spec[1] not in txt: print('  %s: pattern not in header -> FAIL' % name); ctl = False; continue
            r, _ = build_run(gen(uniq), hdr_mutant(td, name, spec[1], spec[2]), max(16, n // 8), name, td)
        else:
            mop, old, new = spec[1:]
            r, _ = build_run(gen(uniq, lambda op, b: b.replace(old, new) if op == mop else b), INC, max(16, n // 8), name, td)
        hit = {op: r.get((op, 'can'), (0, 0))[1] for op in want}
        ok = all(v > 0 for v in hit.values())
        ctl &= ok
        print('  %s: can-class mism %s -> %s' % (name, hit, 'ok' if ok else 'FAIL'))
    print('CONTROL', 'PASS' if ctl else 'FAIL')
    if not ctl: rc = 3
    hits, prod, divs = census()
    print('== census: possibly non-canonical producers %s' % dict(prod))
    byfn = collections.Counter(h[0] for h in hits)
    print('  %d non-canonical -> 32-bit consumer flows in %d functions' % (len(hits), len(byfn)))
    nxt = {}
    cp = re.compile(r'^\s*// 0x([0-9A-F]{8}): (\S+)\s+(.*?)\s*$')
    for f in sorted(os.listdir(FUNCS)):
        if f.endswith('.c'):
            prev = None
            for line in open(os.path.join(FUNCS, f), errors='replace'):
                m = cp.match(line)
                if not m: continue
                pc = int(m.group(1), 16)
                if prev is not None and pc == prev + 4: nxt.setdefault((f, prev), (m.group(2), m.group(3)))
                if prev is None or pc != prev: prev = pc
    nxt_by_pc = collections.defaultdict(set)
    for (f, pc), v in nxt.items(): nxt_by_pc[pc].add(v)
    masked = 0
    for h in hits:
        fn, pc, op, ops, _ = h
        t = [x.strip().lstrip('$') for x in ops.split(',')]
        ok = False
        if op in ('srl', 'sra', 'sll') and len(t) == 3:
            sa = int(t[2], 0)
            for o, a in nxt_by_pc.get(pc, ()):
                u = [x.strip().lstrip('$') for x in a.split(',')]
                if o == 'andi' and u[0] == u[1] == t[0]:
                    bits = int(u[2], 0).bit_length()
                    ok = (sa + bits <= 32) if op != 'sll' else (bits <= 32)
        masked += ok
        print('  NC %s pc=0x%08X %s %s  (nc src %s) %s' % (h + ('masked-to-low-word: upper-bit independent' if ok else 'UNMASKED: read by hand',)))
    print('  %d/%d flows masked to low-word bits (result independent of bits 63..32 under any VR4300 rule)' % (masked, len(hits)))
    if masked != len(hits): rc = 3
    g, bare = div_guards(divs)
    print('== div/divu divisor-0 guard census: %s' % dict(g))
    for b in bare: print('  DIV %s pc=0x%08X %s %s guard=%s' % b)
    print('VERDICT', 'H-equal' if rc == 0 else 'MISMATCH')
    shutil.rmtree(td, ignore_errors=True)
    return rc

if __name__ == '__main__':
    sys.exit(main())
