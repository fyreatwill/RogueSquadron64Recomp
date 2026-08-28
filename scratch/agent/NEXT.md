# NEXT work unit — exact companion identity after `0x800C63C0`

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Single work unit

Resume the generated-symbol sweep at the next unresolved project-TOML
placeholder after the renamed `0x800C63C0` entry. Select one candidate with an exact companion identity,
then audit its companion symbol entry, generated body, callers, header,
overlay registration, project TOML, and local duplicates. Rename only if the
identity and semantics agree; otherwise record why the placeholder remains.
This is a bounded static change and requires no build or runtime run.

## Competing hypotheses

- H-ExactIdentity: the next candidate has a defensible human name in the companion project and can be renamed safely.
- H-BoundaryOnly: the candidate is a fragment, data gap, or boundary without enough semantic evidence and must remain `func_*`.
- H-MappingDrift: companion and generated metadata disagree, so synchronization is needed before any rename.

## Discriminating measurement

The candidate audit must compare all six surfaces: companion identity, body,
callers, header, overlay registration, and project TOML. Agreement across all
six with coherent local semantics selects H-ExactIdentity; an unresolved
fragment/data boundary selects H-BoundaryOnly; any address/name mismatch
selects H-MappingDrift. Land one regeneration-safe rename or a new bounded
audit documenting why no rename is justified.

## Exact commands

1. `grep -n '^## Session ' PORTING-STATE.md | tail -15`
2. Inspect the next candidate after `0x800C63C0` in the companion symbol file,
   generated `RecompiledFuncs/funcs_*.c`, `funcs.h`, `recomp_overlays.inl`,
   and `syms/rogue_squadron.syms.toml`.
3. Record the six-surface comparison in a new
   `scratch/agent/s<next>_generated_symbol_rename/AUDIT.md`.

The next candidate is the first remaining `name = "func_..."` entry in
`syms/rogue_squadron.syms.toml` after `0x800C63C0`; inspect it before selecting
the address. Exact agreement selects `H-ExactIdentity` and permits a
regeneration-safe rename; a fragment/data gap selects `H-BoundaryOnly`; any
disagreement selects `H-MappingDrift` and requires synchronization before
renaming.
