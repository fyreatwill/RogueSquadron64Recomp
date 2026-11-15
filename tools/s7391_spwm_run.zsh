#!/bin/zsh
# s7391 stack low-water run: build_spwm binary, owner-save COPY (build_spwm/saves, read-only), s7386 keyed route
# (level select -> LDESC -> craft -> crawl -> intro cutscene -> flight -> pause -> abort -> MISSION FAILED -> debrief),
# dd8 21:9 FPS60, with the positive control range armed. usage: tools/s7389_fbld_run.zsh <outdir> "<extra env>"
cd "${0:A:h}/.."
O=${1:-scratch/s7391/run}; mkdir -p $O build_spwm/saves
[ -f build_spwm/saves/rs64.n64.us.1.0.bin ] || cp build/saves/rs64.n64.us.1.0.bin build_spwm/saves/ || exit 3
AP=${AP:-6:start,11:start,16:start,21:start,25:left,27:start,31:cup,43:cup,47:start,58:a,64:a,70:a,140:start,144:down,148:a,152:left,155:a,165:a,173:a,181:a}
( cd build_spwm && exec env ROGUESQ_NO_PKILL=1 ROGUESQ_NO_SAVE_WRITE=1 ROGUESQ_AUTOPILOT=$AP ROGUESQ_LOG_PHASE=1 \
  ROGUESQ_AUTOPILOT_HOLD_MS=250 ROGUESQ_FPS60=1 ROGUESQ_DRAW_DISTANCE=8 ROGUESQ_DD_UNSAFE=1 ROGUESQ_DD_WIDEWIN=1 \
  ROGUESQ_ASPECT=21:9 ROGUESQ_S7391_SPWM=1 ${=2} ./RogueSquadron64Recomp ) > $O/run.log 2>&1 &
P=$!
SECS=${SECS:-200}; s=0
while (( s < SECS )) && kill -0 $P 2>/dev/null; do sleep 1; s=$((s+1)); done
kill -9 $P 2>/dev/null; wait $P 2>/dev/null
echo "s7391 run: secs=$s crash=$(grep -a -c 'CRASH\|SIGSEGV\|SIGBUS' $O/run.log) recs=$(grep -a -c "^\[s7391-sp\]" $O/run.log)"
python3 tools/s7391_spwm_report.py $O/run.log
