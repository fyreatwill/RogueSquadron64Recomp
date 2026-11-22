#!/bin/zsh
# s7141: replay every RAM-owning swap of an EVERY=1 G5B capture with angrylion (JOBS=2 parallel chunks of 60, iron rule 0) and score RT64 vs angrylion
# with the central-band split. usage: s7141_post.zsh <dir> <name> <rect x0,y0,x1,y1> <split cx0,cx1>
setopt nonomatch
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
D=$1; N=$2; RECT=$3; SPLIT=$4; AL=scratch/s7124/al16/frame_replay16
[ -f $D/$N.idx -a ! $D/$N.cap -nt $D/$N.idx ] || python3 tools/s7098_rt64_vs_al.py index $D/$N.cap $D/$N.idx
awk '$5==1 {print $1}' $D/$N.idx > $D/$N.swaps
mkdir -p $D/${N}r; rm -f $D/chunk${N}_*
split -l 60 $D/$N.swaps $D/chunk${N}_
for c in $D/chunk${N}_??; do
  while [ $(jobs -r | wc -l) -ge ${JOBS:-2} ]; do /bin/sleep 2; done
  $AL $D/$N.cap $D/${N}r $(cat $c) > $c.log 2>&1 &
done
wait
cat $D/chunk${N}_??.log | grep '^swap' > $D/${N}r.log
python3 tools/s7122_fidelity.py control $D/${N}r
python3 tools/s7122_fidelity.py score $D/$N.raw $D/$N.idx $D/${N}r $D/$N --rect $RECT --split $SPLIT
python3 tools/s7122_fidelity.py score $D/$N.raw $D/$N.idx $D/${N}r $D/${N}_sh2 --rect $RECT --split $SPLIT --shift 2
