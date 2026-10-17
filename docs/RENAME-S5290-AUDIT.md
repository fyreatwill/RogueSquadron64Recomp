# Generated-symbol audit — `factor5RemoveListNode`

Session 5290 classified `factor5RemoveListNode = 0x80098DE0`.

The companion symbol map records a named callable list-unlink function with
67 callers. Its documented behavior removes a node from a doubly-linked list,
updates the list head at `0x80153414`, and gates on the MusyX-active flag at
`0x800A0F50`. The bounded rename helper scanned
`0x80098DE0..0x80098DE4` and reported
`factor5RemoveListNode: already-synchronized`, with zero renamed references in
zero files.

Independent generated-tree inspection found the named callable body in
`funcs_26.c`, its declaration in `funcs.h`, an overlay record, and numerous
call sites. There is no `func_80098DE0`, `fake_func_80098DE0`, or conflicting
data fragment.

Conclusion: H1 is selected in the already-synchronized callable sense. H2 and
H3 are ruled out for this address. No build or soak was warranted, and no
generated source was changed.
