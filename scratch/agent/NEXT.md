# NEXT work unit (s2049)

HYPOTHESIS-ID: m5-route-qualification

## Work unit

Ask the retail oracle first with its whole-RDRAM positive control and the
existing watches at `runMenuModelViewerScreen` (`0x800C28F0`),
`menuControllerInput` (`0x800B47D0`), and `anyAudioSlotActive`
(`0x8008E57C`). Then run one C88=1 route qualification from the existing
build. Keep forced LLE, opt-in audio, spin yield, the eleven boot-relative
width-640 Starts, the existing s2046 caller table, and all passive controls.
After the first VI-1024 phase, use the denser title schedule
`1024@2:a 1024@3:start 1024@4:a 1024@5:start 1024@7:a`. Do not add wait
counters or interpret bridge/PCM rows unless both VI 1024 and hangar VI 512
anchors appear.

## Competing hypotheses and discriminator

- **R1 — wrapper/input failure:** preflight is not `input=ok visual=ok`, or
  the schedule produces no `[pad-host]` rows. Repair the recipe; no route
  evidence is admissible.
- **R2 — title-side guest route:** title VI 1024 and host input are live, but
  `menuControllerInput` and hangar VI 512 remain absent. The guest handoff is
  still the boundary.
- **R3 — presentation handoff:** `menuControllerInput` and a VI-producer
  request toward 512 are live, but no 512 anchor appears. The boundary is
  between guest route and presentation.
- **R4 — route is phase-valid:** both target anchors appear, making the
  callback-side bridge/PCM table admissible next.

The single discriminator is one whole-pass table keyed by preflight, VI
640/1024/512 anchors, `[pad-host]` rows, caller edges, `menuControllerInput`,
VI-producer requested widths, and service controls. R1 wins only on missing
preflight/input control; otherwise R4 wins on both anchors, R3 on a live menu
and 512 request without the anchor, and R2 on live title input without the
menu handoff. PCM is inadmissible for R1–R3 or any run missing either anchor.

## Commands

```sh
# Ground truth first: cap, title, hangar, and all three execution watches.
tools/oracle/build/rs64_oracle \
  --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
  --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib \
  --secs 55 --hit-cap 1 --watch-write 0x0:0x800000 \
  --watch-pc 0x800C28F0,0x800B47D0,0x8008E57C --vi-trace \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start \
  > scratch/agent/s2049_oracle.log 2>&1

set +e
env REGRESS_SECS=130 REGRESS_INTERVAL=0.6 \
REGRESS_KEYS='640@6:start 640@11:start 640@16:start 640@21:start 640@26:start 640@31:start 640@36:start 640@41:start 640@46:start 640@51:start 640@56:start 1024@2:a 1024@3:start 1024@4:a 1024@5:start 1024@7:a' \
REGRESS_LABEL=s2049_m5_route \
ROGUESQ_M5_C88_VALUE=1 ROGUESQ_LLE_FORCE=1 ROGUESQ_AUDIO_UCODE=1 \
ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_M5_CALLER_EDGE=1 \
ROGUESQ_LOG_REAPPLYDISPLAYMODE_REACH=1 ROGUESQ_LOG_M5_GATE_CONTRACT=1 \
ROGUESQ_LOG_VI_TRANSITION=1 ROGUESQ_LOG_PCM_SANITY=1 \
zsh tools/regress.sh scratch/agent/s2049_route 130 \
  > scratch/agent/s2049_route_driver.log 2>&1
printf 'route_rc=%s\n' "$?"
```

Inspect only `verdict.json`, `env.txt`, bounded tag counts, and log tails; do
not read the full run log or treat a final-key scorer failure as a route
verdict when the VI anchors and `[pad-host]` rows are present.
