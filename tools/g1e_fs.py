#!/usr/bin/env python3
"""s6708 G1e: per-arm State::fullSync segment split.

Joins [s4267] per-second phase aggregates (ROGUESQ_S4267=1) with [g1e-aq] per-second
arm tags (as=0 sync, 1 async end-commit, 2 async streamed) from ONE run under
ROGUESQ_RDP_ASYNC_TOGGLE. Seconds carrying more than one arm (toggle edges) and
seconds before --tmin are dropped. Prints ms per fullSync call for every segment;
positive control: the time-ordered segments (10..18) sum to the fullSync total (4).
usage: g1e_fs.py run.log [--tmin 140]
"""
import re, sys, collections
log = sys.argv[1]
tmin = int(sys.argv[sys.argv.index('--tmin') + 1]) if '--tmin' in sys.argv else 140
# Time-ordered top-level segments of State::fullSync (_seg.mark order: 10,11,12,13,19,14,22,23,24,15,16,17,18).
# fsMisc(10) = dispatch+flush+submitFramebufferPair (sub: fsFlush 8, fsSubmitFb 9); fsRsz(19) = pre-render setup;
# fsRender(14) = fb-pair loop (sub: fsTiles 20, fsRenderSync 21); waits 0..3 nest inside these.
SEQ = ['fsMisc', 'fsValidate', 'fsUpload', 'fsRspPipe', 'fsRsz', 'fsRender', 'fsEvictOnly', 'fsPostEvict',
       'fsScript', 'fsEvict', 'fsProj', 'fsAdvance', 'fsTail']
arms = collections.defaultdict(set)
s4 = {}
for ln in open(log, errors='replace'):
    if ln.startswith('[g1e-aq]'):
        m = re.match(r'\[g1e-aq\] t=(\d+) as=(\d)', ln)
        arms[int(m.group(1))].add(int(m.group(2)))
    elif ln.startswith('[s4267]'):
        t = int(re.match(r'\[s4267\] t=(\d+)', ln).group(1))
        s4[t] = {k: (int(n), float(s)) for k, n, s in re.findall(r' (\w+)=(\d+)/([\d.]+)ms', ln)}
acc = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0.0]))
secs = collections.Counter()
for t, ph in s4.items():
    a = arms.get(t, set()) | arms.get(t - 1, set()) | arms.get(t + 1, set())  # clocks differ by <1 s
    if t < tmin or len(a) != 1:
        continue
    arm = a.pop(); secs[arm] += 1
    for k, (n, s) in ph.items():
        acc[arm][k][0] += n; acc[arm][k][1] += s
names = None
for arm in sorted(acc):
    d = acc[arm]; nfs = d['fullSync'][0] or 1
    print(f'arm as={arm} secs={secs[arm]} fullSync n/s={nfs / secs[arm]:.1f} ms/fullSync={d["fullSync"][1] / nfs:.3f}')
    print(f'   control: sum(top-level segs)={sum(d[k][1] for k in SEQ) / nfs:.3f} ms/fullSync')
    rows = sorted(((v[1] / nfs, k, v[0] / nfs) for k, v in d.items() if v[1] > 0), reverse=True)
    for ms, k, calls in rows:
        print(f'   {k:14s} {ms:7.3f} ms/fullSync  calls/fullSync={calls:.2f}')
