# s6791 G3f: per-press pan timeline (fraction of distance / yaw vs real s) of the craft-select camera 800cd670 in port
# ROGUESQ_G3F_CAM logs. usage: g3f_pan_cmp.py ARM... (reads scratch/s6791/ARM/cam.txt; presses 40,46,52,58,64 s)
import sys, math
def load(f):
    out=[]; last=None
    for ln in open(f):
        p=ln.split()
        if len(p)<22 or p[2]!='800cd670': continue
        v=[float(x) for x in p[5:22]]; key=tuple(v[5:17])
        if key==last: continue
        last=key; out.append((float(p[0]),v))
    return out
for arm in sys.argv[1:]:
    r=load(f'scratch/s6791/{arm}/cam.txt')
    for press in (40,46,52,58,64):
        seg=[x for x in r if press-0.5<=x[0]<=press+5.5]
        if not seg: continue
        p0=seg[0][1][14:17]
        mv=[x for x in seg if math.dist(x[1][14:17],p0)>0.05]
        if not mv: print(arm,press,'no move'); continue
        on=mv[0][0]; pf=seg[-1][1][14:17]
        st=[x[0] for x in seg if math.dist(x[1][14:17],pf)>0.05]; settle=(st[-1] if st else on)
        yaw=[math.degrees(math.atan2(x[1][7],x[1][5])) for x in seg]
        steps=[ (seg[i+1][1][14:17], seg[i+1][0]-seg[i][0]) for i in range(len(seg)-1)]
        sp=[math.dist(seg[i+1][1][14:17],seg[i][1][14:17])/max(1e-4,seg[i+1][0]-seg[i][0]) for i in range(len(seg)-1) if seg[i][0]>=on-0.1]
        # overshoot: max distance beyond final along path from start
        D=math.dist(p0,pf); over=max(math.dist(x[1][14:17],p0) for x in seg)-D
        print(f'{arm} press {press}: onset +{on-press:.3f}s settle +{settle-press:.2f}s dist {D:.1f} overshoot {over:.2f} frames {len([x for x in seg if on<=x[0]<=settle])} peakspeed {max(sp):.1f}/s yaw {yaw[0]:.1f}->{yaw[-1]:.1f}')
print('--- fraction-of-distance timeline (s after press) ---')
for arm in sys.argv[1:]:
    r=load(f'scratch/s6791/{arm}/cam.txt')
    for press in (40,46,52,58,64):
        seg=[x for x in r if press-0.05<=x[0]<=press+5.5]
        p0=seg[0][1][14:17]; pf=seg[-1][1][14:17]; D=math.dist(p0,pf)
        def tf(f):
            for x in seg:
                if math.dist(x[1][14:17],p0)>=f*D: return x[0]-press
        # yaw progress
        y0=math.degrees(math.atan2(seg[0][1][7],seg[0][1][5])); yf=math.degrees(math.atan2(seg[-1][1][7],seg[-1][1][5]))
        def yf_(f):
            for x in seg:
                y=math.degrees(math.atan2(x[1][7],x[1][5])); d=(y-y0+540)%360-180; dt=(yf-y0+540)%360-180
                if abs(d)>=f*abs(dt): return x[0]-press
        print(arm,press,' '.join('p%d=%.2f'%(f*100,tf(f)) for f in (.1,.5,.9,.99)),' | ',' '.join('y%d=%.2f'%(f*100,yf_(f)) for f in (.1,.5,.9,.99)))
