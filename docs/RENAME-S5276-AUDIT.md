# Session 5276 symbol audit: `__osSiAccessQueueEnabled`

The bounded companion-symbol helper scanned `0x80039170..0x800391B0`, made
zero edits, and reported `__osSiAccessQueueEnabled` as already synchronized.

Independent checks found the companion declaration at `0x80039170` as
`type:u32` data in `libultra.txt`. The generated tree contains only a `nop`
at that address inside the surrounding `__OSGlobalIntMask` data/fragment
decode, with no distinct callable body, placeholder, header declaration,
overlay record, or direct generated reference.

This selects the typed-data interpretation and rules out callable placeholder
propagation. Preserve the existing name; no build or soak is needed. The next
candidate is `vi = 0x800391B0`.
