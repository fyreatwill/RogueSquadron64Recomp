#!/bin/zsh
# s7505 class FC: over a whole run, how often does ANY live heap header sit on a scanned pixel of the committed VI fb? Wraps
# tools/s7504_fb_recipe.zsh with ROGUESQ_S7505_FC=1 (main.cpp s7505_fc, per swap from rs64_s7503_swap; chain walk upstream_compat
# rs64_s7496_overlap). Per arm: last `[s7505] fc sum` + episode rows (`[s7505] ep`: header in-window for `shown` consecutive swaps,
# frame mean luma ml). Exit 0 = every arm: synth>0, ctl_sw>0 and every non-bad ctl walk hit, and no episode on a lit frame (ml>0.05) or
# shown >2 swaps; 5 = some lit/long episode (read the rows); 3 = control FAIL / no sum; 2 = human-active void.
# SOAK_NEEDS_IDLE=180
# SOAK_TIMEOUT=1400
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp || exit 1
n=${NAME:-s7505_fc}; R=$PWD/scratch/$n
env NAME=$n XC="ROGUESQ_S7505_FC=1${XC:++$XC}" LV="${LV:-4:1:os_rt64fb 15:8:os_rt64fb}" zsh tools/s7504_fb_recipe.zsh; rc=$?
(( rc == 2 )) && exit 2
sr=0
for L in $R/log_l*.txt(N); do a=${${L:t:r}#log_}
  s=$(python3 - "$L" <<'PY'
import re,sys
sm=None;eps=[]
for ln in open(sys.argv[1],errors='replace'):
    if '[s7505] fc sum ' in ln: sm=dict(re.findall(r'(\w+)=(\S+)',ln))
    elif '[s7505] ep ' in ln: eps.append(dict(re.findall(r'(\w+)=(\S+)',ln)))
if not sm: print("nosum ctl=FAIL"); sys.exit()
sy,syn=map(int,sm['synth'].split('/')); ch,cs=map(int,sm['ctl'].split('/')); cb=int(sm['ctlbad'])
ok = sy>0 and cs>0 and ch>=cs-cb and ch>0
bad=[e for e in eps if e['lit']=='1' or e['long']=='1']
print(f"swaps={sm['swaps']} novi={sm['novi']} bad={sm['bad']} hits={sm['hits']} eps={sm['eps']} lit={sm['lit']} long={sm['long']} maxml={sm['maxml']} synth={sm['synth']} ctl={sm['ctl']} ctlbad={cb} ctl={'ok' if ok else 'FAIL'} rows="+";".join(f"{e['hdr']}:fl{e['fl']}:x{e['x']}y{e['y']}:n{e['shown']}:t{e['t']}:ml{e['ml']}:h{e['hlum']}/{e['ring']}" for e in eps[:12]) + (" BAD="+";".join(f"{e['hdr']}:t{e['t']}:ml{e['ml']}:n{e['shown']}" for e in bad[:12]) if bad else ""))
PY
)
  echo "tag=$n fc arm=$a $s" | tee -a $R/out.txt
  [[ $s == *ctl=FAIL* ]] && sr=3
  (( sr == 0 )) && [[ $s != *" lit=0 long=0 "* ]] && sr=5
done
echo "$n fc score=$sr" | tee -a $R/out.txt
(( rc != 0 && rc != 3 && rc != 4 && rc != 5 )) && exit $rc
exit $sr
