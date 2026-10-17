# Next: continue the generated-symbol sweep

Work unit: classify `reinsertNpcIntoSortedFreeList = 0x8003EC10`, the next
address-ordered companion record after the completed
`unregisterAndFreeNpcSlot` check, with one bounded helper run and independent
generated-tree inspection. Do not build or soak unless the discriminator finds
a callable placeholder or a needed rename.

Before any build, record the competing hypotheses and discriminator in this
file. For the next candidate they are:

- H1: the record is typed data or an already-synchronized named callable.
- H2: the bounded helper misses a callable placeholder at the address.
- H3: generated code contains a callable/data fragment whose semantic name conflicts with the companion record.

Discriminator: combine the helper result with companion typing/description and
searches for a generated body, placeholder, declaration, overlay record, and
direct reference. H1 requires typed data or a matching named callable plus no
placeholder/conflict; H2 requires a callable placeholder/body; H3 requires a
callable fragment or conflicting semantic record.

Exact commands after selecting the address:

`rg -n -C 2 'reinsertNpcIntoSortedFreeList|8003EC10' ../rogue_squadron64/symbol_files`

`python3 tools/rename_generated_symbols.py ../N64Recomp/RecompiledFuncs --companion-dir ../rogue_squadron64/symbol_files --start-address 0x8003EC10 --end-address 0x8003EC14 --limit 1`

`rg -n 'reinsertNpcIntoSortedFreeList|func_8003EC10|fake_func_8003EC10|8003EC10' ../N64Recomp/RecompiledFuncs --glob '*.c' --glob '*.h' --glob '*.inl'`

HYPOTHESIS-ID: generated-symbol-renaming-sweep
