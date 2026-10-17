# Generated-symbol rename audit — Session 5322

Candidate: `markHighLodCellsInGrid = 0x80043C30`.

The bounded helper, run with the companion `main_overlay.txt` map, reported
`renamed 0 references in 0 files` and `already-synchronized`.

Independent evidence agrees across all five required lines: the companion map
defines the name at `0x80043C30`; `RecompiledFuncs/funcs_9.c` contains the
named body at that address; `funcs.h` declares it; `recomp_overlays.inl`
records it at the matching overlay offset and size; and `funcs_10.c` contains
a generated caller using the named symbol. No `func_80043C30` or conflicting
fragment was found.

H3 is selected: this candidate is already synchronized and has no placeholder
to rename. No generated mapping, build, or soak change was warranted. The
next bounded candidate is `load_level_hmp = 0x80043D74`.
