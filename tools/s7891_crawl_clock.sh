#!/bin/zsh
# s7891 G3 island A (pre-flight half-frame, s7870-s7874): guest-RAM time state at the crawl/cinematic dt sites, retail vs port.
# Both menu-overlay advanceWrappingPhaseAccumulator (mark 0x800C6674) and cinematic-overlay cinematicComputeDt (mark 0x800AF374)
# quantize timeSnapshotFiller's stored value (struct sp+0x10, +0x20 value, +0x1C period) to whole VIs and bump the call counter
# 0x8013889C. Dumps per call: struct (12 w), counter, caller's saved ra (sp+0x38; retail only, N64Recomp leaves $ra unset),
# cinematic accumulators 0x800B0B2C / 0x80130BA4 (cinematicLoopBody += dt). Retail: rs64_oracle exec-trace rows; port:
# ROGUESQ_RAND_TRACE marker rows (tools/fixup_rand_trace.py s6752). Scorer: tools/s7891_crawl_clock_cmp.py.
# usage: zsh tools/s7891_crawl_clock.sh OUTDIR [EEP=scratch/s7872/v10/lvl.eep SECS=130 SNAP=1]  (s7892: SNAP= sets the port RETAIL_SNAP, unset = 1)
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
O=${1:?OUTDIR}; mkdir -p $O; A=$PWD/$O; SECS=${SECS:-130}; EEP=${EEP:-scratch/s7872/v10/lvl.eep}; cp $EEP $O/lvl.eep || exit 3
M="800C6674:29:10:12,800C6674:0:8013889C:1,800C6674:29:38:1,800AF374:29:10:12,800AF374:0:8013889C:1,800AF374:0:800B0B2C:1,800AF374:0:80130BA4:1,800AF374:29:38:1"
if [[ ! -s $O/r1/oracle.log ]]; then
env CPO=1 RSECS=$SECS EEP=$O/lvl.eep PP=19.5:start,31.5:start,43.5:start,67.5:start,79.5:start,91.5:start RDPBIN=/dev/null \
  RS64_XTRACE_MEM=$M XO="--exec-trace 0x800AF408:8000000 --exec-trace-also 0x800C6674 --exec-trace-also 0x800AF374" \
  zsh tools/s7828_retail_cpo.sh $O/r1 > $O/r1.out 2>&1
fi
AP=6:start,11:start,11.5:w1024,19.5:start,31.5:start,43.5:start,67.5:start,79.5:start,91.5:start
B="ROGUESQ_AUTOPILOT_CLOCK=vi ROGUESQ_S7835_DT=1 ROGUESQ_VI_STAMP=1 ROGUESQ_RETAIL_SNAP=${SNAP:-1} ROGUESQ_RAND_TRACE_BOOT=1 ROGUESQ_RAND_TRACE_MAX=8000000 ROGUESQ_XTRACE_MEM=$M"
[[ -s $O/p1_rand.txt ]] || env SAVE_FROM=$O/lvl.eep SECS=$SECS CAP0=$((SECS-3)) AP=$AP XE="$B ROGUESQ_RAND_TRACE=$A/p1_rand.txt" zsh tools/g3_port_capture.sh $O/p1 > $O/p1.out 2>&1
echo "crashlines $(grep -c 'CRASH\|SIGSEGV\|SIGBUS\|abort' $O/p1/run.log)"
python3 tools/s7891_crawl_clock_cmp.py $O/r1/oracle.log $O/p1_rand.txt | tee $O/score.txt
