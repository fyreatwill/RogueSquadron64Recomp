#!/bin/zsh
# s7504 class FB: is the allocator header RT64 uploads on the present path (s7503 shape 1, coalesceFreeHeapBlocks pair at the mission
# load) inside the VI scanout window, and does it stand out against the frame around it? Wraps tools/s7503_fa_recipe.zsh with
# ROGUESQ_S7504_FB=1 (main.cpp s7504_fb, called from rs64_s7501_up on present-path allocator uploads; tag=ctl = the committed VI fb at
# t>=35 s). PPMs of each VI window in scratch/$NAME/ppm. Per hdr row: inwin, contrast = max |header pixel luma - ring mean luma|.
# Exit 0 = every arm: ctl ok (nz_pm>=100, ncol>=32) and every hdr row invisible (inwin=0 or contrast<0.05); 5 = some header visible
# (read the rows); 3 = control FAIL / no hdr row; 2 = human-active void.
# SOAK_NEEDS_IDLE=180
# SOAK_TIMEOUT=1400
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp || exit 1
n=${NAME:-s7504_fb}; R=$PWD/scratch/$n; mkdir -p $R/ppm
env NAME=$n XC="ROGUESQ_S7504_FB=1+ROGUESQ_S7504_DIR=$R/ppm${XC:++$XC}" LV="${LV:-4:1:os_rt64fb 15:8:os_rt64fb}" zsh tools/s7503_fa_recipe.zsh; rc=$?
(( rc == 2 )) && exit 2
sr=0
for L in $R/log_l*.txt(N); do a=${${L:t:r}#log_}
  s=$(python3 - "$L" <<'PY'
import re,sys
hdr=[];ctl=None;ctls=[]
for ln in open(sys.argv[1],errors='replace'):
    if '[s7504] fb ' not in ln: continue
    d=dict(re.findall(r'(\w+)=(\S+)',ln))
    if d["tag"]=="ctl": ctls.append(d); ctl=max(ctls,key=lambda c:int(c["ncol"])); continue
    hl=[float(x) for x in d['hlum'].split(',')]; ring=float(d['ring'])
    c=max(abs(x-ring) for x in hl) if int(d['nr'])>0 else 0.0
    hdr.append((d['fb'],d['inwin'],round(c,3),d['hx'],d['hy'],d['cols'],d['rows'],d['words'],d['meanlum']))
ok = any(int(c["nz_pm"])>=100 and int(c["ncol"])>=32 for c in ctls)
vis=sum(1 for h in hdr if h[1]=='1' and h[2]>=0.05)
print(f"hdr={len(hdr)} vis={vis} ctl={'ok' if ok else 'FAIL'} ctl_nz={ctl['nz_pm'] if ctl else '-'} ctl_ncol={ctl['ncol'] if ctl else '-'} rows="+";".join(f"{h[0]}:in{h[1]}:c{h[2]}:x{h[3]}y{h[4]}:win{h[5]}x{h[6]}:w{h[7]}:ml{h[8]}" for h in hdr))
PY
)
  echo "tag=$n fb arm=$a $s" | tee -a $R/out.txt
  [[ $s == *ctl=FAIL* || $s == hdr=0\ * ]] && sr=3
  (( sr == 0 )) && [[ $s != *" vis=0 "* ]] && sr=5
done
echo "$n fb score=$sr" | tee -a $R/out.txt
(( rc != 0 && rc != 3 && rc != 4 && rc != 5 )) && exit $rc
exit $sr
