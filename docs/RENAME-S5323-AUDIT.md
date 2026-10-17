# Generated-symbol rename audit — Session 5323

Candidate: `load_level_hmp = 0x80043D74`.

The bounded candidate check used the companion `main_overlay.txt` map and the
current generated tree. Independent evidence agrees across all five required
lines: the companion map defines `load_level_hmp` at `0x80043D74`; the
generated `funcs_9.c` contains the named body at that address; `funcs.h`
declares it; `recomp_overlays.inl` records the matching overlay offset and
size; and the generated level-loader caller invokes `load_level_hmp`. No
`func_80043D74` or conflicting fragment was found.

H3 is selected: the candidate is already synchronized and has no placeholder
to rename. No generated mapping, build, or soak was warranted. The next
bounded placeholder candidate is `func_800E9AE0 = 0x800E9AE0` in the mission
overlay.
