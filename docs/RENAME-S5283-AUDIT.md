# Session 5283 generated-symbol audit: `__osViDevMgr`

The bounded generated-symbol helper was run over `0x80039220..0x80039240`
with the companion symbol files. It renamed zero references in zero files and
reported `__osViDevMgr = 0x80039220` as already synchronized.

Independent inspection found the companion declaration in `libultra.txt`:
`__osViDevMgr = 0x80039220; // type:OSDevMgr size:0x1C`. The generated tree
contains only the instruction/data fragment `nop` at `0x80039220`; it has no
callable body, placeholder symbol, declaration, overlay record, or direct
generated reference at that address.

Conclusion: H1 is selected. `__osViDevMgr` is typed data already carrying its
human name; no rename, build, or soak is needed. The next companion candidate
is `osViModeMpalLan1 = 0x80039240`.
