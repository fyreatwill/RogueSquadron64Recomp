# Generated-symbol audit — Session 5572

Candidate: `fake_func_8000337C` / `data_gap_8000337C` at `0x8000337C`.

The current generated tree is already synchronized: `RecompiledFuncs/funcs.h`,
`recomp_overlays.inl`, and `funcs_0.c` all use `data_gap_8000337C`, with a
four-byte overlay record. The generated body contains only the isolated
`lw $s7, 0x2C($sp)` at `0x8000337C`, and the next callable body begins at
`setVideoReadyFlag` (`0x80003380`).

The companion `rogue_squadron64/symbol_files/main_overlay.txt` independently
labels the exact address a “four-byte non-callable fragment before
setVideoReadyFlag.” `syms/rogue_squadron.syms.toml` independently gives
`data_gap_8000337C` the same address and size `0x4`. The rename table already
contains the mechanical `fake_func_8000337C` to `data_gap_8000337C` mapping.

Result: H3 selected. There is no new semantic rename or generated-tree change
to make. The next live placeholder by address is `fake_func_8006ACA4`.
