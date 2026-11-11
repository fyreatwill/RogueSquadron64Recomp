#!/bin/zsh
# s7152: s7141_post for menu/title captures. Replays every RAM swap twice with angrylion: default (magenta pre-fill = painted control)
# and NOPREFILL=1 (undrawn pixels keep the RAM snapshot's colour image). Title/main-menu/profile frames alpha-blend their backdrop
# over memory and paint only the 512-px centre band of a 1024x448 fb, so their pre-fill replay is magenta-tinted and load_al drops it;
# 336-row fbs (level select, hangar) must use the pre-fill replay (NOPREFILL rows below 336 are stale RAM and break the row crop).
# The combined dir <name>c takes the pre-fill replay wherever load_al accepts it, else the NOPREFILL one.
# usage: s7152_post.zsh <dir> <name> <rect x0,y0,x1,y1> <split cx0,cx1>
setopt nonomatch
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
D=$1; N=$2; RECT=$3; SPLIT=$4; AL=scratch/s7124/al16/frame_replay16
[ -f $D/$N.idx -a ! $D/$N.cap -nt $D/$N.idx ] || python3 tools/s7098_rt64_vs_al.py index $D/$N.cap $D/$N.idx
awk '$5==1 {print $1}' $D/$N.idx > $D/$N.swaps
for M in r n; do
  mkdir -p $D/${N}$M; rm -f $D/chunk${N}${M}_*; split -l 60 $D/$N.swaps $D/chunk${N}${M}_
  for c in $D/chunk${N}${M}_??; do
    while [ $(jobs -r | wc -l) -ge 4 ]; do /bin/sleep 2; done
    if [ $M = n ]; then env NOPREFILL=1 $AL $D/$N.cap $D/${N}$M $(cat $c) > $c.log 2>&1 &
    else $AL $D/$N.cap $D/${N}$M $(cat $c) > $c.log 2>&1 &; fi
  done
  wait; cat $D/chunk${N}${M}_??.log | grep '^swap' > $D/${N}$M.log
done
python3 - $D $N <<'P'
import sys, os; sys.path.insert(0, 'tools'); from s7122_fidelity import load_al
D, N = sys.argv[1:3]; c = '%s/%sc' % (D, N); os.makedirs(c, exist_ok=True); k = {'r': 0, 'n': 0}
for fn in os.listdir('%s/%sn' % (D, N)):
    d = os.path.join(c, fn)
    if os.path.lexists(d): os.remove(d)
    m = 'r' if os.path.exists('%s/%sr/%s' % (D, N, fn)) and load_al('%s/%sr/%s' % (D, N, fn)) is not None else 'n'
    os.symlink('../%s%s/%s' % (N, m, fn), d); k[m] += 1
print('combined: prefill', k['r'], 'noprefill', k['n'])
P
python3 tools/s7122_fidelity.py control $D/${N}r
python3 tools/s7122_fidelity.py score $D/$N.raw $D/$N.idx $D/${N}c $D/${N}C --rect $RECT --split $SPLIT
python3 tools/s7122_fidelity.py score $D/$N.raw $D/$N.idx $D/${N}c $D/${N}C_sh2 --rect $RECT --split $SPLIT --shift 2
