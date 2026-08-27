# NEXT work unit (s2736) — bounded generated-symbol region

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Work unit

Continue the generated-symbol sweep over the next unexamined adjacent region
`0x800D1000..0x800D4000`. Rename only exact semantic companion matches;
preserve address-only, fake, conflicting, or protected placeholders. M5
publication remains unresolved; no M5 runtime experiment is authorized unless
a genuinely new named publication surface appears.

## Competing hypotheses and discriminator

- H-exact-matches: the region contains stale `func_0x...` names with unique
  semantic companion mappings; the tool selects and changes them.
- H-already-synchronized: semantic companion candidates are already named in
  generated output; the tool changes zero references.
- H-ambiguous-or-fake: remaining candidates are address-only, fake, or
  conflicting; they are preserved.

The discriminator is the complete tool decision table for this bounded
region: selected candidates, changed references/files, already-synchronized
entries, ambiguous-or-fake entries, and parser/duplicate-name failures.

## Exact command

```sh
mkdir -p scratch/agent/s2736_generated_symbol_sweep
python3 tools/rename_generated_symbols.py \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs \
  --companion-dir /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files \
  --start-address 0x800D1000 --end-address 0x800D4000 --limit 32 \
  --require-rename \
> scratch/agent/s2736_generated_symbol_sweep/decision-table.txt
```

Create `scratch/agent/s2736_generated_symbol_sweep/` before running the
command and redirect there. Review the decision table and generated diff. A
status 2 from `--require-rename` means the region had no safe rename; record
that result and advance the region. Do not build or run the game for a
symbol-only change, and do not invent names from implementation shape.
