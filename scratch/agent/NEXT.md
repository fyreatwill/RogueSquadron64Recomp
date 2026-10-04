# Next work unit: qualify the audio-arm route before another writer census

HYPOTHESIS-ID: m5-route-qualification-4018

Competing hypotheses:

- H1: the declared/real pre-target stop is schedule-sensitive; adding a
  declared/silent control in the same run will reach both target VIs while
  declared/real remains the only real-audio failure.
- H2: the legacy `0xF80` staging path is causal; declared/real and
  declared/silent will reach both target VIs while legacy/real alone crashes
  at `0x8000834C`.
- H3: the arm failures are shared contention or nondeterministic scheduling;
  all three arms will fail or different arms will fail without a stable split.

Discriminator: one build/run with retail, declared/real, declared/silent, and
legacy/real concurrently. Preserve the whole-RDRAM oracle positive control,
title/hangar VI controls, and port RSP-source/audio-stage/phase controls. H1,
H2, and H3 are distinguished by which arm reaches both target VIs and whether
the crash remains uniquely tied to legacy staging. Do not use a retail-only
null or add a mitigation if no real-audio arm reaches both target phases.

Commands:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    env RS64_BOUNDARY_OUT=/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/s4019_m5_route_qualification zsh scratch/agent/run_s4019_m5_route_qualification.sh

The new recipe must launch the four arms concurrently, use a fresh output
directory, phase-gate every budget, and SIGKILL every arm after its watchdog.
Use the established autopilot and `ROGUESQ_SPIN_YIELD=1`; retain
`ROGUESQ_AUDIO_UCODE=1`, with `ROGUESQ_AUDIO_LEGACY_UCODE_DMA=1` only on the
legacy arm and the silent arm's explicit `ROGUESQ_AUDIO_UCODE=0`.
