#!/usr/bin/env python3
"""Fold a G1c run dir: g1b frame-time p50/p99 (sd_wall mean ms, per second),
gridlog kept distribution, and crash/stall summary. Usage: g1c_fold.py DIR..."""
import re,sys,statistics as st
def pct(a,p):
    a=sorted(a); return a[min(len(a)-1,int(len(a)*p))] if a else float('nan')
for d in sys.argv[1:]:
    log=open(d+'/run.log',errors='replace').read()
    sd=[float(m.group(1)) for m in re.finditer(r'\[g1b\][^\n]*sd_wall=([\d.]+)/',log)]
    tk=[int(m.group(1)) for m in re.finditer(r'\[g1b\][^\n]*tasks=(\d+)',log)]
    kept=[int(m.group(1)) for m in re.finditer(r'\[gridlog\][^\n]*kept=(\d+)',log)]
    req=[int(m.group(1)) for m in re.finditer(r'\[gridlog\][^\n]*req=(\d+)',log)]
    summ=open(d+'/summary').read().strip() if __import__('os').path.exists(d+'/summary') else ''
    print(d.split('/')[-1], f'n={len(sd)} sd_wall p50={pct(sd,.5):.1f} p99={pct(sd,.99):.1f} mean={st.mean(sd) if sd else 0:.1f} tasks/s={st.mean(tk) if tk else 0:.1f}',
      f'grid n={len(kept)} kept p50={pct(kept,.5)} max={max(kept) if kept else 0} req max={max(req) if req else 0}')
    print('   ',summ[:200])
