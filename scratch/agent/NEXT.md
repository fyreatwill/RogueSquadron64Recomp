# NEXT work unit — compare port output relation with retail target swap

HYPOTHESIS-ID: m5-target-phase-edge

Session 3241 produced a valid, target-phase retail relation. The next unit is
the first like-for-like port comparison; do not apply M5 Step 3 until this
comparison identifies a missing legitimate edge.

## Competing hypotheses

- `H-PortOutputMismatch`: the port's target-phase VI/framebuffer publication
  differs from retail's caller `0x8001BE24`, physical framebuffer
  `0x00790000`, or target origins `0x00790400/0x00790800`.
- `H-PortTargetUnevaluable`: the port still cannot reach the corresponding
  target phase, so no output or audio change is authorized.
- `H-PortOutputMatches`: the port reaches the same relation; the current M5
  target-edge theory is not selected and must be parked.

## Discriminator

Build one same-build pair with `ROGUESQ_AUDIO_UCODE=0/1`, retaining all
existing passive M5/phase/dispatch controls. Capture the port's swap caller,
physical framebuffer, VI origin, image-task/output rows, and ordering in the
same phase-gated run. A like-for-like mismatch selects `H-PortOutputMismatch`;
absence of the target row selects `H-PortTargetUnevaluable`; matching caller,
destination, origins, and order selects `H-PortOutputMatches`.

## Exact commands

1. Build: `cmake --build build --config Debug --target
   RogueSquadron64Recomp`.
2. Run the existing bounded recipe, which includes the retail controls and
   both port arms in one invocation:
   `zsh scratch/agent/s3235_m5_port_retail_framebuffer_parity/run_pair.sh`.
3. Require whole-RDRAM positive control, title 1024, and hangar 512 before
   interpreting port zeros. Compare the resulting rows with
   `scratch/agent/soak_results/s3241_m5_vi_swap_target/oracle.log`.
