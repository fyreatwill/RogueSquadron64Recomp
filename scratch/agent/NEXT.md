# NEXT work unit (s2463) — capture dynamic slot callback provenance

HYPOTHESIS-ID: m5-generated-alternate-equivalence

## Work unit

After arming and passing the retail oracle's whole-RDRAM positive control and
hangar phase control, build one phase-gated port capture for the dynamic handler
argument at `spawnNpcOfType` (`0x800400BC`), the resulting context `+0x00`
write, and the `slotDispatcherIter` pre-dispatch value. Retain the indirect
resolver positive control. Do not add guards or change dispatch/audio behavior.

## Competing hypotheses and discriminator

- H-ZeroWriter: a reachable caller writes or preserves `update_func==0` in a
  slot that is later dispatched.
- H-ValidWriter: reachable callers initialize a nonzero callback, so the
  observed pre-target failure is outside the explicit zero-update edge.
- H-UnresolvedWriter: the callback comes from an unclassified copied or
  overlay-produced value, so static provenance is incomplete.

The discriminator is the same-run joined tuple `(handler argument,
context+0 write, pre-dispatch update_func, phase, indirect-control-fired)`.
An argument and write of zero that reaches a target-phase dispatch selects
H-ZeroWriter. A nonzero argument/write followed by a zero pre-dispatch value
selects H-PostWriteClobber. A nonzero argument/write and nonzero pre-dispatch
value followed by the known failure selects H-NonzeroSlotThenMatch. Missing
tuples or a failed positive control are non-results and require a corrected
capture.

## Exact commands

1. Run the retail oracle positive-control recipe from `tools/oracle/README.md`
   and retain its whole-RDRAM and hangar-phase counts.
2. Add all three port capture points in one generated/fixup build, with phase
   gating and bounded rows; run the qualified route from `docs/CURRENT-TRUTH.md`.
3. Compare only joined rows with the indirect resolver control and write
   `scratch/agent/s2463_m5_dynamic_callback_capture/audit.md`. If the port
   dies before a tuple, report a qualified non-result and isolate the earliest
   missing boundary next; do not infer callback polarity.
