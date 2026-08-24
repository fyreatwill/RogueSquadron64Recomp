# NEXT work unit (s2307) — M5 cross-phase unconsumed-edge attribution

HYPOTHESIS-ID: m5-step3-unconsumed-edge-attribution

## Work unit

Run one same-run M5 Step 3 capture using the qualified default Factor 5 image
arm and the independent retail oracle. Retain the port for 45 seconds after
the first hangar origin, preserve the corrected `guest`→physical normalization,
and collect every nonzero image-stage row plus every PCM source/consumer row
from all width-512 `0x006AB400` phases in the retained run. Unlike s2306,
join the stage tuple across phase boundaries by normalized destination, length,
FNV, and nonzero count, and compare global event ordering rather than requiring
the same phase key. Do not change game behavior or add writeback, consumer,
slot, gate, guard, or address-remap machinery.

## Competing hypotheses and discriminating measurement

- H-CrossPhaseExact: the s2306 stage-only tuple gets an exact source and
  consumer tuple in a later `0x006AB400` phase, with both PCM events after the
  stage event. This means the current phase-scoped null is a cross-phase
  publication/consumption boundary.
- H-TrulyUnconsumed: the stage-only tuple has no exact source or consumer tuple
  across any retained width-512 target phase, even though the paired tuple
  still joins exactly.
- H-PayloadTupleMismatch: same-destination PCM calls recur across the retained
  phases, but no call has the stage tuple's length/FNV/nonzero payload; report
  the differing tuple fields and global event deltas.
- H-CoverageInvalid: the retail positive control, both retail VI origins, target
  writer-PC controls, or port title/hangar gates fail.

The discriminator is one complete cross-phase table with columns
`stage_phase,pcm_phase,width,origin,task_ordinal,stage_event,pcm_event,kind,
dest,len,stage_fnv,stage_nz,pcm_fnv,pcm_nz,event_delta,exact_tuple,
stage_before_pcm`. Include all nonzero stage rows, exact candidates, and
same-destination mismatches; include a per-destination summary with exact
source/consumer counts, mismatch counts, and stage-only counts. A positive
paired tuple and the independent retail controls are required before any null
is interpreted. The outcome selects one hypothesis at this capture scope.

## Exact commands

1. Ask ground truth before changing the driver or adding an instrument:

   `grep -a -E 'positive-control threshold|origin=0x00790400 width=1024|origin=0x006ab400 width=512|writer-pc-phase origin=0x006ab400 width=512 watch=2|writer-pc pc=0x8008eb8c|writer-pc pc=0x8008ebbc|writer-pc pc=0x80094648' scratch/agent/s2306_m5_temporal_recurrence/oracle.log | tail -80`

   Require the positive-control threshold, both VI origins, the target writer
   phase line, and all three writer-PC lines. If absent, repair the oracle
   recipe first; do not interpret a port cross-phase table against an
   unqualified retail run.

2. Create/update `scratch/agent/run_s2307_m5_cross_phase_join.sh` from the
   s2306 driver. Keep the oracle recipe, qualified image-arm environment,
   title/hangar gates, 45-second retention, and passive diagnostics unchanged.
   Change only the postprocessor so PCM records are indexed across all
   retained width-512/`0x006AB400` phases and the table records global event
   deltas, exact tuple matches, and same-destination payload mismatches. Run
   the retail oracle and one default image arm in this same iteration.

3. Syntax-check and run the driver:

   `zsh -n scratch/agent/run_s2307_m5_cross_phase_join.sh`

   `zsh scratch/agent/run_s2307_m5_cross_phase_join.sh`

Report the complete cross-phase table and destination summary before
interpreting the stage-only edge. No runtime behavior, writeback, consumer,
writer, slot, gate, guard, address-remap, or default change is authorized by
this work unit.
