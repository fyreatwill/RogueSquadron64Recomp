# NEXT work unit (s2970)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Unit

Perform one bounded generated-symbol census/rename at the next unresolved
address in the current generated tree. Reconcile the companion map, project
TOML, generated artifacts, and regeneration-safe rename table; rename only if
the function has a defensible semantic identity or mechanically proven data
gap. Otherwise record the classification and leave the placeholder unchanged.
Do not touch guest behavior or `lib/`.

## Competing hypotheses and discriminator

- H-named: companion source, caller structure, or exact local semantics give
  one defensible human name.
- H-data-gap: the body is a mechanically proven non-callable gap bounded by
  independent functions/data and should use a `data_gap_...` name.
- H-ambiguous: the bytes are a callable fragment/preamble without enough
  evidence for a semantic name and must remain a placeholder.

The discriminator is the bounded source table for the next unresolved
placeholder: generated disassembly/body bounds, callers/lookup references,
companion-map classification, and successor/predecessor boundaries. A rename
or data-gap reconciliation is a result; an ambiguous classification is also a
result but must not synthesize a name.

## Commands

1. Run `grep -n '^## Session ' PORTING-STATE.md | tail -15`; if all 15 titles
   are sweep-scoped, perform the mandated external retail-entry or M4
   accumulator-boundary revisit instead of another sweep step.
2. Census the next unresolved generated placeholder and its companion-map
   entry; make any rename through the existing regeneration-safe scripts.
3. Build the affected generated target and verify the exact changed symbol(s).
4. Write a source table under `scratch/agent/s2970_generated_symbol_rename/`.

Expected outcomes: one defensible semantic rename or data-gap reconciliation
advances the sweep; otherwise an evidence-backed ambiguous classification parks
the address without inventing a name.
