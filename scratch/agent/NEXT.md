# NEXT work unit (s2020)

HYPOTHESIS-ID: m5-service-direct-entry-caller-witness

## Work unit

Witness the phase-valid direct entry and caller of serviceVoicePoolFrame.

Ask the retail oracle for the phase-valid `0x8009B5A8` execution watch and
whole-RDRAM write control again, then modify the existing
`serviceVoicePoolFrame` entry diagnostic through the fixup script (not the
generated C) to record a bounded pre-phase control and a phase-gated direct
entry/exit witness. Include the entry's `rs64_phase_ord`, guest thread,
status, `ctx->r31`/derived guest call site, and the existing `0x8009B7EC`
store edge. Keep the `get_function` witness, status writers, audio, spin, PI,
guard, and mitigation behavior unchanged. Run one build and one phase-valid
port recipe with the direct-entry witness and the existing audio controls.

The s2019 oracle already supplied a phase-valid retail control: whole-RDRAM
writes reached the 10,000 callback cap, `0x8009B5A8` executed 4,223 times,
and the oracle's aggregate predecessor was `0x80019B74`. The s2019 port run
reached VI 1024 and 512 but had zero `[svc-resolve]`, `[dma-ring-caller]`,
and `[tickfunc-caller]` rows. That was a positive-control failure for the
indirect-dispatch mechanism, not evidence about the worker boundary.

## Competing hypotheses and discriminator

- D1: The phase-valid port reaches the service function directly. The
  pre-phase control fires, phase-gated entry and exit fire, and the derived
  guest call site agrees with the retail predecessor (`ctx->r31 - 8` near
  `0x80019B74`). This selects a live direct service path and moves the open
  question to its status/worker stores.
- D2: The phase-valid port never enters the service function. The pre-phase
  control fires, phase-gated entry/exit and `0x8009B7EC` remain zero, while
  phase-valid audio-gate/task rows and the VI controls are live. This selects
  a gate or missing caller before the service function.
- D3: The phase-valid port enters, but the guest call site or host thread
  differs from retail. Entry/exit are live with a non-retail `ctx->r31 - 8`
  or thread, selecting a port call-path/scheduler mismatch rather than a
  missing registration.
- D4: Entry is live but the exit/store edge is absent or the status is not
  the expected phase-valid value. This selects a service-body or callback
  boundary; it must not be collapsed into D2.

The one discriminating table is: oracle control count, oracle target-PC hits,
port pre-phase entry control, port phase-valid entry count/call site/thread,
phase-valid exit count, status at entry, `0x8009B7EC` store count, and the
existing audio-gate/task rows. A phase-valid port row is only interpreted if
the pre-phase entry control is nonzero in the same run. Do not run another
`get_function` or status-writer join until this direct-entry table selects a
row.

## Exact commands

Ground truth first. Run the existing oracle command from s2019, changing only
the output path to `scratch/agent/soak_results/s2020-retail-service-entry.log`:

```sh
tools/oracle/build/rs64_oracle --core ../rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom ../rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 80 --hit-cap 10000 --watch-write 0x0:0x800000 --watch-pc 0x8009B5A8 --vi-trace --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start > scratch/agent/soak_results/s2020-retail-service-entry.log 2>&1
```

Update the existing `serviceVoicePoolFrame` diagnostic in
`../N64Recomp/fixup_game_funcs.py`, then regenerate in the required order:

```sh
cd ../N64Recomp && python tools/make_elf.py rogue_squadron.toml
build/Debug/N64Recomp.exe rogue_squadron.toml
python fixup_game_funcs.py
cd ../RogueSquadron64Recomp && cmake --build build --config Debug --target RogueSquadron64Recomp
```

Run the single phase-valid port capture without `ROGUESQ_LOG_ALL` (s2019's
ALL arm produced a pre-phase RT64 crash before the gate; the fixed specific
arm reached both 1024 and 512):

```sh
env ROGUESQ_LOG_AUDIO_DRAIN=1 ROGUESQ_LOG_AUDIOTICK_TRACE=1 ROGUESQ_LOG_DMA=1 ROGUESQ_LOG_DMA_CALLER=1 ROGUESQ_LOG_PCM_SANITY=1 ROGUESQ_LOG_VOICE_TRIGGER_CHAIN=1 ROGUESQ_LOG_WAITFORSLOT_GUARD=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh s2020-direct-entry 30 12
```

Extract only bounded discriminator rows:

```sh
RUN=scratch/s73_post_a_scene/s2020-direct-entry/run.log
rg -n -e '\\[s2020-svc\\]' -e '\\[s2006-svc\\]' -e '\\[service-voice-pool-frame\\]' -e '\\[pcm-sanity\\]' -e 'musyx-gate|audio-drain|\\[phase\\]' "$RUN" | tail -220
```
