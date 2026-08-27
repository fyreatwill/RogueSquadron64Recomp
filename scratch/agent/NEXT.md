# NEXT work unit (s2616) — continue the generated-symbol rename sweep

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Single work unit

Audit the next bounded placeholder span after `0x800E8A34` in the companion
symbol files, generated declarations/implementations, m2c/source, and callers.
Rename only a complete callable or a companion-supported duplicate/preamble
fragment, using `tools/rename/build_redefs.py`; leave unresolved boundary
fragments unchanged. This is a static source change, not a runtime experiment.

## Competing hypotheses and discriminator

- `H-DefensibleName`: the companion or clear local semantics identifies a
  stable human name for the next placeholder.
- `H-BoundaryOnly`: the placeholder is an incomplete fragment, duplicate
  boundary, or data artifact with no defensible semantic name.
- `H-AlreadyNamed`: an existing generated/companion symbol already captures
  the address and no new mapping is warranted.

The discriminator is one complete static table for the selected address span:
exact bytes/instructions, companion symbol/deletion comments, generated
symbol, m2c/source match, caller/alias evidence, and the proposed name. A
companion-supported name selects `H-DefensibleName`; only-boundary evidence
selects `H-BoundaryOnly`; an existing stable name selects `H-AlreadyNamed`.

## Exact checks

1. Locate the next placeholder and inspect the complete bounded span plus
   companion evidence; record the hypotheses/table before changing anything.
2. Add only a supported mapping to `tools/rename/build_redefs.py` and run its
   generator validation. Do not regenerate the runtime in this static sweep.
3. Record the exact mapping or the reason the placeholder remains unchanged in
   the ledger; no soak is required for a symbol-only change.
