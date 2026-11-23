#!/bin/zsh
# s7856: serial G3 retail-flight det sweep over several 0x31 values (one game/oracle at a time, iron rule 0).
# usage: zsh tools/s7856_det_sweep.sh OUTROOT <v> [<v> ...]     e.g. zsh tools/s7856_det_sweep.sh scratch/s7857 13 14
# Each value runs tools/s7849_det_pair.sh into OUTROOT/v<v>, then tools/s7856_det_verdict.py appends one line to
# OUTROOT/verdicts.txt. Stops at the first FORK (that level needs a hand diagnosis, H-audio-clock/H-pin-gap/H-new-fork);
# NO-VERDICT continues (record it, rerun later). Exit: 0 all H-exact, 1 a FORK stopped the sweep, 2 any NO-VERDICT.
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
R=${1:?usage: s7856_det_sweep.sh OUTROOT v...}; shift; mkdir -p $R; rc=0
for v in "$@"; do
  zsh tools/s7849_det_pair.sh $v $R/v$v > $R/v$v.drv.log 2>&1
  python3 tools/s7856_det_verdict.py $R/v$v/score.txt --tag 0x31=$v | tee -a $R/verdicts.txt; e=${pipestatus[1]}
  (( e == 1 )) && exit 1
  (( e == 2 )) && rc=2
done
exit $rc
