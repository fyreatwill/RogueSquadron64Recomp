#!/usr/bin/env python3
"""s5465: words stable before results entry that change at it.
usage: rdram_diff_results.py <rd_dir> <pre_lo> <pre_hi> <post_lo> [post_hi]
A word is a candidate if it takes ONE value across all dumps with swap in [pre_lo,pre_hi]
and a DIFFERENT single value across all dumps with swap >= post_lo (<= post_hi).
Dumps are host-order RDRAM; a guest u32 at aligned addr a is the little-endian u32 at file offset a.
"""
import sys, glob, re, os
from array import array

d, pl, ph, ql = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
qh = int(sys.argv[5]) if len(sys.argv) > 5 else 10**9
files = {}
for f in glob.glob(os.path.join(d, 'rdram_*.bin')):
    files[int(re.search(r'rdram_(\d+)_', f).group(1))] = f
pre = sorted(n for n in files if pl <= n <= ph)
post = sorted(n for n in files if ql <= n <= qh)
print('pre dumps', len(pre), 'post dumps', len(post))
if len(pre) < 2 or len(post) < 2:
    sys.exit('need >=2 each')
def ld(n):
    x = array('I'); x.frombytes(open(files[n], 'rb').read()); return x
def const_set(ns):
    base = ld(ns[0]); ok = bytearray(b'\x01') * len(base)
    for n in ns[1:]:
        o = ld(n)
        for i in [i for i in range(len(base)) if o[i] != base[i]]:
            ok[i] = 0
    return base, ok
a, pc = const_set(pre)
b, qc = const_set(post)
cand = [i for i in range(len(a)) if pc[i] and qc[i] and a[i] != b[i]]
print('const-pre', sum(pc), 'const-post', sum(qc), 'candidates', len(cand))
cl = {}
for i in cand:
    cl.setdefault(i * 4 // 64, []).append(i)
for k in sorted(cl)[:80]:
    ws = cl[k]
    print('0x%06X: %d words e.g. ' % (k * 64, len(ws)) + ' '.join('%06X:%08X->%08X' % (w * 4, a[w], b[w]) for w in ws[:4]))
print('clusters', len(cl))
