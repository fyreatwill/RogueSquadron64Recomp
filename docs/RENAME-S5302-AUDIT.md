# Generated-symbol audit — Session 5302

Candidate: `spawnInheritedNpcVariantB = 0x8003F880`.

The bounded helper command was:

```text
python3 tools/rename_generated_symbols.py ../N64Recomp/RecompiledFuncs --companion-dir ../rogue_squadron64/symbol_files --start-address 0x8003F880 --end-address 0x8003F884 --limit 1
```

It reported `already-synchronized` and renamed zero references in zero files.
Independent `rg` inspection found the named callable body in
`../N64Recomp/RecompiledFuncs/funcs_9.c`, its declaration in `funcs.h`, its
overlay record in `recomp_overlays.inl`, and a direct caller in `funcs_19.c`.
There was no `func_8003F880` placeholder or conflicting generated fragment.

Conclusion: H1 is selected for this address. H2 and H3 are ruled out for this
candidate. No build or soak was warranted. The next bounded candidate is
`spawnInheritedNpcVariantC = 0x8003FA14`.
