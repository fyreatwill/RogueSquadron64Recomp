# Generated-symbol audit — `getNpcContextField8`

Session 5289 classified `getNpcContextField8 = 0x8004015C`.

The companion symbol map records a named callable NPC-slot getter with 59
callers. Its documented behavior is to index `gNpcSlotList` and return the
context field at offset `0x8`, or zero for an empty slot. The bounded rename
helper scanned `0x8004015C..0x80040160` and reported
`getNpcContextField8: already-synchronized`, with zero renamed references in
zero files.

Independent generated-tree inspection found the named callable body in
`funcs_9.c`, its declaration in `funcs.h`, call sites, and an overlay record.
There is no `func_8004015C`, `fake_func_8004015C`, or conflicting data
fragment.

Conclusion: H1 is selected in the already-synchronized callable sense. H2 and
H3 are ruled out for this address. No build or soak was warranted, and no
generated source was changed.
