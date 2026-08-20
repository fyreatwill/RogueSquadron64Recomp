# NEXT work unit (s2046)

HYPOTHESIS-ID: m5-postwait-caller-edge

## Work unit

Ask the retail oracle first with the whole-RDRAM positive control and the
existing watches at `runMenuModelViewerScreen` (`0x800C28F0`),
`menuControllerInput` (`0x800B47D0`), and `anyAudioSlotActive`
(`0x8008E57C`). Then add one regeneration-safe, phase-scoped caller-edge
table to the fixup script. It must record, per arm and VI-640 phase, the
post-wait branch's caller/return address, the next `menuOverlayInit` and
`runMenuModelViewerScreen` edge, the existing `pad-host` and service
controls, and the existing VI-transition-producer control. Do not add another
loop counter. Build once in the normal regeneration order and run the
same C88=1, forced-LLE, spin-yield, eleven-Start pair: arm A sets
`ROGUESQ_AUDIO_UCODE=1`; arm B leaves it unset. Keep all passive controls and
do not interpret bridge or PCM rows without both VI 1024 and hangar VI 512
anchors.

## Competing hypotheses and discriminator

- **Q1 — shared guest route:** both arms have the same post-wait caller/edge
  table and live input/service controls, but neither reaches a target VI. The
  shared menu/mission route remains the boundary.
- **Q2 — audio-specific continuation:** the caller/return or next-edge table
  diverges by arm, or only one arm reaches `menuControllerInput`. This selects
  an audio/task-dependent continuation.
- **Q3 — input/focus confound:** the caller edges match, but one arm lacks its
  scheduled `pad-host` depth or the 24/24 service control. No route conclusion
  is allowed; repair the wrapper/input control first.
- **Q4 — VI handoff boundary:** caller edges and controls match in both arms,
  and the VI-transition producer is live, but no target VI appears. This moves
  the boundary below the guest route and above presentation, without claiming
  an audio cause.

The single discriminating table is keyed by arm, phase, origin, site, caller
PC/RA, next edge, `pad-host`, service entry/exit, VI-transition-producer rows,
and target anchors. Q3 wins on a missing control; otherwise Q2 wins on an arm
edge split, Q4 on identical edges plus live VI producer and no target, and Q1
on identical edges with the route still stopping before the handoff.

## Commands

```sh
# Ground truth: the whole-RDRAM watch must hit its cap and retail must show
# both target anchors plus the three execution-watch controls.
tools/oracle/build/rs64_oracle \
  --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
  --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib \
  --secs 55 --hit-cap 1 --watch-write 0x0:0x800000 \
  --watch-pc 0x800C28F0,0x800B47D0,0x8008E57C --vi-trace \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start \
  > scratch/agent/s2046_oracle.log 2>&1

# Add the caller-edge table to fixup_game_funcs.py, then regenerate in order:
cd ../rogue_squadron64 && python3 tools/make_elf.py
cd ../N64Recomp && find RecompiledFuncs -mindepth 1 -maxdepth 1 -type f -delete && ./build/N64Recomp rogue_squadron.toml && python3 fixup_game_funcs.py
cd ../RogueSquadron64Recomp && python3 tools/apply_s652_ssnr_hdr_zero.py
cmake --build build --config Debug --target RogueSquadron64Recomp

# Run both arms from the one build; phase-relative gating is required.
set +e
env PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=120 PROBE_LEAVE_OK=1 PROBE_KEYS_FROM_PHASE=1 \
PROBE_KEYS='6:start 11:start 16:start 21:start 26:start 31:start 36:start 41:start 46:start 51:start 56:start' \
ROGUESQ_M5_C88_VALUE=1 ROGUESQ_LLE_FORCE=1 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_SPIN_YIELD=1 \
ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_M5_CALLER_EDGE=1 ROGUESQ_LOG_REAPPLYDISPLAYMODE_REACH=1 \
ROGUESQ_LOG_M5_GATE_CONTRACT=1 ROGUESQ_LOG_VI_TRANSITION=1 ROGUESQ_LOG_PCM_SANITY=1 \
zsh tools/probe.sh scratch/agent/s2046_audio_on 90 0.6 > scratch/agent/s2046_audio_on_driver.log 2>&1 &
p1=$!
env -u ROGUESQ_AUDIO_UCODE PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=120 PROBE_LEAVE_OK=1 PROBE_KEYS_FROM_PHASE=1 \
PROBE_KEYS='6:start 11:start 16:start 21:start 26:start 31:start 36:start 41:start 46:start 51:start 56:start' \
ROGUESQ_M5_C88_VALUE=1 ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_ALL=1 \
ROGUESQ_LOG_M5_CALLER_EDGE=1 ROGUESQ_LOG_REAPPLYDISPLAYMODE_REACH=1 \
ROGUESQ_LOG_M5_GATE_CONTRACT=1 ROGUESQ_LOG_VI_TRANSITION=1 ROGUESQ_LOG_PCM_SANITY=1 \
zsh tools/probe.sh scratch/agent/s2046_audio_stub 90 0.6 > scratch/agent/s2046_audio_stub_driver.log 2>&1 &
p2=$!
wait $p1; r1=$?
wait $p2; r2=$?
printf 'audio_on_rc=%s audio_stub_rc=%s\n' "$r1" "$r2"
```

Inspect bounded counts and tails only from the oracle and each `run.log`.
