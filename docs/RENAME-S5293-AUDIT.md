# Generated-symbol audit — `allocateNpcSlot`

Session 5293 classified `allocateNpcSlot = 0x8003E5F8`.

The companion map records a named callable that pops the NPC free-list head,
returns `-1` when the list is empty, and optionally registers the slot in a
context array. The bounded rename helper scanned `0x8003E5F8..0x8003E5FC`
and reported `allocateNpcSlot: already-synchronized`, with zero renamed
references in zero files.

Independent generated-tree inspection found the named callable body in
`funcs_8.c`, its declaration in `funcs.h`, an overlay record, and callers in
`funcs_9.c`, `funcs_13.c`, `funcs_29.c`, `funcs_30.c`, and `funcs_40.c`. There
is no `func_8003E5F8`, `fake_func_8003E5F8`, or conflicting data fragment.

Conclusion: H1 is selected in the already-synchronized callable sense. H2
and H3 are ruled out for this address. No build or soak was warranted, and no
generated source was changed.
