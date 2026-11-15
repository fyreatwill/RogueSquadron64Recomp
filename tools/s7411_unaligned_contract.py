#!/usr/bin/env python3
"""s7411 class BU: unaligned load/store macro contract (recomp.h do_lwl/do_lwr/do_swl/do_swr/do_ldl/do_ldr/do_sdl/do_sdr).
The recomp rdram is word-swizzled (guest byte a lives at host byte a^3; a guest word is one native uint32), so every
macro has to re-derive big-endian VR4300 semantics per (addr & 3 / & 7).
1. Sweep: the REAL build header (lib/N64ModernRuntime/N64Recomp/include/recomp.h + the force-included
   include/rsp_dpc_macros.h, included verbatim, not transcribed; its swl/swr/sdl/sdr diagnostic observers are stubbed)
   compiled at -O2, vs an independent BYTE-WISE model written from the VR4300 manual over a plain big-endian byte array
   (LWL: bytes addr..end-of-word -> register lanes from the MSB down; LWR: bytes start-of-word..addr -> lanes from the LSB
   up; 32-bit result sign-extended into the 64-bit GPR; SWL/SWR the mirror image; LDL/LDR/SDL/SDR the same on dwords).
   N random cases per macro (random register, random 64-byte memory image, every misalignment), plus the pair identities
   lwl(a)+lwr(a+3) == sign-extended unaligned BE word and swl(a)+swr(a+3) == unaligned BE word store, and the bytes
   outside the touched word must be unchanged.
2. Positive control: for each macro a mutant header (that macro's misalignment computed as m ^ (m==2), i.e. lanes 2/3
   swapped) must show MISM > 0, and the untouched macros must stay MISM 0.
3. Census of emitted sites in ../N64Recomp/RecompiledFuncs: per op, paired (lwl k / lwr k+3, same rt, same base, within 4
   insns, either order; same for swl/swr) vs lone; lone sites listed with PC + function.
Usage: tools/s7411_unaligned_contract.py [N]   rc 0 = H-equal (0 MISM everywhere) + control PASS, rc 3 otherwise."""
import os, re, sys, subprocess, tempfile, collections, shutil
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
INC = os.path.join(ROOT, 'lib/N64ModernRuntime/N64Recomp/include')
FORCE = os.path.join(ROOT, 'include/rsp_dpc_macros.h')
FUNCS = os.path.join(ROOT, '../N64Recomp/RecompiledFuncs')
OPS = ['lwl', 'lwr', 'swl', 'swr', 'ldl', 'ldr', 'sdl', 'sdr']

C = r'''
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "recomp.h"
uint32_t rs64_ram_top = 0x80800000u;
void rs64_g1d_blk_unaligned(char k, uint32_t a, uint32_t b, uint32_t c) { (void)k; (void)a; (void)b; (void)c; }
void rs64_floor_writer_unaligned(char k, uint32_t a, uint32_t b, uint32_t c) { (void)k; (void)a; (void)b; (void)c; }
#define MEMSZ 64
static uint8_t host[MEMSZ];   /* swizzled rdram window: guest byte a at host[a ^ 3] */
static uint8_t be[MEMSZ];     /* reference: plain big-endian guest bytes */
static uint64_t s = 0x9E3779B97F4A7C15ull;
static uint64_t rnd(void) { s ^= s << 13; s ^= s >> 7; s ^= s << 17; return s; }
static void fill(void) { for (int i = 0; i < MEMSZ; i++) { be[i] = (uint8_t)rnd(); host[i ^ 3] = be[i]; } }
static int same(void) { for (int i = 0; i < MEMSZ; i++) if (host[i ^ 3] != be[i]) return 0; return 1; }
#define GBASE 0xFFFFFFFF80000000ull
static uint8_t lane(uint64_t r, int i) { return (uint8_t)(r >> (8 * i)); }
static uint64_t setlane(uint64_t r, int i, uint8_t b) { return (r & ~(0xFFull << (8 * i))) | ((uint64_t)b << (8 * i)); }
static uint64_t sx32(uint64_t r) { return (uint64_t)(int64_t)(int32_t)(uint32_t)r; }
/* VR4300 byte-wise models (big-endian) */
static uint64_t ref_lwl(uint64_t rt, int a) { int w = a & ~3; for (int j = 0; a + j <= w + 3; j++) rt = setlane(rt, 3 - j, be[a + j]); return sx32(rt); }
static uint64_t ref_lwr(uint64_t rt, int a) { int w = a & ~3; for (int j = 0; a - j >= w; j++) rt = setlane(rt, j, be[a - j]); return sx32(rt); }
static void ref_swl(uint64_t rt, int a) { int w = a & ~3; for (int j = 0; a + j <= w + 3; j++) be[a + j] = lane(rt, 3 - j); }
static void ref_swr(uint64_t rt, int a) { int w = a & ~3; for (int j = 0; a - j >= w; j++) be[a - j] = lane(rt, j); }
static uint64_t ref_ldl(uint64_t rt, int a) { int w = a & ~7; for (int j = 0; a + j <= w + 7; j++) rt = setlane(rt, 7 - j, be[a + j]); return rt; }
static uint64_t ref_ldr(uint64_t rt, int a) { int w = a & ~7; for (int j = 0; a - j >= w; j++) rt = setlane(rt, j, be[a - j]); return rt; }
static void ref_sdl(uint64_t rt, int a) { int w = a & ~7; for (int j = 0; a + j <= w + 7; j++) be[a + j] = lane(rt, 7 - j); }
static void ref_sdr(uint64_t rt, int a) { int w = a & ~7; for (int j = 0; a - j >= w; j++) be[a - j] = lane(rt, j); }
int main(int argc, char** argv) {
    long n = argc > 1 ? atol(argv[1]) : 1000000;
    uint8_t* rdram = host;
    unsigned long long mism[10] = {0}, cnt[10] = {0}, perm[8][8] = {{0}};
    const char* nm[10] = {"lwl","lwr","swl","swr","ldl","ldr","sdl","sdr","pair_lw","pair_sw"};
    for (long i = 0; i < n; i++) {
        uint64_t rt = rnd(), off = rnd() & 0xF; int op = (int)(i % 10);
        int a = 16 + (int)(rnd() % 24);              /* guest byte addr inside the window, room for +/-8 */
        gpr reg = GBASE + (uint64_t)(a - (int)off);  /* emitted call shape: do_x(rdram, [rt,] base, imm) */
        fill(); cnt[op]++; int bad = 0;
        switch (op) {
        case 0: bad = do_lwl(rdram, rt, reg, off) != ref_lwl(rt, a); break;
        case 1: bad = do_lwr(rdram, rt, reg, off) != ref_lwr(rt, a); break;
        case 2: do_swl(rdram, off, reg, rt); ref_swl(rt, a); bad = !same(); break;
        case 3: do_swr(rdram, off, reg, rt); ref_swr(rt, a); bad = !same(); break;
        case 4: bad = do_ldl(rdram, rt, reg, off) != ref_ldl(rt, a); break;
        case 5: bad = do_ldr(rdram, rt, reg, off) != ref_ldr(rt, a); break;
        case 6: do_sdl(rdram, off, reg, rt); ref_sdl(rt, a); bad = !same(); break;
        case 7: do_sdr(rdram, off, reg, rt); ref_sdr(rt, a); bad = !same(); break;
        case 8: { /* ulw: lwl a, lwr a+3 (both orders) == sign-extended BE word at a */
            uint64_t want = sx32(((uint64_t)be[a] << 24) | ((uint64_t)be[a+1] << 16) | ((uint64_t)be[a+2] << 8) | be[a+3]);
            uint64_t r1 = do_lwr(rdram, do_lwl(rdram, rt, reg, off), reg, off + 3);
            uint64_t r2 = do_lwl(rdram, do_lwr(rdram, rt, reg, off + 3), reg, off);
            bad = r1 != want || r2 != want; break; }
        case 9: { /* usw: swl a, swr a+3 == BE word store at a, nothing else touched */
            do_swl(rdram, off, reg, rt); do_swr(rdram, off + 3, reg, rt);
            for (int j = 0; j < 4; j++) be[a + j] = lane(rt, 3 - j);
            bad = !same(); break; }
        }
        if (op < 8) perm[op][a & 7] += bad;
        if (bad) mism[op]++;
    }
    for (int k = 0; k < 10; k++) printf("ROW %s n=%llu mism=%llu\n", nm[k], cnt[k], mism[k]);
    for (int k = 0; k < 8; k++) { printf("BYM %s", nm[k]); for (int m = 0; m < 8; m++) printf(" %llu", perm[k][m]); printf("\n"); }
    return 0;
}
'''

def build_run(incdir, n, tag, td):
    src = os.path.join(td, 'h.c'); exe = os.path.join(td, 'h_' + tag)
    open(src, 'w').write(C)
    r = subprocess.run(['cc', '-O2', '-w', '-fno-strict-aliasing', '-include', FORCE, '-I', incdir, src, '-o', exe],
                       capture_output=True, text=True)
    if r.returncode: sys.exit('compile failed (%s):\n%s' % (tag, r.stderr[:2000]))
    out = subprocess.run([exe, str(n)], capture_output=True, text=True).stdout
    rows = {m.group(1): (int(m.group(2)), int(m.group(3))) for m in re.finditer(r'ROW (\S+) n=(\d+) mism=(\d+)', out)}
    return rows, out

def mutant(op, td):
    d = os.path.join(td, 'mut_' + op); os.makedirs(d, exist_ok=True)
    txt = open(os.path.join(INC, 'recomp.h')).read()
    m = re.search(r'static inline \w+ do_%s\(.*?\n}\n' % op, txt, re.S)
    body = m.group(0)
    mask = '0x7' if op[1] == 'd' else '0x3'
    old = 'gpr misalignment = address & %s;' % mask
    assert old in body, op
    new = body.replace(old, 'gpr misalignment = (address & %s) ^ ((address & %s) == 2);' % (mask, mask))
    open(os.path.join(d, 'recomp.h'), 'w').write(txt.replace(body, new))
    return d

def census():
    pat = re.compile(r'// 0x([0-9A-F]{8}): (lwl|lwr|swl|swr|ldl|ldr|sdl|sdr)\s+\$(\w+), (-?0x[0-9A-F]+|\d+)\(\$(\w+)\)', re.I)
    fnpat = re.compile(r'^RECOMP_FUNC void (\w+)\(')
    sites = []  # (fn, idx, pc, op, rt, off, base)
    for f in sorted(os.listdir(FUNCS)):
        if not f.endswith('.c'): continue
        fn = '?'; idx = 0
        for line in open(os.path.join(FUNCS, f), errors='replace'):
            m = fnpat.match(line)
            if m: fn = m.group(1); idx = 0; continue
            if '// 0x' in line:
                idx += 1
                m = pat.search(line)
                if m: sites.append((fn, idx, int(m.group(1), 16), m.group(2).lower(), m.group(3), int(m.group(4), 0), m.group(5)))
    partner = {'lwl': ('lwr', 3), 'lwr': ('lwl', -3), 'swl': ('swr', 3), 'swr': ('swl', -3),
               'ldl': ('ldr', 7), 'ldr': ('ldl', -7), 'sdl': ('sdr', 7), 'sdr': ('sdl', -7)}
    byfn = collections.defaultdict(list)
    for s in sites: byfn[s[0]].append(s)
    tot = collections.Counter(); paired = collections.Counter(); lone = []
    for fn, ss in byfn.items():
        for s in ss:
            tot[s[3]] += 1
            po, d = partner[s[3]]
            ok = any(t[3] == po and t[4] == s[4] and t[6] == s[6] and t[5] == s[5] + d and abs(t[1] - s[1]) <= 4 for t in ss)
            if ok: paired[s[3]] += 1
            else: lone.append(s)
    return tot, paired, lone

def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 10000000
    td = tempfile.mkdtemp(prefix='s7411_')
    rc = 0
    rows, out = build_run(INC, n, 'real', td)
    print('== sweep: real build header, %d cases (~%d per row)' % (n, n // 10))
    for k, (c, mm) in rows.items(): print('  %-8s n=%-9d mism=%d' % (k, c, mm))
    for l in out.splitlines():
        if l.startswith('BYM') and any(int(x) for x in l.split()[2:]): print('  ' + l)
    if any(mm for _, mm in rows.values()): rc = 3
    print('== positive control: lane-2/3-swap mutant per macro')
    ctl = True
    for op in OPS:
        r, _ = build_run(mutant(op, td), n // 4, op, td)
        hit = r[op][1]; others = sum(mm for k, (c, mm) in r.items() if k != op and not k.startswith('pair'))
        ok = hit > 0 and others == 0
        ctl &= ok
        print('  mut_%s: own mism=%d, other-macro mism=%d -> %s' % (op, hit, others, 'ok' if ok else 'FAIL'))
    print('CONTROL', 'PASS' if ctl else 'FAIL')
    if not ctl: rc = 3
    tot, paired, lone = census()
    print('== census (../N64Recomp/RecompiledFuncs)')
    for op in OPS:
        if tot[op]: print('  %s: %d sites, %d paired, %d lone' % (op, tot[op], paired[op], tot[op] - paired[op]))
    for s in lone[:40]: print('  LONE %s pc=0x%08X %s $%s, %d($%s)' % (s[0], s[2], s[3], s[4], s[5], s[6]))
    print('VERDICT', 'H-equal' if rc == 0 else 'MISMATCH')
    shutil.rmtree(td, ignore_errors=True)
    return rc

if __name__ == '__main__':
    sys.exit(main())
