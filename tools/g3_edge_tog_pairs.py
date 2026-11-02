import sys,glob,os,re
from PIL import Image, ImageChops, ImageStat
mean=lambda v: sum(v)/len(v)
# s6797: ROGUESQ_EXACT_EDGES=tog seam scorer for STATIC screens (menus/hangar). Consecutive captures in opposite arms
# (on = odd epoch second; times.txt "<n> <t0> <t1>", capture counted only if inside one second, >=0.15 s past the boundary)
# whose frames are near-identical (<2% pixels differ) are diffed; a "line" is a column/row where >=24 differing pixels
# (|dRGB|>40) sit in one 1-2 px wide run. Same-arm consecutive pairs are the noise control; a synthetic 1 px line
# injected into one frame of each cross-arm pair is the positive control (must be counted).
# Also splits [exactedges-stat] (tris, fans, extra tris, block us) and [g1b] sd_wall by arm from run.log.
# Usage: python3 tools/g3_edge_tog_pairs.py <capture dir> <run.log>
d,log=sys.argv[1],sys.argv[2]
T={}
for l in open(d+'/times.txt'):
    c,a,b=l.split(); a=float(a.replace(',','.')); b=float(b.replace(',','.'))
    if int(a)==int(b) and a-int(a)>=0.15: T[int(c)]=(int(a)&1,a)
F={}
for f in glob.glob(d+'/w*.png'):
    c=int(os.path.basename(f).split('_')[1])
    if c in T: F[c]=f
def load(c): return Image.open(F[c]).convert('RGB')
def dmask(A,B):
    r,g,b=ImageChops.difference(A,B).split()
    return ImageChops.lighter(ImageChops.lighter(r,g),b).point(lambda v:255 if v>40 else 0)
def lines(m):
    n=0; where=[]; w,h=m.size
    for ax in (0,1):
        sz=(w,1) if ax==0 else (1,h)
        cnt=[v*(h if ax==0 else w)/255 for v in m.resize(sz,Image.BOX).get_flattened_data()]  # ax=0 -> per column
        hot=[c>=24 for c in cnt]
        i=0
        while i<len(hot):
            if hot[i]:
                j=i
                while j<len(hot) and hot[j]: j+=1
                if j-i<=2: n+=1; where.append(('col' if ax==0 else 'row',i))
                i=j
            else: i+=1
    return n,where
cs=sorted(F); res={'x':[0,0,0,[]],'s':[0,0,0,[]]}; pc=[0,0]
prs=[(a,a+g) for a in cs for g in (1,2) if a+g in F]  # gap 2 supplies the same-arm (noise) pairs
for a,b in prs:
    A,B=load(a),load(b)
    if A.size!=B.size: continue
    m=dmask(A,B)
    if ImageStat.Stat(m).mean[0]/255>0.02 or mean(ImageStat.Stat(A).mean)<8: continue
    k='x' if T[a][0]!=T[b][0] else 's'
    n,w=lines(m); r=res[k]; r[0]+=1; r[1]+=n; r[2]+=(n>0)
    if n: r[3].append((a,b,T[a][0],T[b][0],os.path.basename(F[a])[:4],w[:4]))
    if k=='x':  # positive control: synthetic 1 px column, value flipped, rows 100..300
        C=A.copy(); px=C.load(); hot={v for t,v in w if t=='col'}; x=next(x for x in range(A.size[0]//3,A.size[0]) if all(abs(x-v)>4 for v in hot))
        for y in range(100,300): px[x,y]=tuple(255-v if v<128 else 0 for v in px[x,y])
        nc,_=lines(dmask(C,B)); pc[0]+=1; pc[1]+=(nc>n)
for k,lab in (('x','cross-arm'),('s','same-arm')):
    r=res[k]; print('%s pairs %d with-line %d lines %d'%(lab,r[0],r[2],r[1]))
    for e in r[3][:12]: print('   ',e)
print('positive control: synthetic line detected %d/%d'%(pc[1],pc[0]))
st={0:[0,0,0,0.0,0],1:[0,0,0,0.0,0]}
ev=[]  # stderr order of arm toggles and g1b lines
for l in open(log,errors='replace'):
    m=re.search(r'\[exactedges-stat\] on=(\d) sec=\d+ tris=(\d+) fans=(\d+) extra=(\d+) us=(\d+)',l)
    if m:
        a=int(m.group(1)); s=st[a]; s[0]+=int(m.group(2)); s[1]+=int(m.group(3)); s[2]+=int(m.group(4)); s[3]+=float(m.group(5)); s[4]+=1
    m=re.search(r'\[exactedges\] on=(\d)',l)
    if m: ev.append(('e',int(m.group(1))))
    m=re.search(r'\[g1b\] t=\d+ vi=(\d+) tasks=(\d+) sd_wall=([\d.]+)',l)
    if m: ev.append(('g',int(m.group(1)),int(m.group(2)),float(m.group(3))))
for a in (0,1):
    s=st[a]; print('arm on=%d secs %d tris %d fans %d (%.2f%%) extra tris %d (+%.2f%%) block us/s %.0f us/tri %.3f'%(
        a,s[4],s[0],s[1],100*s[1]/max(s[0],1),s[2],100*s[2]/max(s[0],1),s[3]/max(s[4],1),s[3]/max(s[0],1)))
# g1b second -> arm of the toggle line printed most recently before it (majority only if phase offset is small; reported both)
cur=None; g={0:[],1:[]}
for e in ev:
    if e[0]=='e': cur=e[1]
    elif cur is not None and e[2]>0: g[cur].append(e)
for a in (0,1):
    v=g[a]
    if v: print('g1b arm~%d secs %d vi/s %.1f tasks/s %.1f sd_wall ms %.3f'%(a,len(v),mean([x[1] for x in v]),mean([x[2] for x in v]),mean([x[3] for x in v])))
