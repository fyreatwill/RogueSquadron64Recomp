#!/usr/bin/env python3
"""Mean|PCM| ratio (300 callbacks after / 100 before) around each [spath] enqueueSpeechClip,
vs control windows. Usage: speech_window_ratio.py run.log"""
import re, sys, statistics as st
ma=[]; enq=[]
for l in open(sys.argv[1], errors='replace'):
    m=re.match(r'\[pcm-dense\] n=\d+ ma=(\d+)',l)
    if m: ma.append(int(m.group(1)))
    elif '[spath] enqueueSpeechClip' in l: enq.append(len(ma))
def r(i):
    b=ma[max(0,i-100):i]; a=ma[i:i+300]
    return (sum(a)/len(a))/max(1,sum(b)/len(b)) if b and a else None
print('callbacks',len(ma),'enqueues',len(enq))
print('enqueue ratios',[round(x,1) for x in map(r,enq) if x])
ctl=[x for i in range(100,len(ma)-300,150) if all(abs(i-e)>400 for e in enq) for x in [r(i)] if x]
if ctl:
    ctl.sort(); print('control n',len(ctl),'median %.2f p90 %.2f'%(st.median(ctl),ctl[int(.9*len(ctl))]))
