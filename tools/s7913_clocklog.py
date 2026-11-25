#!/usr/bin/env python3
"""s7913: summarise a ROGUESQ_S7913_CLOCKLOG binary (16-byte records: u32 vi, u32 ra, u32 value-low, u32 kind 0=Count 1=Time).
usage: s7913_clocklog.py clock.bin [--vi LO:HI] [--cmp other.bin]
Prints per-RA call counts (whole run and inside the VI window), and with --cmp the per-RA count difference and the
first record index where the two (vi, ra, value) sequences diverge. Control: --selftest plants one changed value in a
copy of the sequence and requires the divergence to be found at exactly that index."""
import struct, sys, collections
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from rs64_zopen import resolve
import subprocess

def load(p):
    p = resolve(p) or p
    b = subprocess.run(['zstd', '-dc', p], capture_output=True, check=True).stdout if p.endswith('.zst') else open(p, 'rb').read()
    n = len(b) // 16
    return list(struct.iter_unpack('<4I', b[:n * 16]))

def first_div(a, b):
    for i, (x, y) in enumerate(zip(a, b)):
        if x != y:
            return i
    return None if len(a) == len(b) else min(len(a), len(b))

def main(a):
    recs = load(a[0])
    lo, hi = 0, 1 << 32
    if '--vi' in a:
        lo, hi = (int(v) for v in a[a.index('--vi') + 1].split(':'))
    print(f'records={len(recs)} vi_span={recs[0][0] if recs else "-"}..{recs[-1][0] if recs else "-"}')
    tot = collections.Counter((r[1], r[3]) for r in recs)
    win = collections.Counter((r[1], r[3]) for r in recs if lo <= r[0] < hi)
    for (ra, k), c in tot.most_common(40):
        print(f'ra={ra:08X} kind={"Time" if k else "Count"} all={c} win[{lo}:{hi})={win.get((ra, k), 0)}')
    if '--selftest' in a:
        t = list(recs); j = len(t) // 2; t[j] = (t[j][0], t[j][1], t[j][2] ^ 1, t[j][3])
        d = first_div(recs, t); print(f'selftest plant={j} found={d} {"PASS" if d == j else "FAIL"}')
    if '--cmp' in a:
        o = load(a[a.index('--cmp') + 1])
        d = first_div(recs, o)
        print(f'cmp records {len(recs)} vs {len(o)} first_divergence={d}')
        if d is not None and d < min(len(recs), len(o)):
            print('  A', [f'{x:08X}' for x in recs[d]], ' B', [f'{x:08X}' for x in o[d]])
        oc = collections.Counter((r[1], r[3]) for r in o if lo <= r[0] < hi)
        for key in sorted(set(win) | set(oc)):
            if win.get(key, 0) != oc.get(key, 0):
                print(f'  ra={key[0]:08X} kind={key[1]} win A={win.get(key, 0)} B={oc.get(key, 0)}')

if __name__ == '__main__':
    main(sys.argv[1:])
