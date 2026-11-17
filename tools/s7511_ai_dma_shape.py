#!/usr/bin/env python3
"""s7511 class FH: AI DMA shape, our HLE vs the hardware model.

Input: game logs with ROGUESQ_LOG_AI_SHAPE=1 lines
  [ai-shape] n=<k> t=<s> addr=0x<vaddr> len=0x<nbytes> ra=0x<ra> freq=<hz>
(one per guest osAiSetNextBuffer call, logged before the s5063 guard).

Ours (librecomp ai.cpp osAiSetNextBuffer_recomp -> ultramodern::queue_audio_buffer): queue exactly
(nbytes & ~1) bytes from vaddr; the replaced libultra body (retail 0x80029E80) never runs.

Hardware model (retail libultra 0x80029E80 disassembled from the ROM in s7511 + mupen64plus-core
ai_controller.c fifo_push/do_dma + n64brew AI):
  libultra: bptr = vaddr - 0x2000 if hdwrBugFlag; hdwrBugFlag = ((vaddr + nbytes) & 0x1FFF) == 0
            AI_DRAM_ADDR = phys(bptr); AI_LEN = nbytes   (busy -> -1 is never taken by our HLE; assumed not taken)
  AI:       addr = AI_DRAM_ADDR & 0xFFFFF8; len = AI_LEN & 0x3FFF8; a len of 0 plays nothing
            at DMA start: addr += 0x2000 if delayed_carry; delayed_carry = ((addr + len) & 0x1FFF) == 0
Per call EQUAL iff (phys(vaddr), nbytes & ~1) == (addr, len) (len 0 vs 0 counts EQUAL).
Shape canon: vaddr&7 == 0, nbytes&7 == 0, 0 < nbytes < 0x40000, phys < 0x1000000.

rc 0 = all live calls EQUAL, 1 = a live DIFF, 3 = controls fail, 4 = no census lines.
"""
import re
import sys

LINE = re.compile(r'\[ai-shape\] n=(\d+) t=([\d.]+) addr=0x([0-9A-Fa-f]+) len=0x([0-9A-Fa-f]+) ra=0x([0-9A-Fa-f]+) freq=(\d+)')
GUARD = re.compile(r'\[s5065-wrapper-census\] osAiSetNextBuffer calls=(\d+) bad=(\d+)')


def phys(v):
    return v & 0x1FFFFFFF


def shape(v, n):
    if n == 0:
        return 'len0'
    if v & 7:
        return 'addr_mis8'
    if n & 7:
        return 'len_mis8'
    if n >= 0x40000:
        return 'len_big'
    if phys(v) >= 0x1000000:
        return 'addr_hi'
    return 'canon'


def simulate(calls, libultra_flag=True, len_mask=True, carry=True):
    """Return list of (ours, hw) tuples per call."""
    flag = False
    dc = False
    out = []
    for v, n in calls:
        ours = (phys(v), n & ~1) if (n & ~1) else (None, 0)
        b = v
        if libultra_flag:
            if flag:
                b = v - 0x2000
            flag = ((v + n) & 0x1FFF) == 0
        a = phys(b) & 0xFFFFF8 if len_mask else phys(b)
        ln = (n & 0x3FFF8) if len_mask else n
        if ln == 0:
            hw = (None, 0)
        else:
            if carry:
                if dc:
                    a += 0x2000
                dc = ((a + ln) & 0x1FFF) == 0
            hw = (a, ln)
        out.append((ours, hw))
    return out


def classify(calls, **kw):
    shapes = {}
    diffs = {}
    for (v, n), (ours, hw) in zip(calls, simulate(calls, **kw)):
        s = shape(v, n)
        shapes[s] = shapes.get(s, 0) + 1
        if ours != hw:
            diffs[s] = diffs.get(s, 0) + 1
    return shapes, diffs


def controls():
    B = 0x80200000
    cases = [
        # (name, calls, expect_diff)
        ('canon', [(B, 0x5C0), (B + 0x5C0, 0x5C0)], False),
        ('boundary_canon', [(B + 0x2000 - 0x600, 0x600), (B + 0x4000, 0x600), (B + 0x4600, 0x600)], False),
        ('len_mis8', [(B, 0x5C4)], True),
        ('addr_mis8', [(B + 4, 0x5C0)], True),
        ('len_big', [(B, 0x40000)], True),
        ('boundary_len_mis8', [(B + 0x2000 - 0x5FE, 0x5FE), (B + 0x4000, 0x600)], True),
        ('len0', [(B, 0)], False),
    ]
    ok = True
    for name, calls, exp in cases:
        _, d = classify(calls)
        got = bool(d)
        ok &= got == exp
        print(f'  ctl {name}: diff={got} expect={exp} {"ok" if got == exp else "FAIL"}')
    # mutants: drop the libultra flag (boundary_canon must flip to DIFF); drop the AI length mask (len_mis8 must flip to EQUAL)
    _, d = classify(cases[1][1], libultra_flag=False)
    m1 = bool(d)
    _, d = classify(cases[2][1], len_mask=False)
    m2 = not d
    print(f'  mutant no-libultra-flag flips boundary_canon: {m1}; mutant no-len-mask flips len_mis8: {m2}')
    ok &= m1 and m2
    print('controls ' + ('PASS' if ok else 'FAIL') + f' ({len(cases)} synthetic + 2 mutants)')
    return ok


def main(argv):
    rc = 0
    if '--controls' in argv:
        argv = [a for a in argv if a != '--controls']
        if not controls():
            return 3
    for p in argv:
        calls, ts, freqs, ras, guard = [], [], {}, {}, (0, 0)
        ns = []
        bnd = 0
        with open(p, errors='replace') as f:
            for line in f:
                m = LINE.search(line)
                if m:
                    n_, t, a, ln, ra, fq = m.groups()
                    v, n = int(a, 16), int(ln, 16)
                    calls.append((v, n))
                    ns.append(int(n_))
                    ts.append(float(t))
                    freqs[int(fq)] = freqs.get(int(fq), 0) + 1
                    ras[ra] = ras.get(ra, 0) + 1
                    bnd += ((v + n) & 0x1FFF) == 0
                    continue
                g = GUARD.search(line)
                if g:
                    guard = (int(g.group(1)), int(g.group(2)))
        print(f'== {p}')
        if not calls:
            print('   no [ai-shape] lines')
            rc = max(rc, 4)
            continue
        gaps = sum(1 for i in range(1, len(ns)) if ns[i] != ns[i - 1] + 1)
        shapes, diffs = classify(calls)
        lens = {}
        for _, n in calls:
            lens[n] = lens.get(n, 0) + 1
        top = sorted(lens.items(), key=lambda x: -x[1])[:5]
        # completeness: bytes queued per wall second vs freq*4 (stereo s16) over the second half of the run
        half = len(ts) // 2
        span = ts[-1] - ts[half] if len(ts) > 2 else 0
        byts = sum(n for _, n in calls[half + 1:])
        fq = max(freqs, key=freqs.get)
        ratio = (byts / span) / (fq * 4) if span > 0 and fq else 0
        print(f'   calls={len(calls)} n_gaps={gaps} guard_calls/bad={guard[0]}/{guard[1]} shapes={shapes} diffs={diffs}')
        print(f'   boundary_8k_ends={bnd} lens_top={[(hex(a), b) for a, b in top]} ras={ras} freqs={freqs}')
        print(f'   rate_check: bytes/s={byts / span if span else 0:.0f} expected={fq * 4} ratio={ratio:.3f} (2nd half, {span:.0f} s)')
        if diffs:
            rc = max(rc, 1)
            sim = simulate(calls)
            k = 0
            for (v, n), (o, h) in zip(calls, sim):
                if o != h and k < 10:
                    print(f'   DIFF vaddr=0x{v:08X} len=0x{n:X} ours={o} hw={h}')
                    k += 1
    return rc


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
