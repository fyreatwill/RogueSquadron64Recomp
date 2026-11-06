#!/usr/bin/env python3
"""s6918 G5h: retail vs port far cutoff inputs at matched camera pose, AT THE MOVIES. Reads the oracle log of scratch/s6918/oracle.zsh
and a ROGUESQ_G5H_BAND file (paths below). Per pose segment prints scene scalar, radius, cutoff^2, eye y for both, and port A/B tris."""
import re,struct,sys,bisect,statistics as st,pickle,math
f=lambda w:struct.unpack('>f',bytes.fromhex(w))[0]
R=[];cam=None
for l in open('scratch/s6918/retail/oracle.log',errors='replace'):
    if not l.startswith('[xtrace]'):continue
    p=l.split();vi=int(p[2]);ms=re.findall(r'm=([0-9a-f]+):([0-9a-f,]+)',l)
    if 'pc=800455dc' in l and ms: cam=ms[0][1].split(',')
    elif 'pc=800456d8' in l and len(ms)>=3 and cam:
        a=ms[0][1].split(',');b=ms[1][1];c=ms[2][1].split(',')
        R.append(dict(t=vi/60.0,deac=f(a[0]),deb0=f(a[1]),deb4=f(a[2]),fbc=f(b),th=[f(x) for x in c],pos=[f(cam[i]) for i in (4,5,6)],h=f(cam[20]),cam=cam))
P=[];t0=None
for l in open('scratch/s6918/band_port.txt',errors='replace'):
    p=l.split()
    if len(p)<45:continue
    t0=t0 or int(p[1]);c=[x.lower() for x in p[13:45]]
    try:P.append(dict(sw=int(p[0]),t=(int(p[1])-t0)/24e6,A=int(p[2]),B=int(p[3]),deac=f(p[4]),deb0=f(p[5]),deb4=f(p[6]),fbc=f(p[7]),th=[f(x) for x in p[8:12]],pos=[f(c[i]) for i in (4,5,6)],h=f(c[20]),cam=c))
    except Exception:pass
print('retail rows',len(R),'port rows',len(P),'retail t',R[0]['t'],R[-1]['t'],'port t',P[0]['t'],P[-1]['t'])
pickle.dump((R,P),open('scratch/s6918/rp.pkl','wb'))
def segs(L):
    o=[];s=0
    for i in range(1,len(L)+1):
        if i==len(L) or L[i]['fbc']!=L[s]['fbc'] or max(abs(x-y) for x,y in zip(L[i]['pos'],L[i-1]['pos']))>5:
            if i-s>=15:o.append((s,i))
            s=i
    return o
sr,sp=segs(R),segs(P);print('segs',len(sr),len(sp))
pp=[p['pos'] for p in P]
out=[]
for a,b in sr:
    if R[a]['t']<150:continue
    # pose match for each sampled retail frame across all port rows
    D=[];I=[]
    for r in R[a:b:max(1,(b-a)//12)]:
        x0,y0,z0=r['pos'];i,dv=min(((i,abs(q[0]-x0)+abs(q[1]-y0)+abs(q[2]-z0)) for i,q in enumerate(pp)),key=lambda e:e[1]);D.append(dv);I.append(i)
    g=[(R[a+k*max(1,(b-a)//12)],P[i]) for k,(i,x) in enumerate(zip(I,D)) if x<0.05]
    if not g:out.append((R[a]['t'],b-a,None));continue
    m=lambda k,j:st.median(x[j][k] for x in g)
    out.append((R[a]['t'],b-a,len(g),m('t',1),m('fbc',0),m('fbc',1),m('deac',0),m('deac',1),m('deb4',0),m('deb4',1),m('h',0),m('h',1),st.median(x[1]['A'] for x in g),st.median(x[1]['B'] for x in g)))
print('rt nfr ng | pt | fbc r p | deac r p | deb4 r p | h r p | portA B')
for o in out:
    if o[2] is None: print('%.0f %d nomatch'%o[:2])
    else: print('%.0f %d %d | %.0f | %.3f %.3f | %.2f %.2f | %.1f %.1f | %.2f %.2f | %d %d'%o)
