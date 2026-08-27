# NEXT work unit (s2810) — sweep generated symbols at 0x8014B000..0x8014D000

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Work unit

Run the regeneration-safe companion selector for
`0x8014B000..0x8014D000`, independently scan the generated tree for
placeholders in that interval, and apply only source-backed semantic names.
Preserve ambiguous/data entries. This is a bounded rename work unit; do not
run a game soak.

## Competing hypotheses and discriminator

- H-semantic-placeholder: a companion semantic symbol maps to a generated
  placeholder in this interval, so a bounded regeneration-safe rename is
  justified.
- H-ambiguous-data: candidates are fake/data or otherwise ambiguous, so no
  rename is safe and the interval must be closed without changes.
- H-already-synchronized: the generated tree has no placeholder definitions or
  references in the interval, so the selector should make no changes.

The discriminator is the complete selector decision table plus the
independent generated-tree placeholder scan. A selected semantic rename and
matching generated references selects H-semantic-placeholder; preserved
ambiguous entries with zero selected references selects H-ambiguous-data; an
empty placeholder scan selects H-already-synchronized.

## Exact commands

```sh
python3 tools/rename_generated_symbols.py \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs \
  --companion-dir /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files \
  --start-address 0x8014B000 --end-address 0x8014D000 --limit 32
rg -n 'func_8014|fake_func_8014' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs
git diff --check
```
