"""s5918: pp identity + bearing of class-1 sphere centres from SHIP position ([plpos], joined by log order) vs ship velocity.
usage: python3 -I tools/s5918_shipbearing.py run.log"""
import re, sys, math, collections
P=re.compile(r"\[plpos\].*pos=\(([-\d.e]+),([-\d.e]+),([-\d.e]+)\)")
S=re.compile(r"\[s5901\] c=\d+ pp=([^,]+),([^,]+),([^ ]+) len=\S+ rows=\d+ best_ratio=(\S+) id=\S+ c1f=(\d).* ctr=([^,]+),([^,]+),([^ ]+) r2=")
ship=None; prev=None; dp=collections.defaultdict(list); dc=collections.defaultdict(list); rel=collections.defaultdict(list); n=0
for l in open(sys.argv[1],errors="replace"):
    m=P.search(l)
    if m:
        q3=tuple(map(float,m.groups())); ship=q3+((q3[0]-prev[0],0,q3[2]-prev[2]) if prev else (0,0,0)); prev=q3; continue
    m=S.search(l)
    if not m or not ship: continue
    g=m.groups(); pp=tuple(map(float,g[:3])); f=int(g[4]); ctr=tuple(map(float,g[5:8]))
    dp[f].append(math.dist(pp,ship[:3])); dc[f].append(math.dist(ctr,ship[:3]))
    if math.hypot(ship[3],ship[5])>0.05:
        a=math.degrees(math.atan2(ctr[2]-ship[2],ctr[0]-ship[0])-math.atan2(ship[5],ship[3]))%360
        rel[f].append(a)
q=lambda v:(sorted(v)[len(v)//10],sorted(v)[len(v)//2],sorted(v)[9*len(v)//10])
for f in (0,1):
    if dp[f]: print("c1f",f,"n",len(dp[f]),"|pp-ship| p10/50/90",q(dp[f]),"|ctr-ship|",q(dc[f]))
    h=collections.Counter(int(a//45)*45 for a in rel[f]); print("  bearing(ship->ctr) vs ship vel, 45deg bins",sorted(h.items()),"n",len(rel[f]))
