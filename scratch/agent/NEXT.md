# Next: continue the generated-symbol sweep

Work unit: classify `getNpcContextField8 = 0x8004015C`, the next companion
record after the completed `0x8004013C` check, with one bounded helper run and
independent generated-tree inspection. Do not build or soak unless the
discriminator finds a callable placeholder or a needed rename.

Before any build, record the competing hypotheses and discriminator in this
file. For the next candidate they are:

- H1: the record is typed data or an already-synchronized ABI symbol.
- H2: the bounded helper misses a callable placeholder at the address.
- H3: generated code contains a callable/data fragment whose semantic name
  conflicts with the companion record.

Discriminator: combine the helper result with companion typing and searches for
a generated body, placeholder, declaration, overlay record, and direct
reference. H1 requires typed data plus no callable evidence; H2 requires a
callable placeholder/body; H3 requires a callable fragment or conflicting
semantic record.

Exact commands after selecting the address:

`rg -n -C 2 '<symbol>|<address>' ../rogue_squadron64/symbol_files`

`python3 tools/rename_generated_symbols.py ../N64Recomp/RecompiledFuncs --companion-dir ../rogue_squadron64/symbol_files --start-address <start> --end-address <end> --limit 1`

`rg -n '<symbol>|func_<address>|fake_func_<address>|<address>' ../N64Recomp/RecompiledFuncs --glob '*.c' --glob '*.h' --glob '*.inl'`

HYPOTHESIS-ID: generated-symbol-renaming-sweep
