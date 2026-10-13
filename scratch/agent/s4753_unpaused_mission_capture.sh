#!/bin/zsh
set -u

ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
OUT="$ROOT/scratch/agent/s4753_unpaused_mission_capture"
mkdir -p "$OUT"
cd "$ROOT/build" || exit 2
pkill -KILL -x RogueSquadron64Recomp >/dev/null 2>&1 || true

env ROGUESQ_OVL2C_DROP=0 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_DLWALK=1 ROGUESQ_LOG_E9_PROVENANCE=1 ROGUESQ_LOG_TASKSUBMIT=1 ROGUESQ_LOG_PHASE=1 ./RogueSquadron64Recomp >"$OUT/run.log" 2>&1 &
pid=$!
trap 'kill -KILL "$pid" 2>/dev/null || true; pkill -KILL -x RogueSquadron64Recomp >/dev/null 2>&1 || true' EXIT INT TERM

wid=""
for i in {1..120}; do
  kill -0 "$pid" 2>/dev/null || exit 3
  wid=$(./winctl find "$pid" 2>/dev/null | awk 'NR==1{print $1}')
  [[ -n "$wid" ]] && break
  sleep .25
done

raise() {
  ./winctl activate "$pid" >/dev/null 2>&1 || true
  osascript -e "tell application \"System Events\" to set frontmost of first application process whose unix id is $pid to true" >/dev/null 2>&1 || true
}
press() {
  raise
  ./winctl key "$pid" "$1" 250 >/dev/null 2>&1 || true
}
snap() {
  [[ -n "$wid" ]] && screencapture -x -o -l"$wid" "$OUT/$1.png" 2>/dev/null || true
}

prev=0
for event in 6:s 9:a 12:s 15:a 18:s 21:a 24:s 27:a 30:s 33:a 36:s 39:a 42:s 45:a; do
  t=${event%%:*}
  key=${event#*:}
  sleep $((t-prev))
  if [[ "$key" == s ]]; then press 36; else press 6; fi
  print "[driver] $key=$t" >>"$OUT/driver.log"
  prev=$t
done

print "[driver] polling mission VI" >>"$OUT/driver.log"
for i in {1..120}; do
  kill -0 "$pid" 2>/dev/null || exit 4
  if grep -aq 'vi_width=512.*origin=0x00690400' "$OUT/run.log"; then
    print "[driver] mission phase at poll=$i" >>"$OUT/driver.log"
    for j in {1..8}; do
      snap "mission_${j}"
      sleep 1
    done
    break
  fi
  sleep 1
done
grep -aE '\[phase\].*(vi_width=512|origin=0x00690400)|\[CRASH\]|\[ABORT\]|unhandled|assert' "$OUT/run.log" | tail -80 >"$OUT/phase-summary.txt"
exit 0
