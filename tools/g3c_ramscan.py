#!/usr/bin/env python3
"""s6320: find smoothly-moving float triples across RDRAM snapshots. Usage: g3c_ramscan.py SNAPDIR [skip_first=5]
Candidate word: finite, |v|<1e6, changes in >=60% of snapshot pairs, max step < 5% of range+1e2, not monotonic-const.
Reports top aligned triples (a,a+4,a+8) where >=2 words qualify, ranked by total travel."""
import sys, glob, numpy as np
d = sys.argv[1]; skip = int(sys.argv[2]) if len(sys.argv) > 2 else 5
fs = sorted(glob.glob(d + '/snap_*.bin'))[skip:]
print(len(fs), 'snapshots')
S = np.stack([np.fromfile(f, dtype='<f4') for f in fs]).astype(np.float64)  # [n, words]
ok = np.isfinite(S).all(0) & (np.abs(S) < 1e6).all(0)
dS = np.abs(np.diff(S, axis=0)); rng = S.max(0) - S.min(0)
chg = (dS > 1e-3).mean(0)
smooth = ok & (chg >= 0.6) & (rng > 1.0) & (dS.max(0) < 0.5 * rng + 1e-9) & (rng < 1e5)
# monotone-ish (steady flight => position drifts consistently)
sg = np.sign(np.diff(S, axis=0)); mono = np.abs(sg.mean(0)) >= 0.7
cand = smooth & mono
idx = np.where(cand)[0]; print('candidate words', len(idx))
cs = set(idx.tolist()); out = []
for w in idx:
    if w + 1 in cs and w + 2 in cs:
        out.append((rng[w] + rng[w+1] + rng[w+2], w))
out.sort(reverse=True)
for r, w in out[:25]:
    print('addr 0x%08X travel x%.1f y%.1f z%.1f  first=%s' % (0x80000000 + 4*w, rng[w], rng[w+1], rng[w+2], S[0, w:w+3].round(1)))
if not out:
    for w in idx[:30]: print('word 0x%08X rng %.1f' % (0x80000000 + 4*w, rng[w]))
