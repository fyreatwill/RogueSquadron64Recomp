# NEXT work unit (s2954) — classify the next unparked generated placeholder

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Context

s2953 classified `0x8009D978` as the mechanically non-callable audio
coefficient table `data_gap_8009D978` and built `RecompiledFuncs`. M5 is
paused after the pre-title route stop, so continue the generated-symbol sweep
at the next unparked candidate after `0x8009D978`.

## Competing hypotheses and discriminator

- H-Callable: the next candidate is a standalone callable function with an
  exact companion semantic name.
- H-Fragment: it is a callable-ambiguous split executable fragment; leave all
  names unchanged.
- H-DataGap: it is a proven non-callable gap/fixup artifact; rename it to a
  `data_gap_...` name across every generated and source map.

Discriminate with one bounded source table: inspect the complete generated
body and exact predecessor/successor boundaries, then search all generated
callers, independent lookups, returns/prologues, and companion m2c/map names.
Only a standalone return/prologue plus an independent caller/lookup or an
exact companion semantic name authorizes a callable rename; otherwise valid
instructions remain ambiguous, while a mechanically bounded non-callable
record authorizes a data-gap rename.

## Exact work

1. Identify the next unparked placeholder after `0x8009D978` in the project
   symbol map and generated overlay order; expected first candidate is
   `0x800AA6CC`, subject to the sweep census.
2. Inspect its complete body and exact predecessor/successor boundaries;
   search generated callers, independent lookups, and the companion map.
3. Write the complete classification to a new
   `scratch/agent/s2954_generated_symbol_rename/source-table.md`.
4. Apply a bounded rename and build `RecompiledFuncs` only if an exact
   semantic name or mechanically proven data gap is found; otherwise preserve
   the placeholder.
