# NEXT work unit (s2047)

HYPOTHESIS-ID: m5-route-qualification

## Work unit

Ask the retail oracle first with its whole-RDRAM positive control and the
existing watches at `runMenuModelViewerScreen` (`0x800C28F0`),
`menuControllerInput` (`0x800B47D0`), and `anyAudioSlotActive`
(`0x8008E57C`). Then run one audio-on route qualification from the existing
s2046 build. Use `tools/regress.sh` so the key schedule is grouped by VI
width: eleven Starts after the first VI-640 phase, followed by the known
title-to-hangar A/Start sequence after VI 1024. Keep C88=1, forced LLE, opt-in
audio, spin yield, the existing s2046 caller table, and all passive controls.
Do not add instrumentation or interpret bridge/PCM rows unless both VI 1024
and hangar VI 512 anchors appear.

## Competing hypotheses and discriminator

- **R1 — wrapper/input failure:** regress preflight is not `input=ok visual=ok`,
  or the phase-relative schedule has no `[pad-host]` rows. The recipe is
  invalid and must be repaired before route evidence is read.
- **R2 — shared route remains:** input is live, but the existing caller table
  still ends at the common `menuOverlayInit` return with no
  `menuControllerInput`/VI-1024 handoff. The shared route boundary remains.
- **R3 — route is phase-valid:** the schedule reaches VI 1024 and hangar VI
  512, making the existing callback-side bridge/PCM table admissible next.
- **R4 — presentation handoff:** `menuControllerInput` and a VI producer
  request for 1024 are live, but no 1024 anchor appears. This keeps the
  boundary between guest route and presentation without assigning an audio
  cause.

The single discriminator is the whole-pass table keyed by preflight status,
VI 640/1024/512 anchors, `[pad-host]` rows, existing s2046 caller edges,
`menuControllerInput`, VI-producer requested widths, and service controls.
R1 wins on a missing preflight/input control; otherwise R3 wins on both target
anchors, R4 on live menu/1024 request without the anchor, and R2 on live input
with the common pre-1024 edge and no handoff. PCM remains inadmissible for R2,
R4, or any run missing either target anchor.

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
  > scratch/agent/s2047_oracle.log 2>&1

# Use the existing s2046 build; no generated code or new diagnostic field is
# needed for this route-qualification unit.
set +e
env REGRESS_SECS=105 REGRESS_INTERVAL=0.6 \
REGRESS_KEYS='640@6:start 640@11:start 640@16:start 640@21:start 640@26:start 640@31:start 640@36:start 640@41:start 640@46:start 640@51:start 640@56:start 1024@2:a 1024@3:start 1024@4:a 1024@6:start' \
REGRESS_LABEL=s2047_m5_route \
ROGUESQ_M5_C88_VALUE=1 ROGUESQ_LLE_FORCE=1 ROGUESQ_AUDIO_UCODE=1 \
ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_M5_CALLER_EDGE=1 \
ROGUESQ_LOG_REAPPLYDISPLAYMODE_REACH=1 ROGUESQ_LOG_M5_GATE_CONTRACT=1 \
ROGUESQ_LOG_VI_TRANSITION=1 ROGUESQ_LOG_PCM_SANITY=1 \
zsh tools/regress.sh scratch/agent/s2047_route 105 \
  > scratch/agent/s2047_route_driver.log 2>&1
printf 'route_rc=%s\n' "$?"
```

Inspect `verdict.json`, `env.txt`, bounded tag counts, and tails only; do not
read the full run log or treat a final-key scorer failure as a route verdict
when the VI anchors and pad-host rows are present.
