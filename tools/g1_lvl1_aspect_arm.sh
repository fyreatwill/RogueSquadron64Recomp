#!/bin/zsh
# s6688 arm: forced lvl1 route at <aspect>, extra env; prints keys.log verdict + crash frames.
# Usage: arm.sh <tag> <aspect> "<extra env>"
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
T=$1; A=$2; X=$3
env ROGUESQ_NO_PKILL=1 TITLE_ORIGIN='0x[0-9A-F]*' MISSION_RE='[0-9A-F]+' \
  XENV_EXTRA="ROGUESQ_ASPECT=$A $X" HOLD_S=${HOLD_S:-90} LEVEL=1 TAG_SUFFIX=s6688_$T \
  zsh scratch/agent/g1_level_coverage_common.zsh > scratch/agent/m6/s6688_$T.runner.log 2>&1
D=scratch/agent/m6/g1_lvl1s6688_$T
echo "== $T"; cat $D/keys.log
for f in $D/fail_att*.log $D/run.log; do [ -f $f ] && echo "$f: $(grep -a -m1 'caught signal' $f | cut -c10-45) $(grep -a -m1 -E '^3 +RogueSquadron64Recomp' $f | awk '{print $4}') $(grep -a -m1 '\[g1f\] window' $f)"; done
