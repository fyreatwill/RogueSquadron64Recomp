#!/bin/zsh
set -u

repo="/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp"
stamp="$(date +%Y%m%d-%H%M%S)"
out="$repo/scratch/agent/soak_results/s4168_m5_step4_clean_pair_$stamp"
mkdir -p "$out"
cd "$repo/build" || exit 3

common=(ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LLE_FORCE=1
  ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_SPIN_YIELD=1
  ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_PHASE=1
  ROGUESQ_AUTOPILOT='3:start,6:start,9:start,12:start,16:a,20:a,24:start,28:a'
  ROGUESQ_AUTOPILOT_STOP_WIDTH=512 PROBE_PHASE_WIDTH=1024
  PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1)

env "${common[@]}" ROGUESQ_AUDIO_UCODE=1 ./RogueSquadron64Recomp > "$out/real.log" 2>&1 &
real_pid=$!
env "${common[@]}" ROGUESQ_AUDIO_UCODE=0 ./RogueSquadron64Recomp > "$out/silent.log" 2>&1 &
silent_pid=$!

trap 'kill -KILL "$real_pid" "$silent_pid" 2>/dev/null || true' EXIT INT TERM
sleep 75
kill -KILL "$real_pid" "$silent_pid" 2>/dev/null || true
wait "$real_pid" 2>/dev/null || true
wait "$silent_pid" 2>/dev/null || true

summary="$out/summary.txt"
for arm in real silent; do
  log="$out/$arm.log"
  {
    print -r -- "arm=$arm"
    for marker in '[phase] vi_width=1024' '[phase] vi_width=512' \
      '[m5-frame-sync-positive]' '[audio]' '[m5-gate]' '[m5-PCM]' \
      '[m5-pcm]' '[m5-source]' '[m5-service]' '[m5-slot]' '[m5-status]' \
      '[m5-rsp]' '[m5-task]' '[CRASH]' '[ABORT]'; do
      print -r -- "$marker=$(grep -a -F -c "$marker" "$log" 2>/dev/null || true)"
    done
    print -r -- "phase_tail:"
    grep -a -E '\[phase\]|\[audio|\[m5-|\[CRASH\]|\[ABORT\]' "$log" | tail -80 || true
  } >> "$summary"
done
print -r -- "output=$out"
print -r -- "summary=$summary"
