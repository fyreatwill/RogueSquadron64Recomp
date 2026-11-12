#!/bin/zsh
# s7177: full retail-4:3 post chain for one level (s7141_post + fsum + rectfit). usage: env FID_MAINRUN=1 zsh tools/s7177_post_lvl.zsh <lvl>
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
L=$1; N=L${L}${SFX:-r}; D=scratch/s7141
zsh tools/s7141_post.zsh $D $N 0,10,308,241 103,205 > $D/post_$N.log 2>&1
grep -i 'control' $D/post_$N.log | tail -2
python3 tools/s7157_fsum.py $D/$N.frames.csv $D/${N}_sh2.frames.csv
python3 tools/s7163_rectfit.py $D/$N.raw $D/${N}r $D/$N.frames.csv 0,10,308,241 --every 8 > $D/rectfit_$N.log 2>&1; tail -6 $D/rectfit_$N.log
