# M5 s3759 — Step 1 contract qualification retry

Date: 2026-10-02

The Debug target was rebuilt once with `cmake --build build --config Debug --target RogueSquadron64Recomp`. The existing concurrent Step 1 driver ran from `build/` with the real image arm (`ROGUESQ_AUDIO_UCODE=1`) and silent control (`ROGUESQ_AUDIO_UCODE=0`), LLE-solo, spin-yield, autopilot, and phase-keyed M5 joins.

The independent retail oracle passed its whole-RDRAM positive control at 10,000 callbacks and reached title (`1024 @ 0x00790400`) and hangar (`512 @ 0x006AB400`). The silent port arm reached title and produced 261 phase-qualified task-ABI/DMA rows, 257 audio-return rows, 771 route rows, and 257 PCM-consumer rows; its DMEM remained unchanged as expected for the stub control. The real/image arm crashed before any target phase with `SIGSEGV`, `si_addr=0x400128d47`, and no phase-qualified M5 rows. The pair driver was stopped with SIGKILL after the pair gate could not be satisfied.

This selects `H-M5-RouteInstability` for this capture. It is not evidence for a missing downstream contract edge and does not authorize a change to audio dispatch, task writeback, voice handling, or PCM code. The next probe must retain the oracle and silent controls while isolating the image arm's pre-target crash path; no additional native task-data value field should be added.

Evidence: `scratch/agent/s3759_m5_step1_contract_pair/`.
