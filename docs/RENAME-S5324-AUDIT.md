# Generated-symbol rename audit — Session 5324

Candidate: `func_800E9AE0 = 0x800E9AE0`.

The bounded audit checked the companion mission-overlay symbols, the generated
body and declaration, the overlay record, callers, and nearby conflicting
fragments. The evidence is:

- `symbol_files/mission_overlay.txt` deliberately retains `func_800E9AE0` and
  documents that the apparent `func_800E9B10` split is false.
- `RecompiledFuncs/funcs_39.c` contains one complete `0x114`-byte body from
  `0x800E9AE0` through its epilogue; `0x800E9B10` is an interior instruction.
- `RecompiledFuncs/funcs.h` declares the address-coded symbol.
- `RecompiledFuncs/recomp_overlays.inl` records the same mission-overlay entry
  at offset `0x449B0` with size `0x114`.
- No generated caller references `func_800E9AE0`; the only nearby conflicting
  name is main-overlay `initObjectAnimAndDetail = 0x800E9B10`, which is the
  documented false split and not this function.

H2 is selected: the exact span is established, but the companion map supplies
no semantic name and the live-caller gate is empty. The existing mechanical
mapping entry is not evidence for a rename, so no generated-symbol edit,
build, or soak was warranted. The sweep is parked pending a new candidate;
the next work unit returns to the M4 accumulator boundary.
