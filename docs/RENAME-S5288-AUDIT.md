# Generated-symbol audit — `getNpcContextByIndex`

Session 5288 classified `getNpcContextByIndex = 0x8004013C`.

The companion symbol map records a named callable NPC-slot getter at
`0x8004013C`; the next record is `getNpcContextField8 = 0x8004015C`. The
bounded rename helper scanned `0x8004013C..0x8004015C` and reported
`getNpcContextByIndex: already-synchronized`, with zero renamed references in
zero files. Independent generated-tree inspection found the named declaration,
call sites, and overlay record, with no `func_8004013C`, `fake_func_8004013C`,
or static placeholder.

Conclusion: H1 is selected in the already-synchronized callable sense. H2 and
H3 are ruled out for this address. No build or soak was warranted, and no
generated source was changed.
