#!/bin/zsh
# s6834: catch the rare title-boot freeze (s6814 a30_s2: RDP frames stopped at fs=39 / VI 128, VI origin 0x006BA280 held
# 215 s, audio kept flowing, no crash line; 1 in 11 boots) in the act. Boots the game N times (retail settings plus
# ROGUESQ_LOG_PHASE=1 for the [vi] fs= counter). A boot is FROZEN when fs has not advanced for STALL s (or is still <200
# at BOOT_SECS). On a freeze: two `sample` call-tree captures 5 s apart (stuck vs spinning), the per-thread summary
# (tools/sample_game_threads.py), the log tail, then SIGKILL; exit 1. Healthy boots keep only a 200-line log tail.
# Positive control: boot 1 is also sampled while healthy, and its summary must name a [Game] thread.
# Freeze-path control: HUNT_SELFTEST=1 SIGSTOPs boot 1 at 18 s (SIGCONT before sampling) - it must report FROZEN.
# Usage (repo root): tools/boot_freeze_hunt.sh <outdir> [boots=12] [boot_secs=40] [stall=12]
# s6835: HUNT_ENV="K=V ..." adds env to every boot; the runtime [stall-dump] (arbiter slot states + video, frame-sync and
# retrace VI queues with their waiting thread) lands in boot*_freeze.tail.log and is echoed on the FROZEN line.
# s7190: HUNT_CONTROL=1 makes boot 1 a non-failing positive control for BOTH capture paths: it runs with
# ROGUESQ_STALL_DUMP_TEST=300 (the runtime's forced [stall-dump] must write its detached self-sample
# rs64_stall_*.sample.txt into ROGUESQ_STALL_SAMPLE_DIR) and is SIGSTOPped at 18 s (the hunter must call it FROZEN).
# Prints "CONTROL dump=PASS|FAIL frozen=PASS|FAIL"; a control FAIL exits 3 (instrument broken, nulls void), a control
# PASS does not count as a freeze. ROGUESQ_STALL_SAMPLE_DIR defaults to <outdir> for every boot.
# HUNT_OWNER=1 adds the s6993 freeze env (owner recipe as run by tools/g1e_owner_quiet_arms.zsh arm L4).
# s7453 class DI: a boot that EXITS before BOOT_SECS is a death (bad=1, st=EXITED exitrc=<status>) even with no crash text, and
# crash= is the shared tools/agent/fatal_scan.sh count (was CRASH|SIGSEGV|SIGBUS|abort: missed quick_exit/switch_error exits).
# GAMEDIR/GAME override the binary (fake-binary control: tools/s7453_harness_death_test.zsh).
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
O=${1:?outdir}; N=${2:-12}; BOOT_SECS=${3:-40}; STALL=${4:-12}; _c=$(sh "$(git rev-parse --show-toplevel)/tools/agent/run_dir_guard.sh" "$O") || { echo "tools/boot_freeze_hunt.sh: $_c (s7952: outdir differs from an existing dir only by case; rename)" >&2; exit 3; }; mkdir -p $O; O=${O:A}; bad=0; ctlbad=0
OWNER_ENV="ROGUESQ_FORCE_SAVE_MISSION=4 ROGUESQ_FORCE_UNLOCK=4 ROGUESQ_NO_SAVE_WRITE=1 ROGUESQ_GODMODE=1 ROGUESQ_FPS60=1 ROGUESQ_DRAW_DISTANCE=4 ROGUESQ_ASPECT=16:9 ROGUESQ_FULLSCREEN=1 ROGUESQ_VI_LOCK=1 ROGUESQ_VI_LOCK_TARGET_MS=10 ROGUESQ_QOS_ALL=1 ROGUESQ_G1B=1"
[[ -n $HUNT_OWNER ]] && HUNT_ENV="$OWNER_ENV $HUNT_ENV"
[[ -n $HUNT_CONTROL ]] && HUNT_SELFTEST=1
fsof() { grep -a -o 'fs=[0-9]*' $1 2>/dev/null | tail -1 | cut -d= -f2; }
for i in $(seq 1 $N); do
  L=$O/boot$i.log
  CE=""; [[ -n $HUNT_CONTROL && $i == 1 ]] && CE="ROGUESQ_STALL_DUMP_TEST=300"
  ( cd ${GAMEDIR:-build} && exec env ROGUESQ_NO_PKILL=1 ROGUESQ_LOG_PHASE=1 ROGUESQ_STALL_SAMPLE_DIR=$O ${=HUNT_ENV} ${=CE} ${GAME:-./RogueSquadron64Recomp} ) > $L 2>&1 &
  P=$!; t=0; last=-1; since=0; st=OK
  while (( t < BOOT_SECS )); do
    sleep 2; t=$(( t + 2 ))
    [[ -n $HUNT_SELFTEST && $i == 1 && $t == 18 ]] && kill -STOP $P
    kill -0 $P 2>/dev/null || { wait $P 2>/dev/null; st="EXITED exitrc=$?"; bad=1; break; }
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
    bad=1; [[ -n $HUNT_SELFTEST && $i == 1 ]] && kill -CONT $P
    sample $P 3 -file $O/boot${i}_freeze_a.sample.txt >/dev/null 2>&1
    sleep 5
    sample $P 3 -file $O/boot${i}_freeze_b.sample.txt >/dev/null 2>&1
    for s in a b; do python3 tools/sample_game_threads.py $O/boot${i}_freeze_$s.sample.txt 14 > $O/boot${i}_freeze_$s.threads.txt; done
    tail -c 2000000 $L > $O/boot${i}_freeze.tail.log
  fi
  kill -9 $P 2>/dev/null; wait $P 2>/dev/null
  FP=tools/agent/fatal_patterns.txt; crash=$(grep -a -c -E -f $FP $L)
  (( crash > 0 )) && { bad=1; grep -a -E -m5 -f $FP $L > $O/boot${i}_crash.txt; }
  vo=$(tail -c 400000 $L | grep -a -o 'origin=0x[0-9A-Fa-f]*' | tail -1)
  [[ $st == FROZEN ]] || { tail -200 $L > $O/boot$i.tail.log; rm -f $L; }
  echo "boot$i fs=$fs t=$t $vo crash=$crash $st"
  # s7457 class DM: standard per-arm line for the loop verdict (soak_verdict_fields.sh); frozen=1 counts as a stall arm.
  al=1; [[ $st == EXITED* ]] && al=0; fz=0; [[ $st == FROZEN ]] && fz=1; echo "tag=boot$i alive_at_end=$al crashlines=$crash frozen=$fz fs=$fs"
  [[ $st == FROZEN ]] && { grep -aE "\[stall-(dump|wait)\]" $O/boot${i}_freeze.tail.log | head -20; grep -a "\[stall-cf0\]" $O/boot${i}_freeze.tail.log | tail -12; }
  print -l $O/rs64_stall_*.sample.txt(N) | sed 's/^/runtime self-sample: /'
  if [[ -n $HUNT_CONTROL && $i == 1 ]]; then
    d=FAIL; [[ -n $(print -l $O/rs64_stall_*.sample.txt(N)) ]] && d=PASS
    f=FAIL; [[ $st == FROZEN ]] && f=PASS
    echo "CONTROL dump=$d frozen=$f"
    [[ $d == PASS && $f == PASS ]] || ctlbad=1
    (( crash == 0 )) && bad=0
    mkdir -p $O/control; mv $O/rs64_stall_*.sample.txt(N) $O/boot1*(N) $O/ctl_boot1*(N) $O/control/ 2>/dev/null
  fi
done
(( ctlbad )) && exit 3
exit $bad
