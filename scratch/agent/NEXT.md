# NEXT work unit (s2462) — audit slot-dispatch callback provenance

HYPOTHESIS-ID: m5-generated-alternate-equivalence

## Work unit

Perform one bounded static audit of every generated `slotDispatcherIter` caller
and every writer to the callback field consumed at `0x8003E974`. Join each
caller with its selector/slot construction and classify whether the callback
is initialized to zero, a valid generated target, or an unresolved value. Do
not add runtime instrumentation, guards, or change dispatch/audio behavior.

## Competing hypotheses and discriminator

- H-ZeroWriter: a reachable caller writes or preserves `update_func==0` in a
  slot that is later dispatched.
- H-ValidWriter: reachable callers initialize a nonzero callback, so the
  observed pre-target failure is outside the explicit zero-update edge.
- H-UnresolvedWriter: the callback comes from an unclassified copied or
  overlay-produced value, so static provenance is incomplete.

The discriminator is a complete table of all generated callers plus callback
writers: any reachable zero writer selects H-ZeroWriter; all reachable writers
nonzero selects H-ValidWriter; an unresolved/copy-only path selects
H-UnresolvedWriter. A partial census is explicitly non-discriminating.

The discriminator is one phase-scoped row joining the slot pre-call's
`update_func`, the resolver's requested address, and the indirect positive
control. `update_func=0` immediately followed by `get_function(0)` selects
H-ZeroUpdateTerminal. A nonzero update pointer followed by match-path failure
selects H-NonzeroSlotThenMatch. Missing positive-control resolution requires a
corrected capture.

## Exact commands

1. Locate the generated function tree and run a bounded `rg` census for every
   `slotDispatcherIter` caller and every store/load of the callback field;
   inspect a maximum 60-line window around each distinct site.
2. Cross-check every candidate against `syms/rogue_squadron.syms.toml` and the
   overlay table so overlay aliases are not counted as independent writers.
3. Write `scratch/agent/s2462_m5_slot_callback_provenance/audit.md` with the
   complete caller/writer table and selected outcome. No runtime run is
   needed unless the static table cannot classify a site.
