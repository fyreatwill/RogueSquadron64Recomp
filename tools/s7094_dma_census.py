#!/usr/bin/env python3
"""s7094: RSP DMA shape census, static + live.

Static: every mtc0 SP_RD_LEN / SP_WR_LEN site in the 3 compiled RSP TUs (count control: RD 6, WR 2, as s7093's C
sections), every DMA-routine call site with the length / DMEM address when it is a literal in the call window, and
every mfc0 of SP_STATUS / SEMAPHORE / DMA_FULL / DMA_BUSY with what RSPRecomp lowers it to.
Live: a build/rs64_s7094.log (ROGUESQ_S7094_DMASHAPE=1, src/rsp/s7094_dma_shape.cpp). A DMEM-bank DMA is a DEFECT when
its shape uses a hardware feature the runtime does not model: mem & 7, raw & 7 != 7, count/skip bits, 4 KB wrap.
(IMEM DMAs are skipped by design; DRAM low 3 bits and bits 24-31 are masked identically by runtime and hardware,
see tools/s7094_dma_test.)  Controls: ctl_count_mask7ff > 0 (detector fires on live raw >= 0x800), imem > 0.
usage: s7094_dma_census.py [LOG]   exit 0 = no defect, 1 = defect shape(s), 2 = a control failed."""
import re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
TUS = ['factor5_ucode_recompiled.c', 'factor5_ucode_b_recompiled.c', 'factor5_boot_recompiled.c']
ASM = re.compile(r'^\s*// ([a-z][a-z0-9.]*)(\s+.*)?$')
LBL = re.compile(r'^([LR]_[0-9A-F]{4}):')
DEFECT = {'mem_lo3', 'len_not7', 'count', 'skip', 'dmem_wrap', 'len_ffffffff'}

def asm_of(path):
    out = []
    for i, l in enumerate(path.read_text().splitlines()):
        m = ASM.match(l)
        if m: out.append((i + 1, (m.group(1) + (m.group(2) or '')).strip()))
        elif LBL.match(l): out.append((i + 1, LBL.match(l).group(1)))
    return out

def static():
    rc = 0; rd = wr = 0
    for tu in TUS:
        a = asm_of(ROOT / 'build/factor5_ucode' / tu)
        lens = {}  # dedupe RSPRecomp delay-slot copies by (previous label, instruction text)
        lab = None; ent = set()
        for k, (n, t) in enumerate(a):
            if t.startswith('L_'): lab = t
            if re.match(r'mtc0\s+\$\w+, SP_(RD|WR)_LEN', t): lens.setdefault((lab, t), n)
            if t.startswith('L_'):
                for _, t2 in a[k + 1:k + 12]:
                    if 'SP_MEM_ADDR' in t2: ent.add(t[2:]); break
                    if t2.startswith('jr'): break
        nrd = sum('RD_LEN' in t for _, t in lens); nwr = sum('WR_LEN' in t for _, t in lens)
        rd += nrd; wr += nwr
        print(f'[static] {tu}: SP_RD_LEN sites {nrd}, SP_WR_LEN sites {nwr}, DMA entries {sorted(ent)}')
        for k, (n, t) in enumerate(a):
            m = re.match(r'(jal|j)\s+(?:0x|L_)([0-9A-F]{4})', t)
            if m and m.group(2) in ent:
                win = [x[1] for x in a[max(0, k - 7):k + 2]]
                lits = [w for w in win if re.match(r'(ori|addiu)\s+\$\d+, \$zero, ', w)]
                print(f'    call L{n:<5} -> {m.group(2)}  literals: {"; ".join(lits) or "-"}')
        st = [t for _, t in a if re.match(r'mfc0\s+\$\w+, SP_(STATUS|SEMAPHORE|DMA_FULL|DMA_BUSY)', t)]
        print(f'    mfc0 SP reads (all lowered to 0 by RSPRecomp): {len(set(st))} distinct forms')
    ok = (rd, wr) == (6, 2)
    print(f'[static] count control RD {rd} WR {wr} (want 6 / 2): {"pass" if ok else "FAIL"}')
    return ok

def live(log):
    L = Path(log).read_text().splitlines()
    tot = [l for l in L if l.startswith('TOT')]; sh = [l for l in L if l.startswith('SH')]
    def f(l, k): return int(re.search(rf'\b{k}=(\d+)', l).group(1))
    ctl = sum(f(l, 'ctl_count_mask7ff') for l in tot); imem = sum(f(l, 'imem') for l in tot); n = sum(f(l, 'n') for l in tot)
    print(f'[live] {log}: {L[0]}; DMAs {n}, shapes {len(sh)}, imem {imem}, ctl {ctl}')
    for l in tot: print('   ', l)
    bad = []
    for l in sh:
        fl = set(re.search(r'flags=(\S*)', l).group(1).strip(',').split(',')) - {''}
        if 'imem' not in fl and fl & DEFECT: bad.append(l)
    for l in bad: print('[live] DEFECT', l)
    ctl_ok = ctl > 0 and imem > 0
    print(f'[live] controls {"pass" if ctl_ok else "FAIL"}; defect shapes {len(bad)}')
    return ctl_ok, bad

if __name__ == '__main__':
    ok = static()
    if len(sys.argv) > 1:
        c, bad = live(sys.argv[1]); ok = ok and c
        sys.exit(2 if not ok else (1 if bad else 0))
    sys.exit(0 if ok else 2)
