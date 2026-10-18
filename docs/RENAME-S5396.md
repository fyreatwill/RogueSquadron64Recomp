# Generated-symbol audit — Session 5396

Candidate: `fake_func_800B47C4` in the menu overlay.

## Discriminator

The generated body starts at `0x800B47C4` and contains exactly three
instructions, ending at `0x800B47D0`. The project symbol table has the same
address and size (`menuControllerInputPreamble`, `0xC`), followed immediately
by `menuControllerInput` at `0x800B47D0` with size `0x38E4`. The companion
symbol file independently identifies `0x800B47C4` as the splat record preceding
that real menu-controller body. This selects H1: the record is a callable
generated preamble/trampoline, not an unclassified data gap.

The companion file retains the address-coded `fake_func_800B47C4` label, so the
semantic destination is the already-established repository mapping
`menuControllerInputPreamble`; no name was inferred from callers alone.

## Change and verification

`tools/rename_generated_symbols.py` was run with the bounded range
`0x800B47C4 <= address < 0x800B47D0`. It renamed three generated references in
`funcs_31.c`, `funcs.h`, and `recomp_overlays.inl`. A follow-up search found no
remaining `fake_func_800B47C4` reference in the generated tree. No build was
needed: this was a symbol-only generated-tree synchronization.

The other two non-data mismatches in the initial census were not renamed:
`func_8000040C` is already covered by the existing mapping and
`fake_func_800B58B4` remains address-coded because the companion map describes
it only as an invalid/splat record before `playerAwingInit`, with no semantic
name for the record itself.
