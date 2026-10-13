#!/bin/zsh
set -u

ROOT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
OUT="$ROOT/scratch/agent/s4796_hangar_gated_mission_2c"
rm -rf "$OUT"; mkdir -p "$OUT"
cd "$ROOT/build" || exit 2
pkill -KILL -x RogueSquadron64Recomp >/dev/null 2>&1 || true

env ROGUESQ_OVL2C_DROP=0 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_FORCE=1 \
  ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 \
  ROGUESQ_DLWALK=1 ROGUESQ_LOG_E9_PROVENANCE=1 ROGUESQ_LOG_TASKSUBMIT=1 \
  ROGUESQ_LOG_PHASE=1 PROBE_PHASE_WIDTH=512 PROBE_PHASE_TIMEOUT=240 \
  PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 ./RogueSquadron64Recomp >"$OUT/run.log" 2>&1 &
pid=$!
trap 'kill -KILL "$pid" 2>/dev/null || true; pkill -KILL -x RogueSquadron64Recomp >/dev/null 2>&1 || true' EXIT INT TERM

wid=""
for i in {1..120}; do
  kill -0 "$pid" 2>/dev/null || exit 3
  wid=$(./winctl find "$pid" 2>/dev/null | awk 'NR==1{print $1}')
  [[ -n "$wid" ]] && break
  sleep .25
done

press() {
  ./winctl activate "$pid" >/dev/null 2>&1 || true
  ./winctl key "$pid" "$1" 250 >/dev/null 2>&1 || true
}

for i in {1..240}; do
  kill -0 "$pid" 2>/dev/null || exit 4
  if grep -aq 'vi_width=512.*origin=0x006AB400' "$OUT/run.log"; then
    print "[driver] hangar phase at poll=$i" >>"$OUT/driver.log"
    break
  fi
  sleep 1
done
grep -aq 'vi_width=512.*origin=0x006AB400' "$OUT/run.log" || exit 5

for n in {1..6}; do
  press 36
  print "[driver] pair=$n key=start" >>"$OUT/driver.log"
  sleep 4
  press 6
  print "[driver] pair=$n key=a" >>"$OUT/driver.log"
  sleep 8
  if grep -aq 'vi_width=512.*origin=0x00690400' "$OUT/run.log"; then
    print "[driver] mission phase after pair=$n" >>"$OUT/driver.log"
    break
  fi
done

grep -aE '\[phase\].*(vi_width=512|origin=0x00690400)|\[dlwalk-2c\]|res=0x2C|\[CRASH\]|\[ABORT\]|unhandled|assert' \
  "$OUT/run.log" | tail -240 >"$OUT/discriminator.txt" || true
if grep -aq '\[CRASH\]\|\[ABORT\]' "$OUT/run.log"; then exit 3; fi
exit 0
