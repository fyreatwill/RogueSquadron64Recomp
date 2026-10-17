# Generated-symbol audit — `safeLookup3DSoundEntry`

Session 5291 classified `safeLookup3DSoundEntry = 0x80088D1C`.

The companion symbol map records a named callable mutex-guarded 3D-sound
lookup wrapper. It gates on the MusyX-active flag, protects the inner linked-
list lookup with the Factor 5 mutex, and is called by 3D-sound NPC handlers.
The bounded rename helper scanned `0x80088D1C..0x80088D20` and reported
`safeLookup3DSoundEntry: already-synchronized`, with zero renamed references
in zero files.

Independent generated-tree inspection found the named callable body in
`funcs_22.c`, its declaration in `funcs.h`, an overlay record, and callers in
the generated functions. There is no `func_80088D1C`,
`fake_func_80088D1C`, or conflicting data fragment.

Conclusion: H1 is selected in the already-synchronized callable sense. H2
and H3 are ruled out for this address. No build or soak was warranted, and no
generated source was changed.
