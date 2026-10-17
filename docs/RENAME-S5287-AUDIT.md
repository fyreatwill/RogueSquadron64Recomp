# Generated-symbol audit — `osViModeTable`

Session 5287 classified `osViModeTable = 0x80039330`.

The companion symbol map records `OSViMode[42]` data of size `0xD20`, ending
at `0x80040050`. The bounded rename helper scanned that range and reported
`osViModeTable: already-synchronized`, with zero renamed references in zero
files. Independent generated-tree inspection found only a `nop` at the data
start in `funcs_8.c`; there was no callable body, placeholder, declaration,
overlay record, or direct generated reference for the address.

Conclusion: H1 is selected. This is typed data, not an unmaterialized or
misnamed callable. No build or soak was warranted, and no generated source
was changed.
