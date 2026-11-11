#!/bin/zsh
# s7139: s7136_post restricted to RAM-owning swaps >= MIN (EVERY=20 captures; skips menu/boot swaps). usage: s7139_post.zsh <dir> <name> <minswap>
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
D=$1; N=$2; MIN=${3:-0}; AL=scratch/s7124/al16/frame_replay16
[ -f $D/$N.idx ] || python3 tools/s7098_rt64_vs_al.py index $D/$N.cap $D/$N.idx
awk -v m=$MIN '$5==1 && $1>=m {print $1}' $D/$N.idx > $D/$N.swaps
mkdir -p $D/${N}r; rm -f $D/chunk${N}_*
split -l 30 $D/$N.swaps $D/chunk${N}_
for c in $D/chunk${N}_??; do
  while [ $(jobs -r | wc -l) -ge 4 ]; do /bin/sleep 2; done
  $AL $D/$N.cap $D/${N}r $(cat $c) > $c.log 2>&1 &
done
wait
cat $D/chunk${N}_??.log | grep '^swap' > $D/${N}r.log
python3 tools/s7133_rects.py $D/$N.cap $(cat $D/$N.swaps) > $D/$N.rects
python3 tools/s7134_score.py $N $D/${N}r.log $D/$N.rects
