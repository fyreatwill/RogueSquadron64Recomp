# M5 session 4164 — declared audio staging span

The rebuilt binary was run with two concurrent, phase-gated real-image arms:

- declared arm: `ROGUESQ_AUDIO_LEGACY_UCODE_DMA` unset
- rollback arm: `ROGUESQ_AUDIO_LEGACY_UCODE_DMA=1`

Both used the existing AUTOPILOT route, `PROBE_PHASE_WIDTH=1024`,
`PROBE_KEYS_FROM_PHASE=1`, `ROGUESQ_LOG_ALL=1`, and the task-contract probes.
The declared arm logged `dma_size=0x800` with `declared=0x800`, repeated image
exits at `break_pc=0x1328`, SP completion, and reached title VI 1024 and
hangar VI 512. Its final hangar join had `dmem_changed=1762`, `exit=1`, and
the expected zero payload signatures.

The first concurrent legacy arm crashed in `spTaskSchedulerThread` before its
first audio dispatch, so that result was route-invalid rather than a staging
comparison. A same-recipe legacy-only retry removed that confounder: it logged
`dma_size=0xF80` against `declared=0x800`, repeated image exits at
`break_pc=0x1328`, SP completion, and reached both title and hangar phases.
The retry's final hangar join had `dmem_changed=2467`, `exit=1`, and the same
zero payload signatures.

The discriminator selects H-step3-equivalent: the declared `0x800` staging
span preserves the complete measured task/route contract, while the legacy
`0xF80` span changes DMEM contents but has no measured downstream benefit.
This is two independent port arms in one rebuilt binary, not independent
retail ground truth; it does not explain the upstream zero source payload.

ORIGIN: `librecomp/src/rsp.cpp` owns the staging DMA size and
`factor5_ucode_b` owns the image DMEM/DMA writes. The declared arm preserves
the OSTask-declared contract; the legacy arm is retained only as rollback.
No mitigation or guest behavior changed.
