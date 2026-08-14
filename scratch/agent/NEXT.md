# NEXT work unit (s1028)

HYPOTHESIS-ID: m3-slot-sp-corruption

Work unit: consume the queued `scratch/agent/soak_queue/s1028_slot_sp_guard.sh`
recipe and classify the first `ROGUESQ_LOG_SLOT_SP_GUARD=1` register dump at
`slotDispatcherIter` entry. This is the required pivot after three controlled
M4 nulls; do not run another M4 budget capture.

Competing hypotheses and discriminator:

- `H-slot-caller-corrupts-sp`: the first out-of-RDRAM `$sp` is inherited from a
  generated caller or indirect target with a bad frame/return path.
- `H-slot-entry-or-runtime-corrupts-sp`: `$sp` is valid at the caller boundary
  but becomes invalid in the dispatcher entry or runtime dispatch machinery.
- `H-no-sp-event`: the standard post-sec2 soak does not reach the guard before
  clean timeout or a disjoint crash.

The discriminator is the guard's first register dump plus its guest PC/caller
attribution. A dump with a valid caller boundary and invalid entry state selects
runtime/entry corruption; a dump whose caller/return path already carries the
wild `$sp` selects caller corruption; no dump with VI/input controls passing is
an unevaluable reachability result, not evidence for either corruption model.

Exact queued recipe:

    zsh scratch/agent/soak_queue/s1028_slot_sp_guard.sh

Required controls are VI-1024, input edges, and the positive
`ROGUESQ_LOG_SLOT_SP_GUARD` record. Analyze the resulting run log with bounded
grep/tail only. The loop owns the soak; do not babysit a repeat run here.
