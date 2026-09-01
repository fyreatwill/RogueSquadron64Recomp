# NEXT work unit — retail zero-fill entry qualification

HYPOTHESIS-ID: m5-image-task-zero-fill-contract

Session 3573 established the port entry tuple `0x801797B0/0/0x298`, but the
retail `0x800078EC` watch was inside the byte loop and cannot stand in for the
function-entry tuple. The port and retail source-span controls were live.

Competing hypotheses and discriminator:

- H-ZeroFillParity: retail and port enter `rs_memset` with the same
  destination, fill, length, and ordering; the zero is a legitimate shared
  contract and the remaining defect is downstream.
- H-ZeroFillPortInput: the port enters the shared writer with a divergent
  destination, fill, length, or source/task context, causing the wrong span to
  be cleared before the image task.
- H-ZeroFillPortOrdering: arguments match, but the port's zero-fill call is
  ordered before the producer/task handoff while retail orders it afterward.

The single discriminating table must join every phase-5 entry to
`0x800078E0` (entry arguments, return address, destination/fill/length,
source-span pre/post FNV/nonzero state) with the first target source-DMA
ordinal, and pair it with the retail `--watch-pc 0x800078E0` plus source-span
watch. Matching arguments and ordering select H-ZeroFillParity; a port-only
argument difference selects H-ZeroFillPortInput; matching arguments with a
cross-system ordering difference selects H-ZeroFillPortOrdering. A missing
positive control makes the result unevaluable.

Before building, verify the oracle core/ROM paths and run one oracle command
with whole-RDRAM control, source-span watch, and `--watch-pc 0x800078E0`.
Reuse the regeneration-safe port entry hook and run the port from `build/`
with:

    env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_AUTOPILOT='3:start,6:start,9:start,12:start,16:a,20:a,24:start,28:a' ROGUESQ_AUDIO_UCODE=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_M5_ZERO_FILL_CONTRACT=1 PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 ./RogueSquadron64Recomp

Require title `1024 @ 0x00790400`, hangar `512 @ 0x006AB400`, positive
writer/RSP controls, a live writer-entry control, and a non-empty joined
table. Stop with SIGKILL and retain logs under `scratch/agent/`.
