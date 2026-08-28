# NEXT work unit (s2951) — classify generated placeholder at 0x80099FDC

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Context

s2950 passed the F5 control and live route hook but stopped pre-title; the M5
source-word discriminator is paused until a genuinely new route repair. The
next unresolved generated placeholder after s2942 is `0x80099FDC` in
`RecompiledFuncs/funcs_26.c`.

## Competing hypotheses and discriminator

- H-Callable: it is a standalone callable function and must retain a callable
  symbol or receive an exact companion semantic name.
- H-Fragment: it is a callable-ambiguous split executable fragment; leave all
  names unchanged.
- H-DataGap: it is a proven non-callable gap/fixup artifact; rename it to
  `data_gap_80099FDC` across every generated and source map.

Discriminate with one bounded source table: inspect the complete generated
body and exact predecessor/successor boundaries, then search all generated
callers, independent lookups, returns/prologues, and companion m2c/map names.
Only a standalone return/prologue plus an independent caller/lookup or an
exact companion semantic name authorizes a callable rename; otherwise valid
instructions remain ambiguous, while a mechanically bounded non-callable
record authorizes a data-gap rename.

## Exact work

1. Read the bounded body around `0x80099FDC` in
   `/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_26.c`.
2. Search the project map, companion symbol file, generated callers, and
   regeneration-safe rename table for `80099FDC` and its placeholder name.
3. Write the complete classification to
   `scratch/agent/s2951_generated_symbol_rename/source-table.md`.
4. If and only if the table proves H-DataGap or supplies an exact semantic
   name, apply the bounded rename through the existing rename tooling and
   build the Debug `RecompiledFuncs` target; otherwise leave code unchanged.
