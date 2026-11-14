#!/usr/bin/env python3
"""s7317: classify every RDRAM word holding a 0x81000000..0x813FFFFF (spill arena) value against the live allocation map.

Inputs: a ROGUESQ_RDRAM_DUMP_DIR directory written with ROGUESQ_RDRAM_DUMP_BYTES=20971520 and ROGUESQ_S7317_ALLOCMAP=1, i.e.
rdram_<swap>_fb*.bin (host order ^3 swizzle: aligned words read as LE u32) + alloc_<swap>.txt ("ptr req caller" per live block,
heap AND spill; optional '#' header lines). Per word: aligned?, value inside a LIVE spill block?, holder inside a live heap block
(owner = that block's caller), in a free/untracked heap area, or below the heap (static data).
Verdict per dump: live_ptr = aligned word -> live spill block (a real holder, needs an owner + field audit); dangling = aligned word
in a LIVE heap block whose value is a spill address no live block covers (a stale pointer a retail compare could still read);
the rest is data (unaligned values, halfword pairs, words in free memory).
--selftest: copies the last dump, plants a live-spill pointer in a live heap block, and checks it is classed live_ptr (control).
Usage: tools/s7317_spill_holders.py <dumpdir> [--selftest] [--all]"""
import bisect, glob, os, re, struct, sys

SPILL_LO, SPILL_HI = 0x81000000, 0x81400000
HEAP_LO = 0x80154690  # s7316: heap head block

def load_alloc(path):
    live, hdr = [], []
    for ln in open(path):
        if ln.startswith('#'): hdr.append(ln.strip()); continue
        f = ln.split()
        if len(f) >= 2: live.append((int(f[0], 16), int(f[1], 16), f[2] if len(f) > 2 else '?'))
    live.sort()
    return live, hdr

def find(live, starts, a):
    i = bisect.bisect_right(starts, a) - 1
    if i >= 0:
        p, n, c = live[i]
        if p <= a < p + max(n, 1): return live[i]
    return None

def classify(r, live):
    starts = [b[0] for b in live]
    spill = [b for b in live if SPILL_LO <= b[0] < SPILL_HI]
    sstarts = [b[0] for b in spill]
    out = {'live_ptr': [], 'dangling': [], 'data_unaligned': 0, 'data_free': 0, 'data_static': 0, 'in_spill': 0}
    n = min(len(r), 0x1400000) & ~3
    words = struct.unpack_from('<%dI' % (n // 4), r, 0)
    for i, v in enumerate(words):
        if not (SPILL_LO <= v < SPILL_HI): continue
        a = 0x80000000 + i * 4
        if SPILL_LO <= a < SPILL_HI: out['in_spill'] += 1; tgt_self = True
        tgt = find(spill, sstarts, v)
        own = find(live, starts, a)
        if tgt is not None:
            out['live_ptr'].append((a, v, own, tgt)); continue
        if v & 3: out['data_unaligned'] += 1; continue
        if own is not None and not (SPILL_LO <= a < SPILL_HI): out['dangling'].append((a, v, own)); continue
        if a < HEAP_LO: out['data_static'] += 1
        else: out['data_free'] += 1
    return out

def dumps(d):
    for b in sorted(glob.glob(os.path.join(d, 'rdram_*.bin'))):
        sw = re.search(r'rdram_(\d+)_', b).group(1)
        a = os.path.join(d, 'alloc_%s.txt' % sw)
        if os.path.exists(a): yield sw, b, a

def main():
    args = [x for x in sys.argv[1:] if not x.startswith('--')]
    d = args[0]
    allv = '--all' in sys.argv
    tot_live = tot_dang = 0
    owners = {}
    last = None
    for sw, b, a in dumps(d):
        live, hdr = load_alloc(a)
        r = open(b, 'rb').read()
        o = classify(r, live)
        nsp = sum(1 for p, _, _ in live if SPILL_LO <= p < SPILL_HI)
        print('swap %s live_blocks=%d live_spill=%d live_ptr=%d dangling=%d unaligned=%d free=%d static=%d in_spill=%d %s' % (
            sw, len(live), nsp, len(o['live_ptr']), len(o['dangling']), o['data_unaligned'], o['data_free'], o['data_static'],
            o['in_spill'], ' '.join(hdr)))
        for a_, v, own, *t in o['live_ptr'] + o['dangling']:
            k = ('LIVE' if t else 'DANG', own[2] if own else '-', own[1] if own else 0, (a_ - own[0]) if own else -1)
            owners.setdefault(k, set()).add(sw)
            if allv: print('   %s %08X=%08X owner=%s' % (k[0], a_, v, ('%08X+0x%X sz=0x%X caller=%s' % (own[0], a_ - own[0], own[1], own[2])) if own else '-'))
        tot_live += len(o['live_ptr']); tot_dang += len(o['dangling'])
        last = (sw, b, live, r)
    print('owner fields (kind, caller, block size, field offset) -> dumps:')
    for k, v in sorted(owners.items(), key=lambda kv: -len(kv[1])): print('  %s caller=%s sz=0x%X off=0x%X in %d dumps' % (k[0], k[1], k[2], k[3], len(v)))
    print('TOTAL live_ptr=%d dangling=%d' % (tot_live, tot_dang))
    if '--selftest' in sys.argv and last:
        sw, b, live, r = last
        heap = [x for x in live if HEAP_LO <= x[0] < SPILL_LO and x[1] >= 8]
        fake_spill = (0x81000040, 0x40, 'selftest')
        live2 = sorted(live + [fake_spill])
        rb = bytearray(r); h = heap[len(heap) // 2]; off = (h[0] - 0x80000000 + 4) & ~3
        struct.pack_into('<I', rb, off, 0x81000050)
        o = classify(bytes(rb), live2)
        hit = [x for x in o['live_ptr'] if x[0] == 0x80000000 + off and x[2] and x[2][0] == h[0]]
        print('SELFTEST planted %08X=81000050 in block %08X: %s' % (0x80000000 + off, h[0], 'PASS' if hit else 'FAIL'))
        if not hit: return 2
    return 1 if tot_live else 0

if __name__ == '__main__':
    sys.exit(main())
