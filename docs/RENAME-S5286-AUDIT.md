# Session 5286 generated-symbol audit: `osViModePalLan1`

The bounded generated-symbol helper was run over `0x800392E0..0x80039330`
with the companion symbol files. It renamed zero references in zero files and
reported `osViModePalLan1 = 0x800392E0` as already synchronized.

Independent inspection found the companion declaration in `libultra.txt`:
`osViModePalLan1 = 0x800392E0; // type:OSViMode size:0x50`. The next companion
record is `osViModeTable = 0x80039330; // type:OSViMode[42] size:0xD20`.
The generated tree has no `func_800392E0`, `fake_func_800392E0`, semantic
declaration, overlay record, or direct generated reference. The address occurs
only in the apparent instruction/data fragment following the preceding
`__OSGlobalIntMask` decode, not in a callable symbol at this address.

Conclusion: H1 is selected. `osViModePalLan1` is typed data already carrying
its human name; no rename, build, or soak is needed. The next companion
candidate is `osViModeTable = 0x80039330`.
