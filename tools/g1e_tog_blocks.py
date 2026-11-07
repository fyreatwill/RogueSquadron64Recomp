#!/usr/bin/env python3
# s6945: per 10 s block view of a =tog run ([g1b] lines, t>=100): block sd_wall/tasks, adjacent on-off pair diffs, p10/min tasks per arm. usage: g1e_tog_blocks.py log
import re,statistics as st,subprocess,sys
f=sys.argv[1]; b=int(subprocess.check_output(['/usr/bin/stat','-f','%B',f]))
G=re.compile(rb'^\[g1b\] t=(\d+) vi=(\d+) tasks=(\d+) sd_wall=([\d.]+)/')
blk={}
for l in open(f,'rb'):
    m=G.match(l)
    if not m or int(m[1])<100: continue
    e=b+int(m[1])
    if 2<=e%10<=7: blk.setdefault(e//10,[]).append((int(m[3]),float(m[4])))
ks=sorted(blk); rows=[(k,k&1,st.mean(x[1] for x in blk[k]),st.mean(x[0] for x in blk[k])) for k in ks]
for r in rows: print(r[0]%1000,'on' if r[1] else 'off','sd %.2f tasks %.1f'%(r[2],r[3]))
# adjacent pair diffs on-off
d=[rows[i+1][2]-rows[i][2] if rows[i+1][1] else rows[i][2]-rows[i+1][2] for i in range(len(rows)-1)]
print('adjacent on-off sd diffs',['%.2f'%x for x in d],'neg',sum(x<0 for x in d),'/',len(d))
for k in (0,1):
    t=sorted(x[0] for r in ks if (r&1)==k for x in blk[r]); print('on' if k else 'off','p10 tasks',t[len(t)//10],'min',t[0])
