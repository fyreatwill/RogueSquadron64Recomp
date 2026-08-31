# Session 3317 — M5 plan reconciliation

## Planned unit and substitution

The planned unit was the configured-host `PatchesLib` build from `NEXT.md`.
It could not run here: this iteration measured `Darwin 25.4.0 arm64`, the
workspace is `/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp`,
and `E:/mips-toolchain` is absent. The configured Windows/MIPS host is not
available in this environment. I did not repeat the local missing-target
build from Session 3316.

The substitute was a source reconciliation of the existing M5 design gate.
This is single-source evidence from the checked-out source and plan, not a
claim about retail behavior.

## Reconciled active boundaries

- `get_rsp_microcode` selects `factor5_ucode_b` for `M_AUDTASK` by default and
  `musyx_stub` when `ROGUESQ_AUDIO_UCODE=0`.
- `musyx_stub` returns `RspExitReason::Broke` without DMEM/DMA work; the
  Factor 5 image performs generated DMEM/DMA work and reaches its generated
  `break 0` completion edge.
- `librecomp/rsp.cpp:run_task` requires `Broke` and then the runtime's SP
  completion path carries the task onward. Unknown task types and
  `aspMain.cpp:aspMain` are not live RS64 de-stubbing targets.
- The remaining gate, wait, slot, voice, AI/SDL, DMEM serialization, and MORT
  surfaces are already inventoried in `docs/M5-AUDIO-PLAN.md`; they require a
  named writer/consumer and a target-phase positive control before change.

This reconciliation did not produce a legitimate writer/consumer edge for
M5 Step 3 and authorizes no code change. The single experiment that would
refute the host-unavailable explanation is to run the prescribed
`cmake --build build --config Debug --target PatchesLib` on the configured
Windows/MIPS host and observe whether the target and inputs exist.
