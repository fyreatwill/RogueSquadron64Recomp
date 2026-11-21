#!/usr/bin/env python3
# s7757: replay every k900 route snap in <snapdir> (tools/s7754_capture_route.zsh) from its BEGIN and END image through the live
# harness at the dd>1 policy (CAP 1048576 TG 1); prints EQ/DIFF vs the live tail per image and b==e (False marks an H-state task).
# usage: s7757_route_replay.py [snapdir]   (default scratch/s7754/w219/snap)
import os,sys,glob,re,subprocess
import importlib.util
sp=importlib.util.spec_from_file_location('g','tools/s7753_rdp_output_gate.py'); g=importlib.util.module_from_spec(sp); sp.loader.exec_module(g)
H='tools/s7752_port_task/harness'; cap,tg=1048576,1
def rep(s,out):
    env=dict(os.environ,ROGUESQ_UCODE_CAP=str(cap),ROGUESQ_G5B_TG_FIX=str(tg)); env.pop('S7752_G1E_FAST',None)
    p=subprocess.run([H,s,out],env=env,capture_output=True,text=True,timeout=300)
    m=re.search(r'tg_hits=(\d+) cap_fires=(\d+)',p.stderr)
    return (open(out,'rb').read() if p.returncode==0 else b''), (m.groups() if m else p.stderr[-150:])
for s in sorted(glob.glob((sys.argv[1] if len(sys.argv)>1 else 'scratch/s7754/w219/snap')+'/k900_s*[0-9].bin'), key=lambda p:int(re.search(r'_s(\d+)',p).group(1))):
    live=g.tail(s); b,mb=rep(s,'/tmp/s7757_b.rdp'); e,me=rep(s[:-4]+'_end.bin','/tmp/s7757_e.rdp')
    print(os.path.basename(s),'live',len(live),'beg',('EQ' if b==live else 'DIFF'),'end',('EQ' if e==live else 'DIFF'),'b==e',b==e,'tg/cap',mb,flush=True)
