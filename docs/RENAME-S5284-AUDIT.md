# Session 5284 generated-symbol audit: `osViModeMpalLan1`

The bounded generated-symbol helper was run over `0x80039240..0x80039290`
with the companion symbol files. It renamed zero references in zero files and
reported `osViModeMpalLan1 = 0x80039240` as already synchronized.

Independent inspection found the companion declaration in `libultra.txt`:
`osViModeMpalLan1 = 0x80039240; // type:OSViMode size:0x50`. The generated
tree has no `func_80039240`, `fake_func_80039240`, semantic declaration,
overlay record, or direct generated reference. The address appears only as
instruction comments inside the surrounding `__OSGlobalIntMask` generated
body, which is a data/fragment decode rather than a callable symbol at this
address.

Conclusion: H1 is selected. `osViModeMpalLan1` is typed data already carrying
its human name; no rename, build, or soak is needed. The next companion
candidate is `osViModeNtscLan1 = 0x80039290`.
