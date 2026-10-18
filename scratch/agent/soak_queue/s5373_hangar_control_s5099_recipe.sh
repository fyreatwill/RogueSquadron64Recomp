#!/bin/zsh
[ -n "${ZSH_VERSION:-}" ] || exec /bin/zsh "$0" "$@"
# s5099: confirms s5098 shape-3 fixes (scene-node-cache zero_hi guard, heap-dequeue diag) under the hangar route.
# PASS = >=2 hangar arrivals, 0 CRASH.
set -u
NAME=s5373_hangar_control_s5099_recipe
ROOT=$(git -C "${0:A:h}" rev-parse --show-toplevel); OUT="$ROOT/scratch/agent/soak_results/$NAME"; BUILD="$ROOT/build"
rm -rf "$OUT"; mkdir -p "$OUT"
COMMON=(ROGUESQ_LOG_SCENE_NODE_CACHE_GUARD=1 ROGUESQ_OVL2C_DROP=0 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1
  ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_DLWALK=1 ROGUESQ_LOG_PHASE=1
  ROGUESQ_LOG_M5_ROUTE_TRANSITION=1 ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_AUDIO_UCODE=1
  PROBE_PHASE_WIDTH=512 PROBE_PHASE_TIMEOUT=240 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1)
K=$OUT/keys.log; : > $K
hang=0; crash=0; t00=$SECONDS
for try in 1 2 3; do
  [ $((SECONDS-t00)) -lt 380 ] || break
  pkill -KILL -x RogueSquadron64Recomp >/dev/null 2>&1 || true
  L=$OUT/run$try.log
  ( cd "$BUILD" && exec env "${COMMON[@]}" ./RogueSquadron64Recomp ) > $L 2>&1 &
  p=$!
  has() { grep -aq "$1" $L; }
  key() { "$BUILD/winctl" activate $p >/dev/null 2>&1; "$BUILD/winctl" key $p $1 250 >/dev/null 2>&1; }
  for i in $(seq 1 120); do has 'origin=0x00790400' && break; sleep 1; done
  if has 'origin=0x00790400'; then
    for n in $(seq 1 10); do
      has 'origin=0x006AB400' && break
      key 36; sleep 4; key 6; sleep 7
    done
    if has 'origin=0x006AB400'; then hang=$((hang+1)); sleep 30; fi
  fi
  c=$(grep -ac CRASH $L); crash=$((crash+c))
  print "try=$try hangar=$(has 'origin=0x006AB400' && echo 1 || echo 0) crash=$c guard_log=$(grep -ac 'scene-node-cache' $L) t=$((SECONDS-t00))" >> $K
  kill -9 $p 2>/dev/null; wait $p 2>/dev/null
done
print "result hangar_arrivals=$hang crash=$crash" >> $K
[ $crash -eq 0 ] || exit 1
[ $hang -ge 2 ] || exit 1
