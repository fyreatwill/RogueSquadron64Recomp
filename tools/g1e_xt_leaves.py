# s6939: leaf PC histogram from `xctrace export` of a Time Profiler run (see tools/g1e_ucode_blocks.py for the recipe).
# leaf-PC histogram from an xctrace time-profile export; prints "count addr name" for every leaf
# s6941: THREAD=<substring> keeps only samples of matching threads (e.g. THREAD='Gfx Thread'); per-thread totals go to stderr.
import os
TH = os.environ.get('THREAD')
# s6942: CALLER=<leaf name substring> prints counts of frames 1..3 (callers) for samples whose leaf matches, instead of the leaf histogram.
CALLER = os.environ.get('CALLER')
import sys, xml.etree.ElementTree as ET, collections
cal = collections.Counter()
ids = {}
def res(e):
    r = e.get('ref'); return ids.get(r, e) if r else e
cnt = collections.Counter(); nm = {}; thr = collections.Counter()
for ev, e in ET.iterparse(sys.argv[1], events=('end',)):
    i = e.get('id')
    if i: ids[i] = e
    if e.tag == 'row':
        bt = None; th = None
        for c in e:
            c2 = res(c)
            if c2.tag == 'tagged-backtrace':
                for g in c2:
                    g = res(g)
                    if g.tag == 'backtrace': bt = g
            if c2.tag == 'backtrace': bt = c2
            if c2.tag == 'thread': th = c2.get('fmt')
        if bt is None: continue
        if TH and (th is None or TH not in th): continue
        fr = [res(f) for f in bt if res(f).tag == 'frame']
        if not fr: continue
        if CALLER:
            if CALLER in (fr[0].get('name') or ''):
                cal[' <- '.join((f.get('name') or f.get('addr') or '?') for f in fr[1:4])] += 1
            continue
        a = fr[0].get('addr'); cnt[a] += 1; nm[a] = fr[0].get('name') or '?'; thr[th] += 1
for k, c in cal.most_common(25): print(c, k)
for a, c in cnt.most_common(): print(c, a, nm[a].replace(' ', '_'))
print('#threads', thr.most_common(8), file=sys.stderr)
