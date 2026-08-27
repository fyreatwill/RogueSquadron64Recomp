# s2516 M5 Step 3 contract-edge audit

Date: 2026-08-26

## Ground-truth control

The retail oracle whole-RDRAM positive control reached its 10,000-hit
threshold, returned `oracle_rc=0`, and ran 479 VI in 8 emulated seconds.

## Port A/B capture

Both arms used one existing binary, the qualified LLE route, `ROGUESQ_LOG_ALL`,
the phase gate, and the established input schedule. The stub arm used
`ROGUESQ_AUDIO_UCODE=0`; the image arm used `=1`; both reached title phase
`width=1024 origin=0x790400`.

| Field | Stub | Factor 5 image |
|---|---:|---:|
| `audtask-dispatch` rows | 1,423+ | 919+ |
| task handoff rows | 1,423+ | 919+ |
| DMEM change | 0 | 1,597 bytes, `break_pc=0x1328` |
| DMA count | 0 | 2–3 |
| image/stage payload | none | observed spans all `nz=0` |
| PCM source/consumer | zero/zero | matching zero/zero rows |
| output/task field writer | none | none; `output_buff=0` in task rows |
| crash marker | none in phase capture | none in phase capture |

The image arm demonstrated real task execution and generated DMA, but this
run did not select a legitimate nonzero writer or a missing output consumer
relation. The retail control proves the oracle instrument was live; it does
not prove a retail image contract edge. The prior s2513 nonzero image row
remains route/ordinal-scoped evidence and is not enough to authorize a
writeback or remap here.

## Decision

`H-proven-edge` was not selected. `H-no-edge` is selected for this title-phase
capture; `H-route-only` remains possible across the differing route/ordinal
scopes. No code, default, guard, writeback, or output mapping changed. The
image arm remains opt-in.
