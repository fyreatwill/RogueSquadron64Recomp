# NEXT work unit (s2044)

HYPOTHESIS-ID: m5-audio-wait-boundary

## Work unit

Ask the retail oracle for its whole-RDRAM positive control and documented
eleven-Start route first. Then build once and run two concurrent port arms with
the same C88=1, forced-LLE, boot-relative eleven-Start recipe and all passive
M5 controls. Arm A sets `ROGUESQ_AUDIO_UCODE=1`; arm B leaves that variable
unset so the existing audio stub remains active. Gate both with
`PROBE_PHASE_WIDTH=1024`, keep `PROBE_LEAVE_OK=1`, and require a live
`pad-host` control before interpreting the route. Do not interpret bridge or
PCM rows unless an arm has both VI 1024 and hangar VI 512 anchors.

## Competing hypotheses and discriminator

- **W1 — opt-in audio task/slot ABI:** only arm A reaches
  `waitForAnyAudioSlot` at VI 640 while arm B reaches VI 1024 (and possibly
  VI 512), with `pad-host` and service controls live in both. The audio
  de-stubbing path is the pre-title boundary.
- **W2 — common C88/menu route:** both arms reach the same
  `waitForAnyAudioSlot` site at VI 640 with live `pad-host` and service
  controls, so the wait is upstream of the audio-image arm and the guest/menu
  route remains the boundary.
- **W3 — focus/event route:** either arm lacks its `pad-host` Start rows or
  its service positive control. A phase difference in that arm is not an
  audio result; the wrapper/input path must be repaired before more M5
  interpretation.
- **W4 — transient wait observation:** both arms have live `pad-host` and
  service controls, neither reaches VI 1024, and neither records the wait
  site. This refutes the claim that the single s2043 wait row is the durable
  blocker and parks it for a new route discriminator.

The one-build comparison selects W1 when the A-only wait/title split occurs,
W2 when both arms have the wait with live controls, W3 when the required input
or service control is missing, and W4 when both controlled arms avoid the wait
while remaining phase-invalid. A missing phase anchor never authorizes a PCM
conclusion.

## Commands

```sh
# Ground truth: whole-RDRAM watch must hit its cap and retail must show both anchors.
tools/oracle/build/rs64_oracle \
  --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
  --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib \
  --secs 55 --hit-cap 1 --watch-write 0x0:0x800000 --vi-trace \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start \
  > scratch/agent/s2044_oracle.log 2>&1

cmake --build build --config Debug --target RogueSquadron64Recomp

set +e
env PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=120 PROBE_LEAVE_OK=1 \
PROBE_KEYS='6:start 11:start 16:start 21:start 26:start 31:start 36:start 41:start 46:start 51:start 56:start' \
ROGUESQ_M5_C88_VALUE=1 ROGUESQ_LLE_FORCE=1 ROGUESQ_AUDIO_UCODE=1 \
ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_ALL=1 \
ROGUESQ_LOG_REAPPLYDISPLAYMODE_REACH=1 ROGUESQ_LOG_M5_GATE_CONTRACT=1 \
ROGUESQ_LOG_PCM_SANITY=1 \
  zsh tools/probe.sh scratch/agent/s2044_audio_on 90 0.6 > scratch/agent/s2044_audio_on_driver.log 2>&1 &
p1=$!
env -u ROGUESQ_AUDIO_UCODE PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=120 \
PROBE_LEAVE_OK=1 \
PROBE_KEYS='6:start 11:start 16:start 21:start 26:start 31:start 36:start 41:start 46:start 51:start 56:start' \
ROGUESQ_M5_C88_VALUE=1 ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1 \
ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_REAPPLYDISPLAYMODE_REACH=1 \
ROGUESQ_LOG_M5_GATE_CONTRACT=1 ROGUESQ_LOG_PCM_SANITY=1 \
  zsh tools/probe.sh scratch/agent/s2044_audio_stub 90 0.6 > scratch/agent/s2044_audio_stub_driver.log 2>&1 &
p2=$!
wait $p1; r1=$?
wait $p2; r2=$?
print "audio_on_rc=$r1 audio_stub_rc=$r2"
```

Inspect only bounded counts and phase/`pad-host`/wait-site tails from both
`run.log` files, plus the oracle's positive-control and VI-anchor lines.
