# NEXT work unit (s2586) — locate the missing M5 writer call path

HYPOTHESIS-ID: m5-audio-contract-gap

## Single work unit

Add regeneration-safe, phase-gated entry/branch/return diagnostics for every
function containing the seven direct `0x800A0F50` stores and the indexed
`0x80141AD8+index` store: `setDisplayMode`, `reapplyDisplayMode`,
`shutdownMusyXEngine`, `musyxNoopStub`, and the channel-array writer function
containing `0x80094648`. Preserve behavior. Build once and run one qualified
image arm with the existing writer, PCM, task, image, and VI controls.

## Competing hypotheses and discriminator

- `H-WriterNeverEntered`: a complete entry census has no row for the
  retail-attributed function/site in title or hangar.
- `H-StoreBranchSkipped`: the attributed function entry fires, but its
  branch/return census shows the store path is not taken.
- `H-DispatchAlias`: entry fires under an unexpected generated function or
  route, indicating a dispatch/overlay binding mismatch.

The discriminator is one phase-keyed table with an entry row, every branch
that can bypass each target store, each target store row, and the return row,
joined to route ordinal, task dispatch, image completion, PCM source/consumer,
and title/hangar controls. No entry selects `H-WriterNeverEntered`; an entry
without its store selects `H-StoreBranchSkipped`; an entry under the wrong
function/route selects `H-DispatchAlias`. Missing phase or control rows make
the capture unevaluable.

## Required implementation and command

Put the diagnostics in the companion `N64Recomp/fixup_game_funcs.py` (not
generated C), regenerate/fix up the affected output in the documented order,
then:

```sh
cmake --build build --config Debug --target RogueSquadron64Recomp
cd build
env ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1 \
  ROGUESQ_LLE_SOLO=1 ROGUESQ_AUTOPILOT='3:start,6:start,9:start,12:start,16:a,20:a,24:start,28:a' \
  ROGUESQ_AUTOPILOT_STOP_WIDTH=512 ROGUESQ_LOG_M5_PCM_WRITER=1 \
  ROGUESQ_LOG_M5_GATE_CONTRACT=1 ROGUESQ_LOG_PCM_BOUNDARY=1 \
  ROGUESQ_LOG_AUDTASK=1 ROGUESQ_LOG_M5_WRITER_ENTRY=1 \
  ./RogueSquadron64Recomp > ../scratch/agent/s2586_m5_writer_callpath.log 2>&1
```

Run from `build/`, verify exact title/hangar phase rows and all positive
controls, then SIGKILL the game PID at the bound. Do not promote a store,
task field, output pointer, or gate from the result.
