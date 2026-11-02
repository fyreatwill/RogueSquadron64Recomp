# s6785: break the hangar RDP-frame diff into classes (texrects vs tris per PRIM) for best-matched pairs.
import sys, collections, statistics as st
sys.path.insert(0, 'tools'); import g3_rdp_frame_match as m
R = m.frames(sys.argv[1], True, 240); P = m.frames(sys.argv[2], False, 240)
def split(c):
    t = collections.Counter({k[1]: v for k, v in c.items() if k[0] == 'tri'})
    r = collections.Counter({k: v for k, v in c.items() if k[0] != 'tri'})
    return t, r
rt = collections.Counter(); pt = collections.Counter(); trd = []; rrd = []; texonly = 0
for c in R:
    q = min(P, key=lambda q: sum(((c - q) + (q - c)).values()))
    ct, cr = split(c); qt, qr = split(q)
    rd = (cr - qr) + (qr - cr); td = (ct - qt) + (qt - ct)
    rrd.append(sum(rd.values())); trd.append(sum(td.values()))
    for k, v in (cr - qr).items(): rt[k] += v
    for k, v in (qr - cr).items(): pt[k] += v
print('texrect diff/frame median %s max %s ; tri diff/frame median %s max %s' % (st.median(rrd), max(rrd), st.median(trd), max(trd)))
print('texrects only-retail top', rt.most_common(8)); print('texrects only-port top', pt.most_common(8))
def pp(F, tag):
    per = collections.defaultdict(list)
    for c in F:
        t, _ = split(c)
        for k in set(k for f in F for k in split(f)[0]): per[k].append(t.get(k, 0))
    return per
pr, pq = pp(R, 'r'), pp(P, 'p')
print('PRIM            retail tris min/med/max      port tris min/med/max')
for k in sorted(set(pr) | set(pq), key=lambda k: -(st.median(pr.get(k, [0])) + st.median(pq.get(k, [0])))):
    a = pr.get(k, [0]); b = pq.get(k, [0])
    print('%-10s %5d %6.0f %5d   %5d %6.0f %5d' % (k, min(a), st.median(a), max(a), min(b), st.median(b), max(b)))
rtx = [sum(v for k, v in c.items() if k[0] != 'tri') for c in R]; ptx = [sum(v for k, v in c.items() if k[0] != 'tri') for c in P]
print('texrects/frame retail', collections.Counter(rtx).most_common(4), 'port', collections.Counter(ptx).most_common(4))
