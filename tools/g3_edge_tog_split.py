import sys,glob,os
# Usage: python3 tools/g3_edge_tog_split.py <capture dir with w*.png + times.txt "<n> <t0> <t1>" (scratch/s6796/dense.sh)>
from PIL import Image
# s6796: s6736 edge.py scorer split by ROGUESQ_EXACT_EDGES=tog arm (on = odd epoch second). A capture counts only if its
# screencapture start/end epoch both fall in the same second, >=0.15 s past the boundary (frame latency margin).
d=sys.argv[1]
T={}
for l in open(d+'/times.txt'):
    c,a,b=l.split(); a=float(a.replace(',','.')); b=float(b.replace(',','.'))
    if int(a)==int(b) and a-int(a)>=0.15: T[int(c)]=int(a)&1
st={0:[0,0,0,0,0],1:[0,0,0,0,0]}  # lit, sky_col, dark, dark_line, newcol
prof={0:[0]*8,1:[0]*8}; npf={0:0,1:0}
for f in sorted(glob.glob(d+'/w*.png')):
    b=os.path.basename(f); t=int(b[1:4]); c=int(b.split('_')[1])
    if t<90 or c not in T: continue
    arm=T[c]; s_=st[arm]
    im=Image.open(f).convert('RGB'); px=im.load(); w,h=im.size
    s=sum(sum(px[x,y])//3 for y in range(60,h,16) for x in range(0,w,16))/((h-60)//16*(w//16))
    if s<15:
        s_[2]+=1
        lit=sum(1 for y in range(60,h,2) if any(sum(px[x,y])>120 for x in list(range(w-4,w))+list(range(1189,1197))))
        if lit>20: s_[3]+=1
        continue
    hit=0; nh=0
    for y in (700,800,850):
        xs=[x for x in range(w-1,w-200,-1) if sum(px[x,y])>36]
        if not xs: continue
        r=xs[0]
        e=max(range(r-3,r+1),key=lambda x:px[x,y][2])
        if px[e,y][2]-px[r-6,y][2]>40 and px[e,y][2]>120: hit+=1
        # new-line probe: any single column in r-30..r-5 bluer than both neighbours by >40
        if any(px[x,y][2]-px[x-2,y][2]>40 and px[x,y][2]-px[x+2,y][2]>40 for x in range(r-30,r-4)): nh+=1
        for k in range(8): prof[arm][k]+=px[r-k,y][2]
        npf[arm]+=1
    s_[0]+=1; s_[1]+= hit>=2; s_[4]+= nh>=2
for arm in (0,1):
    s_=st[arm]; n=max(npf[arm],1)
    print('arm on=%d lit %d sky_edge_col %d (%.0f%%) newcol %d | dark %d dark_line %d | mean B at r-0..7: %s'%(arm,s_[0],s_[1],100*s_[1]/max(s_[0],1),s_[4],s_[2],s_[3],' '.join('%.0f'%(v/n) for v in prof[arm])))
print('kept',len(T),'of',sum(1 for _ in open(d+'/times.txt')))
