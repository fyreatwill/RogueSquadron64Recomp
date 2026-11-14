#!/usr/bin/env python3
"""s7330 report: pair every audio DMA that lands in a freed guest block with the audio task that issued it and the free.
Input: build/rs64_s7330.log (ROGUESQ_S7324_RCPREF=ctl + ROGUESQ_S7317_ALLOCMAP=1). Per hit task: submitted after the free
(H-next-task: the synth built a command list over freed memory) or before it (in flight: the guest freed while the RSP ran).
bulk=1 = no host freer frames (retail scene bulk free coalesceFreeHeapBlocks), bulk=0 = rs_free. Exit 1 on a failed control
(every audio DMA must attribute to a submitted task: noseq=late=neg=0) or an unattributable hit."""
import re, sys
from collections import defaultdict
path = sys.argv[1] if len(sys.argv) > 1 else 'build/rs64_s7330.log'
T, H, W, ctl = {}, [], [], {}
for l in open(path):
    d = dict(re.findall(r'(\w+)=(\S+)', l))
    if l.startswith('s7330 ctl'): ctl = d
    elif l.startswith('TASK'): T[int(d['seq'])] = d
    elif l.startswith('HIT'): H.append(d)
    elif l.startswith('WAIT'): W.append((float(d['t']), d['edge']))
bad = any(int(ctl.get(k, 1)) for k in ('noseq', 'late', 'neg'))
print('ctl aud_dma=%s attr_ok=%s noseq=%s late=%s neg=%s -> %s' % (ctl.get('aud_dma'), ctl.get('attr_ok'), ctl.get('noseq'),
      ctl.get('late'), ctl.get('neg'), 'FAIL' if bad else 'PASS'))
grp = defaultdict(list)
for h in H: grp[(h['ft'][:12], h['bulk'])].append(h)
for (ft_s, bulk), hs in sorted(grp.items()):
    ft = float(hs[0]['ft']); seqs = sorted({int(h['seq']) for h in hs})
    print('free t=%s bulk=%s hits=%d (rd %d wr %d) blocks=%s' % (ft_s, bulk, len(hs), sum(h['dir'] == 'rd' for h in hs),
          sum(h['dir'] == 'wr' for h in hs), ','.join(sorted({h['fptr'] + '+' + h['freq'] for h in hs}))))
    for s in seqs:
        t = T.get(s)
        if not t: print('  seq %d: task row missing' % s); bad = True; continue
        sub, last = float(t['sub']), float(t['last'])
        print('  seq %d %s: sub %+.2f ms, last DMA %+.2f ms rel free, data=%s' % (s, 'AFTER free (next-task)' if sub > ft else
              'BEFORE free (in flight)', (sub - ft) * 1e3, (last - ft) * 1e3, t['data']))
    if seqs and seqs[0] - 1 in T: print('  prev task seq %d last DMA %+.2f ms' % (seqs[0] - 1, (float(T[seqs[0] - 1]['last']) - ft) * 1e3))
    near = [(round((t - ft) * 1e3, 2), e) for t, e in W if abs(t - ft) < 0.5]
    print('  wait edges within 0.5 s (ms, 1 entry/2 seed/3 exit):', near)
sys.exit(1 if bad else 0)
