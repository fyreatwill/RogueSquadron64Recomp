# NEXT work unit (s2754) — bounded generated-symbol rename batch

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Work unit

Continue the source-backed generated-symbol sweep with the bounded interval
`0x800EB000..0x800ED000`. Run the required revisit check first. Use the
companion-backed decision table, apply only exact mappings from that table,
and preserve ambiguous, fake, and address-only placeholders. This is a real
rename batch; no CMake build is required for a source-only generated-symbol
change.

## Competing hypotheses and discriminator

- H2-exact: at least one stale placeholder has an exact companion/source-backed
  semantic name, so the tool renames it.
- H3-ambiguous: candidates exist but evidence is insufficient; preserve them
  and record the ambiguity.
- H4-synchronized: every defensible candidate is already synchronized; preserve
  placeholders and advance to the next bounded interval.

The discriminator is the single bounded tool decision table plus bounded
reference verification. Any exact mapping selects H2; candidates all marked
ambiguous select H3; no stale semantic placeholder selects H4.

## Exact commands

1. `grep -n '^## Session ' PORTING-STATE.md | tail -15`
2. `python3 tools/rename_generated_symbols.py /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs --companion-dir /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files --start-address 0x800EB000 --end-address 0x800ED000 --limit 32 --require-rename`
3. Verify changed symbols and references with bounded `rg`, then save the
   decision table under `scratch/agent/s2754_generated_symbol_sweep/`.
