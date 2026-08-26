#!/bin/zsh
set +e
repo_dir="$(cd "$(dirname "$0")/../.." && pwd)"
out_dir="$repo_dir/scratch/agent/s2401_identity_edges"
mkdir -p "$out_dir"
cd "$repo_dir/build"
stamp="$(date +%Y%m%d-%H%M%S)"
log_a="$out_dir/arm_a_$stamp.log"
log_b="$out_dir/arm_b_$stamp.log"
env ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_STUB_MISSING_FUNCS=1 PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 ROGUESQ_LOG_M5_ROUTE_ORDER=1 ROGUESQ_LOG_M5_STAGE_CALLS=1 ROGUESQ_LOG_M5_IDENTITY_EDGES=1 ./RogueSquadron64Recomp >"$log_a" 2>&1 &
p1=$!
env ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_STUB_MISSING_FUNCS=1 PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 ROGUESQ_LOG_M5_ROUTE_ORDER=1 ROGUESQ_LOG_M5_STAGE_CALLS=1 ROGUESQ_LOG_M5_IDENTITY_EDGES=1 ./RogueSquadron64Recomp >"$log_b" 2>&1 &
p2=$!
sleep 120
kill -KILL "$p1" "$p2" 2>/dev/null
wait "$p1"; a=$?
wait "$p2"; b=$?
printf 'arm_a=%s\narm_b=%s\nlog_a=%s\nlog_b=%s\n' "$a" "$b" "$log_a" "$log_b" >"$out_dir/status"
