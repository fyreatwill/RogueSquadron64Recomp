# Session 5281 symbol audit: `__osViCurr`

The bounded generated-symbol helper scanned `0x80039210..0x80039240`, made
zero edits, and reported `__osViCurr`, `__osViNext`, and `__osViDevMgr` as
already synchronized. Independent inspection of `rogue_squadron64`'s
`libultra.txt` types `__osViCurr = 0x80039210` as `OSViContext*`; the generated
tree contains no callable placeholder, body, declaration, overlay record, or
direct generated reference at the address. This selects the typed-data
interpretation and rules out callable placeholder propagation. Preserve the
existing name. The next candidate is `__osViNext = 0x80039214`.
