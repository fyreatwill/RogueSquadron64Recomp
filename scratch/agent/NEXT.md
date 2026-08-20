# NEXT work unit (s2045)

HYPOTHESIS-ID: m5-audio-wait-boundary

## Work unit

Ask the retail oracle for its whole-RDRAM positive control and the documented
eleven-Start route first, adding execution watches for
`runMenuModelViewerScreen` (`0x800C28F0`), `menuControllerInput`
(`0x800B47D0`), and `anyAudioSlotActive` (`0x8008E57C`). Then add one bounded,
diagnostic-only `ROGUESQ_LOG_M5_POSTWAIT` census in the fixup script, covering
entry/return and branch/loop rows for the post-`waitForAnyAudioSlot`
menu/mission path. Build once and run the same C88=1, forced-LLE,
spin-yield, eleven-Start pair: arm A sets `ROGUESQ_AUDIO_UCODE=1`; arm B
leaves it unset. Keep all passive controls. Require service and per-arm
`pad-host` controls; do not interpret bridge or PCM rows without both VI 1024
and hangar VI 512 anchors.

## Competing hypotheses and discriminator

- **P1 — common post-wait mission loop:** both arms pass the controls, return
  from the model-viewer path, and show the same post-wait branch/loop rows
  without a target phase. This selects the shared guest menu/mission route.
- **P2 — audio-specific continuation:** both controls are live, but the arms
  differ in post-wait entry/return/branch rows or target-phase reachability.
  This selects an audio/task-dependent continuation.
- **P3 — input/focus confound:** either arm lacks the scheduled `pad-host`
  control or its 24/24 service control. No route conclusion is allowed; the
  wrapper/input control must be repaired.
- **P4 — actual wait/consumer boundary:** both arms have live controls, but
  neither produces a post-wait return row while the slot-predicate rows show
  the same state. This selects the wait consumer itself rather than the
  later menu/mission branch.

The single discriminating table is keyed by arm and phase and contains
`pad-host`, service entry/exit, `waitForAnyAudioSlot` entry/return,
`runMenuModelViewerScreen` entry/return, post-wait branch/loop ordinal, and
VI anchors. P3 wins on a missing control; otherwise P2 wins on an arm split,
P4 on a shared missing return, and P1 on a shared returned loop.

## Commands

```sh
# Ground truth: whole-RDRAM watch must hit its cap; retail must show both anchors
# and the execution order of the three named PCs.
tools/oracle/build/rs64_oracle \
  --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
  --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib \
  --secs 55 --hit-cap 1 --watch-write 0x0:0x800000 \
  --watch-pc 0x800C28F0,0x800B47D0,0x8008E57C --vi-trace \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start \
  > scratch/agent/s2045_oracle.log 2>&1

# Add the M5 post-wait diagnostic to the fixup script, then build once.
cmake --build build --config Debug --target RogueSquadron64Recomp

set +e
env PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=120 PROBE_LEAVE_OK=1 \
PROBE_KEYS='6:start 11:start 16:start 21:start 26:start 31:start 36:start 41:start 46:start 51:start 56:start' \
ROGUESQ_M5_C88_VALUE=1 ROGUESQ_LLE_FORCE=1 ROGUESQ_AUDIO_UCODE=1 \
ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_M5_POSTWAIT=1 \
ROGUESQ_LOG_REAPPLYDISPLAYMODE_REACH=1 ROGUESQ_LOG_M5_GATE_CONTRACT=1 \
ROGUESQ_LOG_PCM_SANITY=1 \
  zsh tools/probe.sh scratch/agent/s2045_audio_on 90 0.6 > scratch/agent/s2045_audio_on_driver.log 2>&1 &
p1=$!
env -u ROGUESQ_AUDIO_UCODE PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=120 \
PROBE_LEAVE_OK=1 \
PROBE_KEYS='6:start 11:start 16:start 21:start 26:start 31:start 36:start 41:start 46:start 51:start 56:start' \
ROGUESQ_M5_C88_VALUE=1 ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1 \
ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_M5_POSTWAIT=1 \
ROGUESQ_LOG_REAPPLYDISPLAYMODE_REACH=1 ROGUESQ_LOG_M5_GATE_CONTRACT=1 \
ROGUESQ_LOG_PCM_SANITY=1 \
  zsh tools/probe.sh scratch/agent/s2045_audio_stub 90 0.6 > scratch/agent/s2045_audio_stub_driver.log 2>&1 &
p2=$!
wait $p1; r1=$?
wait $p2; r2=$?
print "audio_on_rc=$r1 audio_stub_rc=$r2"
```

Inspect bounded counts and tails only from the oracle plus each `run.log`.
