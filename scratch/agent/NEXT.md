# NEXT work unit (s1030)

HYPOTHESIS-ID: m3-slot-sp-corruption

Run/consume exactly one queued recipe: `s1029_slot_sp_guard_late_a.sh`.
s1029's ordinary-dispatch recipe reached VI-1024 but exited after 65 frames
at sticky guest PC `0x8000834c`, before the slot-dispatch family or SP guard.
The only change is postponing the late `a` input to frame 300; do not re-run
the s1028 recipe verbatim and do not reopen M4.

## Competing hypotheses and discriminator

* `H-slot-caller-corrupts-sp`: an invalid guard row at the `+872` entry has a
  return address/register state identifying a caller boundary that already
  carries the wild guest `$sp`.
* `H-slot-entry-or-runtime-corrupts-sp`: an invalid guard row has a valid
  caller boundary but an invalid entry `$sp`, implicating dispatch/runtime
  state.
* `H-no-sp-event`: the run again exits before `slotDispatcherIter` or its
  `+872` family; this is a reachability result and classifies neither model.

Discriminating measurement: the phase-gated run must produce either a
`[slot-sp-guard] INVALID` register dump at the slot-dispatch family or a
slot-dispatch crash/marker. A dump's `ra`/entry registers split the first two
hypotheses; no slot marker with an early `0x8000834c` exit selects only
`H-no-sp-event`.

The loop consumes the recipe automatically between iterations (up to two
recipes, 600s cap). At the next iteration, read the SOAK-RESULTS tail. If an
invalid guard row appears, cross-reference its `ra` against the direct
`slotDispatcherIter` callers. If the run reaches `+872` with zero guard hits,
record a real evaluable null. If it again dies at `0x8000834c` before slot
dispatch, record `H-no-sp-event` and pivot rather than requeueing verbatim.

Do not re-run the M4 accumulator probe (three controlled nulls already
recorded, s1025-s1027) unless a genuinely new discriminator is identified.
