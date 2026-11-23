"""s7843 (tools/s7843_dt_snap_replay.py): replay runInMissionFrame's dt snap (0x800FA730-0x800FA7AC: r=fmodf(dt,q) via 0x8001E20C; r>0: r/q<C1 ? dt-r : (dt+q)-r)
in IEEE float32 over a retail oracle log (--watch-pc 0x8004D6C8,0x8000BE28,0x8000BE80,0x800FA738,0x800FA7D0, FPR 0,4,6,14,20).
Prints model-vs-retail agreement, which (el,vd) give which snapped dt, the running min (= chase cam+0xA4) and where it first
drops, and what a constant pin (el,vd) would give. Usage: qreplay.py ORACLE_LOG"""
import re,sys,collections,struct
import math
f32=lambda x: struct.unpack('>f',struct.pack('>f',x))[0]  # one IEEE op in double then RN to single = exact single RN for +-*/
F=lambda h: struct.unpack('>f',bytes.fromhex(h))[0]; H=lambda x: struct.pack('>f',x).hex()
rx=re.compile(r'^\[hit\] x addr=\w+ pc=0x(\w+) .* n=(\d+) v0=0x(\w+) .* s0=0x(\w+) v1=0x(\w+).*?fpr: f0=(\w+) f4=(\w+) f6=(\w+) f14=(\w+) f20=(\w+)')
el=vd=None; ticks=[]; cur=None
for ln in open(sys.argv[1],errors='replace'):
    m=rx.match(ln)
    if not m: continue
    pc,n,v0,s0,v1,f0,f4,f6,f14,f20=m.groups()
    if pc=='8000be28': el=int(v0,16)
    elif pc=='8000be80': vd=int(v0,16)
    elif pc=='800fa738': cur={'dt':f20,'q':f14,'el':el,'vd':vd}; el=vd=None
    elif pc=='800fa7d0' and cur: cur['fin']=f20
    elif pc=='8004d6c8' and cur: cur['chase']=f20; ticks.append(cur); cur=None
def snap(dt,q,C1=0.5):
    x=f32(dt/q); r=f32(f32(x-float(math.trunc(x)))*q)
    if r>0: dt=f32(dt-r) if f32(r/q)<C1 else f32(f32(dt+q)-r)
    return dt
print('ticks',len(ticks))
ok=sum(H(snap(F(t['dt']),F(t['q'])))==t['fin'] for t in ticks if 'fin' in t); print('model==retail snapped dt:',ok,'/',len(ticks))
bad=[(i,t) for i,t in enumerate(ticks) if H(snap(F(t['dt']),F(t['q'])))!=t['fin']][:5]
for i,t in bad: print('  mismatch',i,t,H(snap(F(t['dt']),F(t['q']))))
c=collections.Counter((t['fin'],t['dt']) for t in ticks); print('snapped<-raw top:',c.most_common(8))
mn=None; first={}
for i,t in enumerate(ticks):
    v=F(t['fin']); mn=v if mn is None or v<mn or mn==0 else mn
    if H(mn)!=t['chase']: first.setdefault('chase_vs_min_mismatch',(i,H(mn),t['chase']))
    first.setdefault(H(mn),(i,t))
print('running-min first appearances:'); [print('  ',k,v) for k,v in first.items()]
fin87=[(i,t) for i,t in enumerate(ticks) if t['fin']=='3d088887']; print('ticks whose snapped dt = 87:',len(fin87),'first',fin87[:3])
print('per raw dt (el): snapped, count, first tick')
d=collections.defaultdict(list)
for i,t in enumerate(ticks): d[(t['dt'],t['el'])].append((i,t['fin']))
for k in sorted(d, key=lambda k:k[0]):
    fs=collections.Counter(f for _,f in d[k]); print('  raw',k[0],'el',k[1],dict(fs),'first',d[k][0][0])
# port pin: el 811160 vd 1 -> raw seen in s7842 port chase? compute snap for every raw in the 3d0b25xx band by mantissa step
print('snap of raw 3d0b2500..3d0b2600 giving 87:',[hex(m) for m in range(0x3d0b2500,0x3d0b2600) if H(snap(F('%08x'%m),F('3c888888')))=='3d088887'][:40])
print('snap(3d0b259c)=',H(snap(F('3d0b259c'),F('3c888888'))),' snap(3d088889)=',H(snap(F('3d088889'),F('3c888888'))))
