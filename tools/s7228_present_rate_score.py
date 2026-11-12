#!/usr/bin/env python3
"""s7228: on-screen present rate around a display removal, from a ROGUESQ_PRESENT_RING file.
usage: s7228_present_rate_score.py RING [split_s]
split = time (s after first ring row) of the removal; default = first Z row whose width differs from the
previous Z/first-seen width after t>=150 s, else 172 s. Prints per-second on-screen presents (P rows with
at>0) for 50 s before / after the split, and a verdict: FLAT30 (after: >=90% of seconds in 25..35 and none
>=45) vs MIXED (some seconds >=45)."""
import sys, re, collections
ring = sys.argv[1]
rows = []
for ln in open(ring):
    p = ln.split()
    if len(p) < 2: continue
    try: t = float(p[1])
    except ValueError: continue
    rows.append((p[0], t, ln))
t0 = rows[0][1]
zs = [(t - t0, re.search(r'w=(\d+) h=(\d+)', ln).groups()) for k, t, ln in rows if k == 'Z']
split = float(sys.argv[2]) if len(sys.argv) > 2 else None
if split is None:
    for tz, wh in zs:
        if tz >= 150: split = tz; break
    if split is None: split = 172.0
on = collections.Counter(); q = collections.Counter(); acq = collections.defaultdict(list)
for k, t, ln in rows:
    s = int(t - t0)
    if k == 'P':
        m = re.search(r'at=([0-9.]+)', ln)
        if m and float(m.group(1)) > 0: on[s] += 1
    elif k == 'Q':
        q[s] += 1
        m = re.search(r'acq_ms=([0-9.]+)', ln)
        if m: acq[s].append(float(m.group(1)))
S = int(split)
def win(a, b): return [on[s] for s in range(a, b)]
pre, post = win(S - 50, S - 1), win(S + 4, S + 53)
qpre, qpost = [q[x] for x in range(S - 50, S - 1)], [q[x] for x in range(S + 4, S + 53)]
def summ(v):
    v2 = [x for x in v if x > 0]
    if not v2: return 'none'
    return 'n=%d mean=%.1f ge45=%d in25_35=%d max=%d' % (len(v2), sum(v2)/len(v2), sum(x >= 45 for x in v2), sum(25 <= x <= 35 for x in v2), max(v2))
def verdict(v):
    v2 = [x for x in v if x > 0]
    if len(v2) < 10: return 'NODATA'
    if sum(x >= 45 for x in v2) == 0 and sum(25 <= x <= 35 for x in v2) >= 0.9 * len(v2): return 'FLAT30'
    return 'MIXED'
def med(v):
    v = sorted(v); return v[len(v)//2] if v else -1
print('ring', ring, 'split %.1f s' % split, 'Z rows', ['%.1f:%sx%s' % (tz, *wh) for tz, wh in zs])
print('on-screen pre ', summ(pre), verdict(pre)); print('on-screen post', summ(post), verdict(post))
print('queued    pre ', summ(qpre), verdict(qpre)); print('queued    post', summ(qpost), verdict(qpost))
print('acq_ms median pre %.2f post %.2f' % (med(sum((acq[x] for x in range(S-50, S-1)), [])), med(sum((acq[x] for x in range(S+4, S+53)), []))))
print('post on-screen per-s', post)
