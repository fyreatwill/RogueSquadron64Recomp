#!/usr/bin/env python3
"""s7873 G3: the value timeSnapshotFiller actually stores (a0+0x20), per game frame, from a retail rs64_oracle log.

timeSnapshotFiller (0x8000BC00) stores at 0x8000BF3C (delay slot of the jal at BF38):
    prev == -1                 -> 0
    flags 0x8011A8C8/C9 clear  -> 0x8011A904 / rate                    (BEE8 path)
    else                       -> el/rate + getViModePeriod()*0.001 * (vd < 2 ? 1 : vd)
with el = stamp 0x80128ED8 - prev 0x8011A900 (v0 at BE28) and vd = byte 0x80128EAF - byte 0x80128EAE. There is NO el == 0 special
case (s7872's guess); ROGUESQ_RETAIL_SNAP pins el=811160 AND the vd branch to 1, so the port stores el/rate + 1 VI = 0.03397 on
every frame, while retail stores 0.01667 (el 0, vd<2), 0.03333 (el 0, vd 2) or 0.03397 (el 1 VI).
Oracle recipe: RS64_ORACLE_FPR=0,2,4,20 + `--watch-pc 0x8000BF38` (f0 at that hit = the stored value; BE88 is a delay slot and
never fires as a watch). Prints run-lengths of the value class with the hit index and emulated time.
Control (iron rule 1): rc 3 unless at least two distinct non-zero classes are seen (an instrument that saw one value cannot
report "constant").
usage: s7873_snap_value.py ORACLE.log [--from IDX]
"""
import re, struct, sys
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from rs64_zopen import zopen


def cls(v):
    for name, ref in (('0', 0.0), ('1VI', 1 / 60), ('2VI', 2 / 60), ('el1VI+1VI', 0.033971), ('3VI', 3 / 60)):
        if abs(v - ref) < 2e-5:
            return name
    return f'{v:.6f}'


def main():
    a = sys.argv[1:]
    if not a:
        print(__doc__); return 2
    lo = int(a[a.index('--from') + 1]) if '--from' in a else 0
    vals = []
    with zopen(a[0]) as fh:
        for ln in fh:
            if isinstance(ln, bytes): ln = ln.decode(errors='replace')
            if ln.startswith('[hit] x') and 'pc=0x8000bf38' in ln:
                m = re.search(r'f0=([0-9a-f]{8})', ln); t = re.search(r' t=([\d.]+)s', ln)
                if m: vals.append((float(t.group(1)) if t else -1, struct.unpack('>f', bytes.fromhex(m.group(1)))[0]))
    runs, prev = [], None
    for i, (t, v) in enumerate(vals):
        c = cls(v)
        if c != prev: runs.append([i, 0, c, t]); prev = c
        runs[-1][1] += 1
    print(f'stores {len(vals)}  runs {len(runs)}')
    for i, n, c, t in runs:
        if i + n > lo: print(f'  idx {i:5d} n {n:4d} t {t:6.1f}s  {c}')
    tally = {}
    for _, v in vals: tally[cls(v)] = tally.get(cls(v), 0) + 1
    print('classes', sorted(tally.items(), key=lambda x: -x[1])[:8])
    nz = [c for c in tally if c != '0']
    if len(nz) < 2:
        print('CONTROL FAIL: fewer than two non-zero value classes'); return 3
    print('CONTROL PASS'); return 0


if __name__ == '__main__':
    sys.exit(main())
