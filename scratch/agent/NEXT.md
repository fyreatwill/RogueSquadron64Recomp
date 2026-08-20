# NEXT work unit (s2048)

HYPOTHESIS-ID: m5-route-qualification

## Work unit

Ask the retail oracle first with its whole-RDRAM positive control and the
existing watches at `runMenuModelViewerScreen` (`0x800C28F0`),
`menuControllerInput` (`0x800B47D0`), and `anyAudioSlotActive`
(`0x8008E57C`). Then run one audio-on route qualification from the existing
build. Use `tools/regress.sh`: keep the eleven width-640 Starts that reach
title, but use the established denser title schedule
`1024@2:a 1024@3:start 1024@4:a 1024@5:start 1024@7:a` after the first
VI-1024 phase. Keep C88=1, forced LLE, opt-in audio, spin yield, the existing
s2046 caller table, and all passive controls. Do not add instrumentation or
interpret bridge/PCM rows unless both VI 1024 and hangar VI 512 anchors appear.

## Competing hypotheses and discriminator

- **R1 — wrapper/input failure:** preflight is not `input=ok visual=ok`, or
  the schedule produces no `[pad-host]` rows. The recipe is invalid and must
  be repaired before route evidence is read.
- **R2 — title-side guest route:** title VI 1024 and host input are live, but
  `menuControllerInput` and the hangar transition remain absent. The guest
  title-to-hangar handoff remains the boundary.
- **R3 — presentation handoff:** `menuControllerInput` and a VI-producer
  request/transition toward 512 are live, but no 512 anchor appears. The
  boundary is between guest route and presentation.
- **R4 — route is phase-valid:** both VI 1024 and hangar VI 512 anchors appear,
  making the existing callback-side bridge/PCM table admissible next.

The single discriminator is one whole-pass table keyed by preflight status,
VI 640/1024/512 anchors, `[pad-host]` rows, existing caller edges,
`menuControllerInput`, VI-producer requested widths, and service controls.
R1 wins only on missing preflight/input control; otherwise R4 wins on both
target anchors, R3 on live menu/512 request without the anchor, and R2 on
live title input without the menu handoff. PCM remains inadmissible for R1–R3
or any run missing either target anchor.

## Commands

```sh
# Ground truth first: whole-RDRAM must reach its cap, retail must reach both
# target anchors, and all three execution watches must fire.
tools/oracle/build/rs64_oracle \
  --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
  --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib \
  --secs 55 --hit-cap 1 --watch-write 0x0:0x800000 \
  --watch-pc 0x800C28F0,0x800B47D0,0x8008E57C --vi-trace \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start \
  > scratch/agent/s2048_oracle.log 2>&1

# Existing build; no generated code or new diagnostic field is needed.
set +e
env REGRESS_SECS=130 REGRESS_INTERVAL=0.6 \
REGRESS_KEYS='640@6:start 640@11:start 640@16:start 640@21:start 640@26:start 640@31:start 640@36:start 640@41:start 640@46:start 640@51:start 640@56:start 1024@2:a 1024@3:start 1024@4:a 1024@5:start 1024@7:a' \
REGRESS_LABEL=s2048_m5_route \
ROGUESQ_M5_C88_VALUE=1 ROGUESQ_LLE_FORCE=1 ROGUESQ_AUDIO_UCODE=1 \
ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_M5_CALLER_EDGE=1 \
ROGUESQ_LOG_REAPPLYDISPLAYMODE_REACH=1 ROGUESQ_LOG_M5_GATE_CONTRACT=1 \
ROGUESQ_LOG_VI_TRANSITION=1 ROGUESQ_LOG_PCM_SANITY=1 \
zsh tools/regress.sh scratch/agent/s2048_route 130 \
  > scratch/agent/s2048_route_driver.log 2>&1
printf 'route_rc=%s\n' "$?"
```

Inspect `verdict.json`, `env.txt`, bounded tag counts, and tails only; do not
read the full run log or treat a final-key scorer failure as a route verdict
when the VI anchors and pad-host rows are present.
