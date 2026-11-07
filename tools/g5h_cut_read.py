#!/usr/bin/env python3
"""s6919 G5h: far cutoff the chain actually READ at 0x800434F4, retail vs port, at matched eye position, port rows split by ROGUESQ_CUT_LIVE=tog state.
Usage: g5h_cut_read.py oracle.log band.txt [tmin]. Oracle spec: scratch/s6919/oracle.zsh. Band rows: ROGUESQ_G5H_BAND, last 12 words g_rs64_s6919.
Per retail pose bucket prints read cutoff retail, port live, port old, and port B/A by state."""
import re,struct,sys,statistics as st,pickle
f=lambda w:struct.unpack('>f',bytes.fromhex(w))[0]
R=[];cam=None;fbc=None
for l in open(sys.argv[1],errors='replace'):
    if not l.startswith('[xtrace]'):continue
    ms=re.findall(r'm=([0-9a-f]+):([0-9a-f,]+)',l);vi=int(l.split()[2])
    if 'pc=800455dc' in l and ms: cam=ms[0][1].split(',')
    elif 'pc=800434f4' in l and len(ms)>=5 and cam:
        n=ms[0][1].split(',');d=ms[1][1].split(',');c=ms[2][1].split(',')
        R.append(dict(t=vi/60.0,d2=f(n[2]),x=int(n[3],16),z=int(n[4],16),deac=f(d[0]),cut=f(d[2]),c10=[f(x) for x in c],pos=[f(cam[i]) for i in (4,5,6)]))
P=[];t0=None
for l in open(sys.argv[2],errors='replace'):
    p=l.split()
    if len(p)<57:continue
    t0=t0 or int(p[1]);c=[x.lower() for x in p[13:45]];s=p[45:57]
    try:P.append(dict(t=(int(p[1])-t0)/24e6,odd=(int(p[1])//24000000)&1,A=int(p[2]),B=int(p[3]),seen=f(p[6]),d2=f(s[0]),cut=f(s[1]),live=int(s[11],16),c10=[f(x) for x in s[4:7]],pos=[f(c[i]) for i in (4,5,6)]))
    except Exception:pass
print('retail rows',len(R),'port rows',len(P),'live',sum(p['live'] for p in P))
print('retail d2<cut at the cut node',sum(r['d2']<r['cut'] for r in R),'of',len(R))
pickle.dump((R,P),open(sys.argv[2]+'.pkl','wb'))
tmin=float(sys.argv[3]) if len(sys.argv)>3 else 0
q=lambda v,n=1:round(st.median(v),n) if v else None
print('retail t | n | cut R | port cut live, old | seen | port B/A live, old | c10 dist')
i=0;Rs=[r for r in R if r['t']>=tmin]
for s in range(0,len(Rs),max(1,len(Rs)//60)):
    r=Rs[s];X,Y,Z=r['pos']
    near=[p for p in P if abs(p['pos'][0]-X)+abs(p['pos'][1]-Y)+abs(p['pos'][2]-Z)<0.5]
    L=[p for p in near if p['live']];O=[p for p in near if not p['live']]
    ba=lambda v:q([p['B']/max(p['A'],1) for p in v],2)
    dc=q([sum(abs(a-b) for a,b in zip(p['c10'],r['c10'])) for p in near],3)
    print(round(r['t']),len(near),'|',round(r['cut'],1),'|',q([p['cut'] for p in L]),q([p['cut'] for p in O]),'|',q([p['seen'] for p in near]),'|',ba(L),ba(O),'|',dc)
