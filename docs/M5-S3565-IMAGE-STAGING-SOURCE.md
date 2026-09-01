# M5 session 3565 — image-task staging DMA source and ordering

## Work unit

The existing phase-keyed source-window, DMEM-writer, image-stage, and route
controls were run on a standalone image arm. The retail oracle was unavailable
because this checkout has neither its ROM nor debugger core. The first port
capture used a route that crashed at guest PC `0x80001B08` before hangar and was
discarded. Its failure exposed a measurement defect: the shared source-window
budget was process-lifetime scoped and exhausted during title. The budget was
reset when the source-DMA phase key changed, then the same route was rebuilt and
rerun.

## Result

The corrected arm reached title (`0x00790400`, VI width 1024) and hangar
(`0x006AB400`, VI width 512), with 3,244 image-stage rows, 8,316 source-window
rows, 2,048 DMEM-writer rows, 505 audio returns, and no crash or abort before
the deliberate SIGKILL. The positive controls were live in both target phases.

Stage 2 and stage 3 remained zero-valued in both phases: title had 566/560
rows and hangar 247/245 rows respectively, all with `nz_a=0`. Hangar source
DMA rows included stage 3 `DMEM 0xCB0, len 0x198` from RDRAM `0x1798B0` and
stage 2 `DMEM 0x6F0, len 0x100` from RDRAM `0x1797B0`; both had zero payload
hash/nonzero counts. For the same hangar task ordinal, nonzero DMEM staging
was observed earlier (source-window events 4101–4104), followed by stores that
cleared the target span (events 4484–4485), and then the zero stage DMAs
(events 4488–4489). This is a phase/task-keyed ordering observation, not a
cross-run timing inference.

## Discrimination

The result selects `H-ZeroDmaOrdering` at the immediate boundary: the zero
stage DMAs occur after earlier nonzero staging and a subsequent clear in the
same task sequence. It refutes `H-DmaContractMismatch` for the observed stage
edges because the stage DMEM addresses and lengths match the image-stage
contract. `H-ZeroDmaSource` remains open at the deeper boundary: the source
range is demonstrably zero when read, but this run does not identify the
legitimate RDRAM writer or prove whether that zero is intended.

This remains single-source port evidence; the independent retail arm was not
available. No game state, task field, output, gate, slot, PCM, or writeback
behavior changed. The only code change was resetting the diagnostic source-
window print budget per target phase so a title budget cannot hide hangar rows.

Run log: `scratch/agent/s3565_image_staging_source_final/run.log`.
