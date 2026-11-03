#!/bin/zsh
# s6834: catch the rare title-boot freeze (s6814 a30_s2: RDP frames stopped at fs=39 / VI 128, VI origin 0x006BA280 held
# 215 s, audio kept flowing, no crash line; 1 in 11 boots) in the act. Boots the game N times (retail settings plus
# ROGUESQ_LOG_PHASE=1 for the [vi] fs= counter). A boot is FROZEN when fs has not advanced for STALL s (or is still <200
# at BOOT_SECS). On a freeze: two `sample` call-tree captures 5 s apart (stuck vs spinning), the per-thread summary
# (tools/sample_game_threads.py), the log tail, then SIGKILL; exit 1. Healthy boots keep only a 200-line log tail.
# Positive control: boot 1 is also sampled while healthy, and its summary must name a [Game] thread.
# Freeze-path control: HUNT_SELFTEST=1 SIGSTOPs boot 1 at 18 s (SIGCONT before sampling) - it must report FROZEN.
# Usage (repo root): tools/boot_freeze_hunt.sh <outdir> [boots=12] [boot_secs=40] [stall=12]
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
O=${1:?outdir}; N=${2:-12}; BOOT_SECS=${3:-40}; STALL=${4:-12}; mkdir -p $O; bad=0
fsof() { grep -a -o 'fs=[0-9]*' $1 2>/dev/null | tail -1 | cut -d= -f2; }
for i in $(seq 1 $N); do
  L=$O/boot$i.log
  ( cd build && exec env ROGUESQ_NO_PKILL=1 ROGUESQ_LOG_PHASE=1 ./RogueSquadron64Recomp ) > $L 2>&1 &
  P=$!; t=0; last=-1; since=0; st=OK
  while (( t < BOOT_SECS )); do
    sleep 2; t=$(( t + 2 ))
    [[ -n $HUNT_SELFTEST && $i == 1 && $t == 18 ]] && kill -STOP $P
    kill -0 $P 2>/dev/null || { st=EXITED; break; }
    fs=$(fsof $L); fs=${fs:-0}
    if (( fs != last )); then last=$fs; since=$t; fi
    if (( t - since >= STALL && t >= 16 )); then st=FROZEN; break; fi
    if (( i == 1 && t == 20 )); then
      sample $P 2 -file $O/ctl_boot1.sample.txt >/dev/null 2>&1
      python3 tools/sample_game_threads.py $O/ctl_boot1.sample.txt 12 > $O/ctl_boot1.threads.txt
      echo "control boot1: sample $(grep -c '^== \[Game\]' $O/ctl_boot1.threads.txt) [Game] threads named"
    fi
  done
  fs=$(fsof $L); fs=${fs:-0}
  [[ $st == OK ]] && (( fs < 200 )) && st=FROZEN
  if [[ $st == FROZEN ]]; then
    bad=1; [[ -n $HUNT_SELFTEST ]] && kill -CONT $P
    sample $P 3 -file $O/boot${i}_freeze_a.sample.txt >/dev/null 2>&1
    sleep 5
    sample $P 3 -file $O/boot${i}_freeze_b.sample.txt >/dev/null 2>&1
    for s in a b; do python3 tools/sample_game_threads.py $O/boot${i}_freeze_$s.sample.txt 14 > $O/boot${i}_freeze_$s.threads.txt; done
    tail -c 2000000 $L > $O/boot${i}_freeze.tail.log
  fi
  kill -9 $P 2>/dev/null; wait $P 2>/dev/null
  crash=$(grep -a -c -i 'SIGSEGV\|SIGBUS\|abort\|CRASH' $L)
  (( crash > 0 )) && { bad=1; grep -a -i -m5 'SIGSEGV\|SIGBUS\|abort\|CRASH' $L > $O/boot${i}_crash.txt; }
  vo=$(tail -c 400000 $L | grep -a -o 'origin=0x[0-9A-Fa-f]*' | tail -1)
  [[ $st == FROZEN ]] || { tail -200 $L > $O/boot$i.tail.log; rm -f $L; }
  echo "boot$i fs=$fs t=$t $vo crash=$crash $st"
done
exit $bad
