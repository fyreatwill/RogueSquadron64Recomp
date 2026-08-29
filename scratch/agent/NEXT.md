# NEXT work unit — resume the generated-symbol sweep

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Single work unit

Perform one bounded six-surface audit of the next unresolved project
`fake_func_*`/placeholder symbol after the last synchronized sweep entry.
Use the companion map, generated body, callers, generated header and overlay
registration, project TOML, and rename tooling. Preserve the placeholder when
the evidence only supports a fragment/data gap or cannot establish semantics.

## Competing hypotheses

- H-SemanticName: all six surfaces and the companion map establish one human
  function identity.
- H-Fragment: the record is a non-callable instruction fragment or data gap;
  only a mechanical `data_gap_*` name is justified.
- H-Unresolved: the surfaces disagree or do not establish callability or
  semantics; preserve the placeholder and document the boundary.

## Discriminating measurement

For the selected placeholder, record exact evidence for all six surfaces. A
stable human identity selects H-SemanticName; a bounded non-callable fragment
selects H-Fragment; disagreement or insufficient evidence selects
H-Unresolved. Do not invent a semantic name.

## Exact commands

1. `grep -n '^## Session ' PORTING-STATE.md | tail -15` (REVISIT check).
2. Locate the next unresolved placeholder with bounded `rg`/`sed` searches in
   `../N64Recomp/RecompiledFuncs`, `../rogue_squadron64`, `syms`, and rename
   tooling.
3. Save the six-surface audit under
   `scratch/agent/s3106_generated_symbol_rename/` and update synchronized
   symbol surfaces only if the evidence selects a safe name.
