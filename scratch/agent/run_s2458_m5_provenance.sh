#!/bin/zsh
set -u
repo_dir="$(cd "$(dirname "$0")/../.." && pwd)"
stamp="$(date +%Y%m%d-%H%M%S)"
out_dir="$repo_dir/scratch/agent/s2458_m5_provenance_$stamp"
mkdir -p "$out_dir"
run_arm() {
    local arm="$1"
    local audio="$2"
    env ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_AUDIO_UCODE="$audio" PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 'PROBE_KEYS=3:start 7:start 11:start 15:a 100:start' ROGUESQ_LOG_M5_SECOND_EXEC=1 ROGUESQ_LOG_M5_STATIC_CALLS=1 ROGUESQ_LOG_M5_ROUTE_ORDER=1 ROGUESQ_LOG_M5_STAGE_CALLS=1 ROGUESQ_LOG_M5_IDENTITY_EDGES=1 ROGUESQ_LOG_AUDIO_RETURN=1 ROGUESQ_LOG_PCM_SANITY=1 zsh "$repo_dir/tools/probe.sh" "$out_dir/$arm" 60 0.5 >"$out_dir/$arm.driver" 2>&1
    print "$?" >"$out_dir/$arm.rc"
}
run_arm stub 0 & p_stub=$!
run_arm image 1 & p_image=$!
wait "$p_stub"; stub_rc=$?
wait "$p_image"; image_rc=$?
print "stub_rc=$stub_rc" >"$out_dir/status"
print "image_rc=$image_rc" >>"$out_dir/status"
print "$out_dir"
