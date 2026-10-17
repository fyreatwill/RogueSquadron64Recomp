# Generated-symbol audit — `initNpcSlotList`

Session 5292 classified `initNpcSlotList = 0x8003E560`.

The companion map records a named callable that allocates the NPC slot list,
builds its 0x800-entry doubly-linked free list, and seeds the sentinel state.
The bounded rename helper scanned `0x8003E560..0x8003E564` and reported
`initNpcSlotList: already-synchronized`, with zero renamed references in zero
files.

Independent generated-tree inspection found the named callable body in
`funcs_8.c`, its declaration in `funcs.h`, an overlay record, and callers in
`funcs_27.c`, `funcs_33.c`, and `funcs_42.c`. There is no
`func_8003E560`, `fake_func_8003E560`, or conflicting data fragment.

Conclusion: H1 is selected in the already-synchronized callable sense. H2
and H3 are ruled out for this address. No build or soak was warranted, and no
generated source was changed.
