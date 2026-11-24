#!/bin/zsh
# s7891 G3 island A fix arm: the s7849 v10 (0x31=10) p1 recipe with ROGUESQ_RETAIL_SNAP=<SNAP, default 2> instead of =1, RDP stream kept,
# plus the s7891 crawl/cinematic dt dumps. Scores: island A + flight render vs the retained retail bin (s7868 cmp), det ticks vs the
# retained oracle log (s7845), crawl dt vs the s7891 retail oracle log (s7891 cmp).
# usage: zsh tools/s7891_fix_arm.sh OUTDIR [SNAP=2] [R=scratch/s7872/v10] [RC=scratch/s7891/a/r1/oracle.log]
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
O=${1:?OUTDIR}; mkdir -p $O; A=$PWD/$O; SNAP=${SNAP:-2}; R=${R:-scratch/s7872/v10}; RC=${RC:-scratch/s7891/a/r1/oracle.log}
source $R/pins.txt; SECS=${SECS:-305}
M="800C6674:29:10:12,800C6674:0:8013889C:1,800AF374:29:10:12,800AF374:0:8013889C:1,800AF374:0:800B0B2C:1,800AF374:0:80130BA4:1"
B="ROGUESQ_AUTOPILOT_CLOCK=vi ROGUESQ_S7834_RAMDUMP=1 ROGUESQ_G3C_CAMLOG=1 ROGUESQ_S7835_DT=1 ROGUESQ_VI_STAMP=1 ROGUESQ_RETAIL_SNAP=$SNAP ROGUESQ_RAND_TRACE_BOOT=1 ROGUESQ_RAND_TRACE_MAX=8000000 ROGUESQ_XTRACE_MEM=800FA730:0:80137E7C:1,800FA730:0:80003470:1,800FA730:0:8010C0E0:1,$M"
AP=6:start,11:start,11.5:w1024,19.5:start,31.5:start,43.5:start,67.5:start,79.5:start,91.5:start
[[ -s $O/p1.bin ]] || env SAVE_FROM=$R/lvl.eep SECS=$SECS CAP0=$((SECS-3)) AP=$AP XE="$B ROGUESQ_RAND_TRACE=$A/p1_rand.txt ROGUESQ_XTRACE_POKE=800FA730:0:80003470:$SEED:1 ROGUESQ_S7844_DT_AT=$DT_AT RS64_RDP_BIN_PORT=$A/p1.bin RS64_RDP_BIN_PORT_MAX_MB=6000" zsh tools/g3_port_capture.sh $O/p1 > $O/p1.out 2>&1
{ echo "crashlines $(grep -c 'CRASH\|SIGSEGV\|SIGBUS\|abort' $O/p1/run.log)"; grep -m6 'snap7891\|snap7839\] armed' $O/p1/run.log
  echo "=== s7891 crawl dt vs retail"; python3 tools/s7891_crawl_clock_cmp.py $RC $O/p1_rand.txt | grep -E 'seg|control'
  echo "=== s7845 det ticks"; python3 tools/s7845_rng_tick_cmp.py $R/r1/oracle.log $O/p1_rand.txt | head -12
  echo "=== s7868 render"; python3 tools/s7868_det_frame_cmp.py $R/r1/retail.bin $O/p1.bin --plant; } > $O/score.txt 2>&1
echo done
