#!/usr/bin/env python3
"""G3c(b) H-rt64 offline model. usage: g3c_spike_rdp_model.py run.log
For each logged [spike] polygon (5 edge vertices), take the convex hull, clip it to the RDP
scissor (0,0)-(320,240) with Sutherland-Hodgman, report on-screen area in pixels. Also checks the
RDP coordinate limits (X s15.16, Y s11.2 => |y| < 1024). Positive control: synthetic in-screen tri."""
import re, sys
pat = re.compile(r"\[spike\] swap=(\d+) off=(\w+) op=(\w+) .*? V=((?:\([^)]*\))+)")
def hull(P):
    P = sorted(set(P))
    if len(P) < 3: return P
    cr = lambda o,a,b: (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
    lo=[]; up=[]
    for p in P:
        while len(lo)>=2 and cr(lo[-2],lo[-1],p)<=0: lo.pop()
        lo.append(p)
    for p in reversed(P):
        while len(up)>=2 and cr(up[-2],up[-1],p)<=0: up.pop()
        up.append(p)
    return lo[:-1]+up[:-1]
def clip(poly, W=320.0, H=240.0):
    for inside, inter in (
        (lambda p:p[0]>=0, lambda a,b:(0,a[1]+(b[1]-a[1])*(0-a[0])/(b[0]-a[0]))),
        (lambda p:p[0]<=W, lambda a,b:(W,a[1]+(b[1]-a[1])*(W-a[0])/(b[0]-a[0]))),
        (lambda p:p[1]>=0, lambda a,b:(a[0]+(b[0]-a[0])*(0-a[1])/(b[1]-a[1]),0)),
        (lambda p:p[1]<=H, lambda a,b:(a[0]+(b[0]-a[0])*(H-a[1])/(b[1]-a[1]),H))):
        out=[]
        for i,p in enumerate(poly):
            q=poly[i-1]
            if inside(p):
                if not inside(q): out.append(inter(q,p))
                out.append(p)
            elif inside(q): out.append(inter(q,p))
        poly=out
        if not poly: break
    return poly
def area(p):
    return abs(sum(p[i-1][0]*p[i][1]-p[i][0]*p[i-1][1] for i in range(len(p))))/2 if len(p)>2 else 0.0
ctl = area(clip(hull([(10,10),(100,10),(10,100)])))
print(f"POSITIVE CONTROL in-screen tri area={ctl} (expect 4050)"); assert abs(ctl-4050)<1e-6
rows=[]
for line in open(sys.argv[1], errors="replace"):
    m = pat.search(line)
    if not m: continue
    pts=[tuple(map(float,p.split(","))) for p in re.findall(r"\(([^)]*)\)", m[4])]
    a = area(clip(hull(pts)))
    rows.append((int(m[1]), m[3], a, max(abs(p[1]) for p in pts), max(p[0] for p in pts)))
vis=[r for r in rows if r[2]>0.5]
print(f"flagged={len(rows)} on_screen_after_scissor(>0.5px)={len(vis)} y_limit_exceeded={sum(1 for r in rows if r[3]>=1024)}")
for r in vis: print(f"swap={r[0]} op={r[1]} area_px={r[2]:.1f} maxx={r[4]:.1f}")
