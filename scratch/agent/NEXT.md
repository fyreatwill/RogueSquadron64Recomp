# NEXT work unit (s2061)

HYPOTHESIS-ID: m5-audio-task-completion-boundary

## Work unit

Run the retail oracle first, then run both audio-dispatch arms sequentially
in one iteration on the already-qualified no-focus route. Hold C88=1,
forced-LLE, `LLE_UNGATED=1`, `LLE_SOLO=1`, audio logging, spin yield, and the
phase-key schedule constant. The only treatment is whether
`ROGUESQ_AUDIO_UCODE=1` selects the current Factor 5 image; the control leaves
that variable unset and uses the existing `musyx_stub`.

Do not change the guest gate, C88 writer/value, audio task code, wait/slot
guards, PCM bridge, or scorer. Do not enable stock `aspMain`. Treat a missing
title/hangar anchor or missing direct-input control as UNEVALUABLE, not as
evidence about the audio image.

## Competing hypotheses and discriminator

- **H-StubBoundary** — the unset arm dispatches and returns through the stub
  but produces no audio DMEM activity/DMA/valid slot transition; the image arm
  shows DMEM activity and perhaps DMA, yet source and consumer PCM remain
  all-zero. This selects an unresolved Factor 5 task ABI or MORT boundary.
- **H-ImageValid** — the image arm has a clean audio task exit, valid slot
  status transitions, and nonzero PCM at the guest source and host consumer;
  the first de-stubbing step is structurally valid. The unset arm remains the
  silent negative control.
- **H-HostBridge** — the image arm produces nonzero guest PCM, but the queued
  host consumer differs in full-span bytes/count/FNV or is absent. This moves
  the boundary to the host AI/PCM bridge rather than the task image.
- **H-RouteUnevaluable** — either arm lacks the same-run graphics-task,
  direct-input, title-1024, or hangar-512 controls. No task/PCM null is
  admissible until the route recipe is repaired.

The selecting table is phase-keyed and must contain, for both arms: retail
whole-RDRAM and route positive controls; a non-audio `M_GFXTASK` dispatch and
completion control through the same RSP path; `[audtask-dispatch]` and audio
task exit reason; DMEM changed/canary rows; audio DMA and queue rows; slot
status writes/read transitions; PCM source/consumer full-span joins with FNV,
byte count, and nonzero-byte count; `[pad-host]`; title VI 1024; and hangar
VI 512. H-ImageValid requires clean task exit plus valid slot and nonzero PCM
rows. H-HostBridge requires nonzero source PCM with a consumer mismatch.
H-StubBoundary requires the positive controls plus image-side activity but no
valid slot/nonzero PCM result. Any missing positive control selects
H-RouteUnevaluable.

## Ground truth command (run before any port command)

```sh
tools/oracle/build/rs64_oracle \
  --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
  --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib \
  --secs 55 --hit-cap 1 \
  --watch-write 0x0:0x800000 \
  --watch-write 0x0CE730:0x0CE828 \
  --watch-pc 0x800B47C4,0x800B8014,0x800B8050 \
  --vi-trace --pif-trace \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start \
  > scratch/agent/s2061_oracle.log 2>&1
```

Require the whole-RDRAM threshold, title VI 1024, hangar VI 512, PIF rows,
and at least one relevant menu PC before treating either port arm as a valid
audio comparison.

## Port arms

```sh
route_keys='640@6:start 640@11:start 640@16:start 640@21:start 1024@2:a 1024@3:start 1024@4:a 1024@5:start 1024@7:a'

env REGRESS_NO_FOCUS=1 REGRESS_REQUIRE_VISUAL=1 REGRESS_SECS=180 REGRESS_INTERVAL=0.6 REGRESS_KEYS="$route_keys" REGRESS_LABEL=s2061_audio_stub \
  ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
  ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_SPIN_YIELD=1 \
  ROGUESQ_M5_C88_VALUE=1 ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_M5_POSTWAIT=1 \
  ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_PCM_SANITY=1 \
  zsh tools/regress.sh scratch/agent/s2061_audio_stub 180 \
  > scratch/agent/s2061_audio_stub_driver.log 2>&1

env REGRESS_NO_FOCUS=1 REGRESS_REQUIRE_VISUAL=1 REGRESS_SECS=180 REGRESS_INTERVAL=0.6 REGRESS_KEYS="$route_keys" REGRESS_LABEL=s2061_audio_image \
  ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
  ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_SPIN_YIELD=1 \
  ROGUESQ_M5_C88_VALUE=1 ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_M5_POSTWAIT=1 \
  ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_PCM_SANITY=1 \
  zsh tools/regress.sh scratch/agent/s2061_audio_image 180 \
  > scratch/agent/s2061_audio_image_driver.log 2>&1
```

ORIGIN: no guest writer, C88 value, wait, guard, skip, audio task, callback,
or default behavior change is authorized; this is a same-build treatment/
control comparison of the existing dispatch arms.
