#!/bin/zsh
# s6863: scratch-only replay of the full chain with a per-script trace. Never touches the live tree (hash checked).
cd "$(dirname "$0")/../.." || exit 2
LIVE=../N64Recomp/RecompiledFuncs; SRC=../N64Recomp/scratch_s5547_regen; D=../N64Recomp/scratch_s6863_replay; O=scratch/s6863
(cd $LIVE && cat *.c *.h 2>/dev/null | shasum) > $O/live_before.sha
rm -rf "$D"; ditto $SRC "$D" || exit 3
rm -f $O/trace.jsonl; date > $O/t0
rm -f $O/fixup.log; env RS64_REPLAY_TRACE=$PWD/$O/trace.jsonl tools/regen_replay.sh "$D" $PWD/$O/fixup.log | tee $O/rc
(cd $LIVE && cat *.c *.h 2>/dev/null | shasum) > $O/live_after.sha
date >> $O/t0
for f in $LIVE/*; do b=${f:t}; n=$(diff "$D/$b" "$f" 2>&1 | grep -c '^[<>]'); [ "$n" -gt 0 ] && echo "$b $n"; done | sort -k2 -nr > $O/diffsummary.txt
wc -l $O/diffsummary.txt; cat $O/rc; cmp $O/live_before.sha $O/live_after.sha && echo LIVE_UNCHANGED
