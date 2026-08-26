# NEXT work unit (s2396) — distinguish image-stage call reach from route filtering

HYPOTHESIS-ID: m5-image-stage-capture-route

## State going in

s2395 is route-valid only with `ROGUESQ_STUB_MISSING_FUNCS=1`: the suppressed
arm reached title width 1024 and stayed alive, while the unsuppressed control
reproduced the `0x80001F88` null-function crash. The suppressed arm still had
zero `[audtask-image-stage-row]` and `[m5-stage-bytes]` rows. Existing dispatch
counts were positive (61 `[audtask-dispatch]` rows), so the next boundary is
the image-stage call itself, not title reachability.

## Work unit

Add one bounded, phase-scoped call-attempt counter at the entry of
`rs64_audio_image_stage`, before its route filter, logging stage number and
route identity for at most 8 calls per stage. Keep the existing row/byte
captures unchanged. Build once, then run one suppressed image-arm instance
from `build/` for 60 seconds with `PROBE_PHASE_WIDTH=1024` and the required
route controls. Use the existing s2392 retail exact-window witness as the
ground-truth prerequisite; do not change task data, audio, gate, fallback,
dispatch, VI, output behavior, or any mitigation.

## Competing hypotheses and discriminator

- H-ImageStageCallsiteNotReached: dispatch is live but no stage-call attempt
  occurs in the title phase; call-attempt count is zero.
- H-StageCallRouteFiltered: stage-call attempts occur with title identity, but
  the existing route predicate suppresses every row; call attempts are
  positive and image-stage rows remain zero.
- H-StageCaptureBudgetOrLabel: stage-call attempts and rows are positive but
  the current grep label/capture budget is hiding them; both counts are
  positive and the call-attempt stage/route table exposes the mismatch.

The discriminating table is one row for each stage 0–3: call-attempt count,
first/last phase, width, origin, `[audtask-image-stage]` row count, and
`[m5-stage-bytes]` row count. A zero-call title row selects the missing
callsite hypothesis; positive title calls with zero rows select route
filtering; positive rows select a capture-label/budget issue.

## Controls and commands

The run must show `[audtask-dispatch]` activity and title origin
`0x00790400` at width 1024. Use the built macOS executable, not the stale
Windows name:

```zsh
cmake --build build --config Debug --target RogueSquadron64Recomp
mkdir -p scratch/agent/s2396_stage_call_boundary
cd build
env ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1 \
    ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 \
    PROBE_PHASE_WIDTH=1024 ROGUESQ_LOG_M5_STAGE_CALLS=1 \
    ./RogueSquadron64Recomp > ../scratch/agent/s2396_stage_call_boundary/run.log 2>&1 &
PID=$!
sleep 60
kill -9 "$PID" 2>/dev/null
wait "$PID" 2>/dev/null || true
grep -E 'm5-stage-call|audtask-image-stage|m5-stage-bytes|audtask-dispatch|origin=0x00790400' \
    ../scratch/agent/s2396_stage_call_boundary/run.log | tail -80
```

If title is not reached, the run is route-invalid and the call table cannot
select among the stage hypotheses.
