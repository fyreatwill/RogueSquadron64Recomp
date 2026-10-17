# Session 5285 generated-symbol audit: `osViModeNtscLan1`

The bounded generated-symbol helper was run over `0x80039290..0x800392E0`
with the companion symbol files. It renamed zero references in zero files and
reported `osViModeNtscLan1 = 0x80039290` as already synchronized.

Independent inspection found the companion declaration in `libultra.txt`:
`osViModeNtscLan1 = 0x80039290; // type:OSViMode size:0x50`. The following
companion record is `osViModePalLan1 = 0x800392E0`, establishing the expected
`0x50` data span. The generated tree has no `func_80039290`,
`fake_func_80039290`, semantic declaration, overlay record, or direct
generated reference. The address appears only as instruction/data comments
and generated operations inside the surrounding `__OSGlobalIntMask` body,
which is a data/fragment decode rather than a callable symbol at this address.

Conclusion: H1 is selected. `osViModeNtscLan1` is typed data already carrying
its human name; no rename, build, or soak is needed. The next companion
candidate is `osViModePalLan1 = 0x800392E0`.
