# NEXT work unit (s2446) — explain the port zero-return-address boundary

HYPOTHESIS-ID: m5-port-second-range-execution-identity

## Work unit

Add one regeneration-safe, observation-only table at the port dispatch/call
boundary that invokes `0x800078EC`, capturing the dispatcher's current guest
PC, target guest PC, and the callee context. Join it to the existing image
stage/DMA identity and exact `0x1798B0..0x179A48` rows. Do not change audio,
output, task data, dispatch, or guards.

## Competing hypotheses and discriminator

- H-PortCallABI: the port invokes the callee through a host/runtime wrapper
  that does not populate `ctx->r31`; the dispatch-boundary table will show a
  stable target `0x800078EC` and caller/target pair while callee `ra` remains
  zero.
- H-PortDirectJump: the port reaches the callee through a direct/tail path;
  the boundary table will show no caller return edge and a stable direct-jump
  or tail-dispatch signature.
- H-PortWrongIdentity: the existing `0x800078EC` rows are an unrelated
  resident-overlay execution; the boundary table will not join them to the
  image task/DMA identity in the hangar phase.

The discriminator is one same-build table covering the dispatch boundary and
callee rows in both stub/image arms. A stable caller/target pair joined to the
image rows selects H-PortCallABI; no caller edge with a direct/tail signature
selects H-PortDirectJump; no joined target execution with all route controls
valid selects H-PortWrongIdentity. The probe must first emit a positive
control in each arm, and a null is valid only if both arms pass title/hangar,
the image arm shows DMEM/generated DMA/SP completion, and the retail
whole-RDRAM/title/hangar/exact-range/writer controls pass.

## Exact commands

`cmake --build build --config Debug --target RogueSquadron64Recomp`

`env ROGUESQ_LOG_M5_SECOND_EXEC=1 zsh scratch/agent/run_s2325_m5_task_output_join.sh s2446_m5_port_dispatch_boundary`

Use the established eleven-Start schedule and the existing retail controls:
`--watch-write 0x0:0x800000`, title/hangar VI origins, exact ranges
`0x167650:0x167C50` and `0x1798B0:0x179A48`, and the retail
`0x8002BEEC`/`0x800078EC` relation. Use phase-gated budgets and SIGKILL
cleanup. Keep `ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1
ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1` on both port arms.
