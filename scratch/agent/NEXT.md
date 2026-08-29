# NEXT work unit — audit `fake_func_800B58B4`

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Single work unit

Audit the next unresolved project-TOML placeholder, `fake_func_800B58B4`,
which is in the menu overlay. Compare its companion symbol entry, generated
body, callers, header, overlay registration, project TOML, and local
duplicates. Rename only if an exact semantic identity is independently
supported; otherwise record why it remains a placeholder/data-gap name.
This is one bounded static audit and requires no build or runtime run.

## Competing hypotheses

- H-ExactIdentity: companion evidence names a real callable routine or
  bounded semantic preamble and all
  six surfaces agree, permitting a regeneration-safe rename.
- H-BoundaryOnly: the address is a fragment, invalid decode, or data gap and
  must remain address-derived.
- H-MappingDrift: companion and generated/project metadata disagree, so the
  entry needs synchronization or must remain unresolved.

## Discriminating measurement

Compare all six surfaces for `0x800B58B4`: companion identity, generated body, callers, header,
overlay registration, and project TOML, including duplicate-address entries.
Coherent callable semantics plus exact agreement selects H-ExactIdentity;
invalid/data-boundary evidence selects H-BoundaryOnly; any address, extent,
overlay, or name disagreement selects H-MappingDrift. Land one
regeneration-safe rename or a new bounded audit explaining why no rename is
justified.

## Exact commands

1. `grep -n '^## Session ' PORTING-STATE.md | tail -15`
2. Inspect `fake_func_800B58B4` in the companion menu symbol file, generated
   `RecompiledFuncs/funcs_*.c`, `funcs.h`, `recomp_overlays.inl`, and
   `syms/rogue_squadron.syms.toml`.
3. Record the six-surface comparison in
   `scratch/agent/s<next>_generated_symbol_rename/AUDIT.md`.
