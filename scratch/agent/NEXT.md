# NEXT work unit (s2056)

HYPOTHESIS-ID: m5-guest-gate-c88-causality

## Work unit

Ask the retail oracle for ground truth first. Then, from one unchanged build,
run two sequential, focus-checked port arms with the qualified route held
fixed. Arm A sets `ROGUESQ_M5_C88_VALUE=1`; arm B leaves it unset. Require
windowed capture, use only the pre-hangar phase-relative key schedule below,
and reject any arm whose preflight, host Start control, title VI 1024, or
hangar VI 512 marker is absent. Do not change the guest writer, audio task
result, callback behavior, or any guard.

## Competing hypotheses and discriminator

- **H-C — guest-gate causal:** with input and route controls equal, only the
  C88=1 arm carries the retail value through the raw/gate consumer and reaches
  the title-to-hangar chain.
- **H-F — focus/route confound:** both arms have equal host-input and route
  controls once windowed capture/focus is valid; the earlier C88 split was not
  caused by the guest value.
- **H-W — writer/observation failure:** the two arms differ because the
  reapply writer or its phase/origin attribution is absent or inconsistent;
  neither arm is admissible until the writer and gate controls fire.
- **H-R — downstream route boundary:** both arms show the C88 writer and raw
  gate rows, but the later menu/hangar boundary differs while input remains
  live; C88 is upstream-correlated but not sufficient to explain the handoff.

The discriminator is one phase-keyed two-arm table joining `[pad-host]` and
`[host-start]`, the `reapplyDisplayMode` writer, raw/gate-1 consumer rows,
`menuControllerInput`/`menuInput`, and VI title/hangar anchors. Same-run
positive controls are windowed preflight, host Start rises, the retail
whole-RDRAM/PC watches, and live audio-task/gate rows. H-C requires a
C88-only difference that survives all controls; H-F requires equal route and
gate outcomes; H-W is selected by a missing writer/control; H-R by equal
writer/raw-gate results followed by a later route split.

## Commands

```sh
# Ground truth first.
tools/oracle/build/rs64_oracle \
  --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
  --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib \
  --secs 55 --hit-cap 1 --watch-write 0x0:0x800000 \
  --watch-pc 0x800C28F0,0x800B47D0,0x8008E57C --vi-trace \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start \
  > scratch/agent/s2056_oracle.log 2>&1

cmake --build build --config Debug --target RogueSquadron64Recomp

route_keys='640@6:start 640@11:start 640@16:start 640@21:start 1024@2:a 1024@3:start 1024@4:a 1024@5:start 1024@7:a'

env REGRESS_REQUIRE_VISUAL=1 REGRESS_SECS=75 REGRESS_INTERVAL=0.6 REGRESS_KEYS="$route_keys" REGRESS_LABEL=s2056_c88_on \
  ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
  ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_SPIN_YIELD=1 \
  ROGUESQ_M5_C88_VALUE=1 ROGUESQ_LOG_ALL=1 \
  ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_PCM_SANITY=1 \
  zsh tools/regress.sh scratch/agent/s2056_c88_on 75 \
  > scratch/agent/s2056_c88_on_driver.log 2>&1

env -u ROGUESQ_M5_C88_VALUE REGRESS_REQUIRE_VISUAL=1 REGRESS_SECS=75 REGRESS_INTERVAL=0.6 REGRESS_KEYS="$route_keys" REGRESS_LABEL=s2056_c88_unset \
  ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
  ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_SPIN_YIELD=1 \
  ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_PCM_SANITY=1 \
  zsh tools/regress.sh scratch/agent/s2056_c88_unset 75 \
  > scratch/agent/s2056_c88_unset_driver.log 2>&1
```

Inspect each `verdict.json`, preflight, `[pad-host]`/`[host-start]`, writer
and raw/gate rows, route markers, target VI transitions, and task controls.
