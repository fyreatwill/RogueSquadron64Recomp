#!/usr/bin/env python3
"""s7769: game frames/s from a present ring (ROGUESQ_PRESENT_RING) - counts gen= changes per window, no G3C_LOG needed.
usage: s7769_ring_genrate.py <ring.txt> [win_s=5] [from_s=70] [slow=45]
Prints SUMMARY windows= slow_windows= min_rate= first_slow_t=. Positive control: scratch/s7749_soak/ring_u124.txt (L12 drop from t~75 s)
must report slow_windows>0; a ring with no Q lines exits 3."""
import re, sys, collections
p = sys.argv[1]; W = float(sys.argv[2]) if len(sys.argv) > 2 else 5.0
F = float(sys.argv[3]) if len(sys.argv) > 3 else 70.0; SLOW = float(sys.argv[4]) if len(sys.argv) > 4 else 45.0
q = re.compile(r'^Q ([\d.]+) .* gen=(\d+)')
t0 = None; last = None; bins = collections.Counter(); seen = set()
for l in open(p, encoding='latin-1'):
    m = q.match(l)
    if not m: continue
    t = float(m.group(1)); g = int(m.group(2))
    if t0 is None: t0 = t
    k = int((t - t0) // W); seen.add(k)
    if last is not None and g != last: bins[k] += 1
    last = g
if t0 is None: print('SUMMARY no Q lines'); sys.exit(3)
ks = [k for k in sorted(seen) if k * W >= F][:-1]  # drop the partial last window
rates = [(k * W, bins[k] / W) for k in ks]
slow = [r for r in rates if r[1] < SLOW]
for t, r in rates: print(f't {t:6.0f} gen/s={r:5.1f}{"  SLOW" if r < SLOW else ""}')
print(f'SUMMARY windows={len(rates)} slow_windows={len(slow)} min_rate={min((r for _, r in rates), default=float("nan")):.1f} '
      f'first_slow_t={slow[0][0] if slow else "none"}')
