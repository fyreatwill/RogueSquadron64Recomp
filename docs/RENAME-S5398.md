# Generated-symbol audit — Session 5398

The bounded candidate was `func_8000040C` in the live sibling tree
`../N64Recomp/RecompiledFuncs`.

The generated body starts at `0x8000040C` and ends at `0x80000440`, exactly
`0x34` bytes. `funcs.h` and `recomp_overlays.inl` reference the same callable
entry and ROM span. The companion `rogue_squadron64/tools/make_elf.py`
hard-codes this entry's address and `0x34`-byte size; it does not provide a
semantic label for the entry. The checked-in `syms/rogue_squadron.syms.toml`
has the existing exact mapping `clearMemory16ByteBlocks` at that address and
size. This selects H1 for the bounded existing mapping; it does not claim a
new companion-source name inference.

`tools/rename_generated_symbols.py` was run only for
`0x8000040C <= address < 0x80000440` and renamed five references in
`funcs_0.c`, `funcs.h`, and `recomp_overlays.inl`. A follow-up search found no
`func_8000040C` in those generated surfaces. No runtime build or soak was
needed for this symbol-only synchronization.
