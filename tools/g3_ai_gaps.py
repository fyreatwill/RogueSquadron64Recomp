#!/usr/bin/env python3
"""s6806: largest VI gaps between consecutive AI buffers (osAiSetNextBuffer rows 0x8008EE08/0x8008EE84) per arm, with
the sim tick. A gap of N VI = the guest did not feed the AI for N VIs (guest-side, not host queue). Retail oracle logs
only carry these rows after the --debug-write trace arm, so a retail null here covers in-mission time only.
usage: [G3_GAP_MIN=N] g3_ai_gaps.py [PAIR_DIR ...]   (dir holding retail/oracle.log[.zst] + port.rand.txt)"""
import os,sys,subprocess
os.environ["G3_TICK"]="800FA730"
src=open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"g3_ai_clock.py")).read(); ns={"__name__":"x"}; exec(src.replace("\nmain()",""),ns)
GMIN=int(os.environ.get("G3_GAP_MIN","0"))
def gaps(path,retail):
    tick=-1; prev=None; out=[]; first=None; nb=0
    for vi,pc,l in ns["rows"](path,retail):
        if pc==ns["TICK"]: tick+=1
        elif pc in ns["AI"]:
            nb+=1
            if first is None: first=vi
            if prev is not None: out.append((vi-prev,prev,tick))
            prev=vi
    if GMIN: return first,prev,nb,[(g,v,t) for g,v,t in out if g>=GMIN]  # s6807: every gap >= G3_GAP_MIN, VI order
    out.sort(reverse=True)
    return first,prev,nb,out[:4]
for d,r,p in [(a.replace("scratch/","").rstrip("/"),"retail","port") for a in (sys.argv[1:] or ["scratch/s6777","scratch/s6763","scratch/s6766","scratch/s6773/r19","scratch/s6764"])]:
    log=f"scratch/{d}/{r}/oracle.log.zst"; tmp="/tmp/aigap_oracle.log"
    if not os.path.exists(log): log=log[:-4]
    subprocess.run(f"zstd -dcfq {log} > {tmp}",shell=True)
    print(d,"retail",gaps(tmp,True)); print(d,"port  ",gaps(f"scratch/{d}/{p}.rand.txt",False))
