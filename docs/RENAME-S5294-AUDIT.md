# Session 5294 generated-symbol audit

Candidate: `unregisterAndFreeNpcSlot = 0x8003E7D0`.

Competing hypotheses:

- H1: the companion record is typed data or an already-synchronized named callable.
- H2: the bounded helper misses a callable placeholder at the address.
- H3: generated code contains a callable/data fragment whose semantic name conflicts with the companion record.

Discriminator: compare the bounded helper result with the companion description and independent searches for a generated body, placeholder, declaration, overlay record, and direct references.

Evidence:

- `rename_generated_symbols.py` reported `already-synchronized` and renamed zero references in zero files.
- The companion map describes a 127-caller NPC-slot unregister/free-list routine at `0x8003E7D0`.
- `../N64Recomp/RecompiledFuncs/funcs_8.c` contains the complete named `RECOMP_FUNC` body beginning at the candidate address; its operations match the described count decrement, compacting shift, and free-list unlink.
- `funcs.h` declares `unregisterAndFreeNpcSlot`, `recomp_overlays.inl` registers it, and generated callers resolve to that name across multiple `funcs_*.c` files.
- No `func_8003E7D0` or `fake_func_8003E7D0` placeholder was found.

H1 is selected in the already-synchronized callable sense. H2 and H3 are ruled out for this address. No build or soak was warranted. The next address-ordered companion candidate is `reinsertNpcIntoSortedFreeList = 0x8003EC10`.
