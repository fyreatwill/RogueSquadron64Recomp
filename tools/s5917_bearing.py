"""s5917: for [s5901] rows, bearing (xz) from pp to ctr vs pp travel direction, split by c1f.
usage: python3 -I tools/s5917_bearing.py run.log"""
import re, sys, math, collections
R = re.compile(r"\[s5901\] c=(\d+) pp=([^,]+),([^,]+),([^ ]+) len=(\S+) rows=(\d+) best_ratio=(\S+) id=(\S+) c1f=(\d+) did=(\S+) obj=(\S+) ctr=([^,]+),([^,]+),([^ ]+) r2=(\S+)")
rows=[]
for l in open(sys.argv[1],errors="replace"):
    m=R.search(l)
    if m:
        g=m.groups(); rows.append((int(g[0]),tuple(map(float,g[1:4])),float(g[6]),g[7],int(g[8]),tuple(map(float,g[11:14])),float(g[14])))
print("rows",len(rows),"by c1f",collections.Counter(r[4] for r in rows))
for f in (0,1):
    d=[];dy=[];inn=0;n=0
    for c,pp,br,i,c1,ctr,r2 in rows:
        if c1!=f: continue
        dx,dz=ctr[0]-pp[0],ctr[2]-pp[2]; D=math.hypot(dx,dz); n+=1
        d.append(D); dy.append(ctr[1]-pp[1]); inn+= br<=1
    d.sort(); dy.sort()
    if n: print("c1f",f,"n",n,"xz dist p10/50/90",d[n//10],d[n//2],d[9*n//10],"dy p10/50/90",dy[n//10],dy[n//2],dy[9*n//10],"best_ratio<=1:",inn)
# bearing relative to ship travel: ship pp per cycle (first sample each cycle, mean)
cyc=collections.defaultdict(list)
for r in rows: cyc[r[0]].append(r)
cs=sorted(cyc); rel=collections.defaultdict(list)
for a,b in zip(cs,cs[1:]):
    if b!=a+1: continue
    pa=cyc[a][0][1]; pb=cyc[b][0][1]
    vx,vz=pb[0]-pa[0],pb[2]-pa[2]
    if math.hypot(vx,vz)<0.05: continue
    for c,pp,br,i,c1,ctr,r2 in cyc[b]:
        ang=math.degrees(math.atan2(ctr[2]-pp[2],ctr[0]-pp[0])-math.atan2(vz,vx))%360
        rel[c1].append(ang)
for f,v in rel.items():
    h=collections.Counter(int(a//45)*45 for a in v)
    print("c1f",f,"rel bearing hist(45deg bins)",sorted(h.items()),"n",len(v))
