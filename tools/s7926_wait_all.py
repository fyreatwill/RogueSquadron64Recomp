#!/usr/bin/env python3
"""s7926: settle s7925's open datum -- does the port skip retail's 8th MusyX wait (flight entry), or take it in < 0.05 ms?
Reads a present ring written with ROGUESQ_PRESENT_RING + ROGUESQ_S7926_WAITALL=1 (src/rsp/s7324_rcp_spill.cpp):
  M <t> ... dur_ms=<d>   slow waits (>= 0.05 ms, s7925)
  m <t> dur_ms=<d>       EVERY completed waitForMusyXAudioTaskDone call (slow ones too)
  m <t> unpaired=1       an entry re-entered before its exit
Positive control (same run): every M row must have an m row at the same entry time with the same duration (the all-call
path demonstrably writes). Then the calls after the last slow wait (+1 s) are listed: none -> SKIPPED, fast ones -> FAST.
Exit 0 = verdict printed, 3 = control failed or no M rows. --selftest runs planted rings."""
import re, sys, os, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from rs64_zopen import zopen
except Exception:
    zopen = open

def analyse(path):
    M, m, unp = [], [], 0
    with zopen(path) as f:
        for l in f:
            if isinstance(l, bytes): l = l.decode('latin-1')
            if l.startswith('M '):
                M.append((float(l.split()[1]), float(re.search(r'dur_ms=([\d.]+)', l).group(1))))
            elif l.startswith('m '):
                if 'unpaired=1' in l: unp += 1; continue
                m.append((float(l.split()[1]), float(re.search(r'dur_ms=([\d.]+)', l).group(1))))
    if not M: return 3, 'no M rows (ring off or no slow wait)'
    hit = sum(1 for t, d in M if any(abs(t - u) < 1e-5 and abs(d - e) < 0.01 for u, e in m))
    if hit != len(M): return 3, 'CONTROL FAIL: %d/%d slow waits have an m row (WAITALL off?)' % (hit, len(M))
    t0 = M[0][0]; last = M[-1][0]
    after = [(t - t0, d) for t, d in m if t > last + 1.0]
    fast = sum(1 for t, d in m if d < 0.05)
    v = 'SKIPPED' if not after else ('FAST' if all(d < 0.05 for _, d in after) else 'SLOW-AFTER')
    det = ' '.join('%.2f:%.4f' % a for a in after[:12])
    return 0, ('s7926 control %d/%d PASS; calls %d (fast %d, unpaired %d); after last slow wait (+%.1f s): %d -> %s %s'
               % (hit, len(M), len(m), fast, unp, last - t0, len(after), v, det)).rstrip()

def selftest():
    def ring(rows):
        fd, p = tempfile.mkstemp(suffix='.txt'); os.write(fd, ''.join(rows).encode()); os.close(fd); return p
    base = ['M 10.000000 pc=0x80091EB0 dur_ms=140.000 fast=0\n', 'm 10.000000 dur_ms=140.0000\n',
            'M 50.000000 pc=0x80091EB0 dur_ms=133.000 fast=0\n', 'm 50.000000 dur_ms=133.0000\n']
    cases = [('skipped', base, 0, 'SKIPPED'), ('fast', base + ['m 60.000000 dur_ms=0.0031\n'], 0, 'FAST'),
             ('nocontrol', [r for r in base if r[0] == 'M'], 3, 'CONTROL FAIL'), ('empty', ['Q 1 x\n'], 3, 'no M')]
    ok = True
    for name, rows, rc, want in cases:
        p = ring(rows); r, s = analyse(p); os.unlink(p)
        good = r == rc and want in s; ok &= good
        print('selftest %-9s %s (rc=%d: %s)' % (name, 'OK' if good else 'BAD', r, s))
    return 0 if ok else 1

if __name__ == '__main__':
    if sys.argv[1:] == ['--selftest']: sys.exit(selftest())
    rc, s = analyse(sys.argv[1]); print(s); sys.exit(rc)
