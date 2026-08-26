# NEXT work unit (s2445) — locate the port-side execution identity for the grounded second-range path

HYPOTHESIS-ID: m5-port-second-range-execution-identity

## Work unit

Add one regeneration-safe, observation-only port execution table for the
guest-call boundary corresponding to the retail-grounded
`0x8002BEEC` → `0x800078EC` relation, joined to the existing image task/DMA
identity and the exact `0x1798B0..0x179A48` range. Build one Debug binary and
run the same eleven-Start stub/image arms plus the retail oracle controls.
Do not change audio, output, dispatch, task data, or guards.

## Competing hypotheses and discriminator

These hypotheses are written before the next build:

- H-PortSemanticPathLive: the port executes the grounded caller/callee path
  after the image task, but the exact range is reached through a non-CPU or
  differently keyed event already missing from the current join.
- H-PortSemanticPathAbsent: neither the grounded caller boundary nor its
  callee executes in the target phase for the image identity.
- H-PortAlternatePath: a stable port execution path reaches the target phase
  and image identity, but it is not the grounded caller/callee pair.

The discriminator is one same-build, same-phase table containing both arms:
execution of the grounded pair joined after an image DMA selects
H-PortSemanticPathLive; no execution of either boundary with all controls
valid selects H-PortSemanticPathAbsent; execution of a stable alternate path
joined to the same image identity selects H-PortAlternatePath. A null is not
interpreted unless both port arms pass title/hangar controls, the image arm
shows DMEM work/generated DMA/SP completion, and the retail
whole-RDRAM/title/hangar/writer controls pass.

## Exact commands

`cmake --build build --config Debug --target RogueSquadron64Recomp`

`zsh scratch/agent/run_s2325_m5_task_output_join.sh s2445_m5_port_second_range_execution_identity`

Before building, add the bounded execution table to the existing
instrumentation and arm both stub and image with `ROGUESQ_AUDIO_UCODE=0/1`,
with `ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1
ROGUESQ_LLE_SOLO=1`, the eleven-Start schedule, and retail controls including
`--watch-write 0x0:0x800000`, title/hangar VI controls, exact ranges
`0x167650:0x167C50` and `0x1798B0:0x179A48`, plus the
`0x8002BEEC`/`0x800078EC` relation. Use shell-native watchdogs and SIGKILL.
