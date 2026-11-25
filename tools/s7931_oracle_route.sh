#!/bin/zsh
# s7931: settle s7928's single-source route reading (port 3 menuOverlayInit transitions between initScenes vs retail 4).
# Retail oracle (Rice, HLE RSP, wall clock, as s7928) with a PRIVATE copy of the owner's save (build/saves is only read) and
#   arm portOFF<o> : the port autopilot press schedule of tools/g1e_owner_quiet_arms.zsh (EARLY block, start/z, hold 1800 ms) + o s
#   arm s7928sched : s7928's schedule (start every 6 s from 6, A every 6 s from 9) -> isolates save vs schedule vs s7928_oracle
# Each arm: oracle.log with runVideoFrameTick entry (0x80001354) + wait-taken (0x80091EC4) hits; score with
#   python3 tools/s7928_gate_writers.py <port ring> --oracle <arm>/oracle.log
# Usage: zsh tools/s7931_oracle_route.sh <outdir> [arms...]   (arms default: port7.3 port5.75 s7928sched)
set -u
O=${1:?outdir}; shift; ARMS=("$@"); (( ${#ARMS} )) || ARMS=(port7.3 port5.75 s7928sched)
pgrep -x rs64_oracle >/dev/null && { echo "rs64_oracle already running" >&2; exit 4; }
C=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib
R=/Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64
V=/opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib
H=/opt/homebrew/lib/mupen64plus/mupen64plus-rsp-hle.dylib
SAVE=${SAVE:-build/saves/rs64.n64.us.1.0.bin}
for arm in $ARMS; do
  D=$O/$arm; mkdir -p $D/savedir; SD=$(cd $D && pwd)/savedir
  cp $SAVE "$SD/Star Wars - Rogue Squadron (U) (-47CAC4E2.eep" || exit 3
  case $arm in
    port*) off=${arm#port}; P=""; e=10
      for i in $(seq 1 20); do if (( i % 2 == 0 || e > 74 )); then k=z; else k=start; fi; P="$P$(python3 -c "print('%g'%($e+$off))"):$k,"; e=$((e+4)); done
      P=${P%,}; HOLD=1800;;
    s7928sched) P=$(python3 -c "
ev=[(t,'start') for t in range(6,88,6)]+[(t,'a') for t in range(9,88,6)]
print(','.join('%d:%s'%e for e in sorted(ev)))"); HOLD=150;;
    *) echo "unknown arm $arm" >&2; exit 2;;
  esac
  echo "$arm press=$P hold=$HOLD save=$SAVE" > $D/press.txt
  tools/oracle/build/rs64_oracle --save-dir $SD --core $C --rom $R --secs ${SECS:-110} --vi-poll --vi-trace --rsp $H --video $V \
    --press $P --hold-ms $HOLD --watch-pc 0x80001354,0x80091EC4 --hit-vi --hit-cap 64 > $D/oracle.log 2>&1
  echo "$arm rc=$? ticks=$(grep -c 'pc=0x80001354 prev' $D/oracle.log) waits=$(grep -c 'pc=0x80091ec4 prev' $D/oracle.log)"
done
