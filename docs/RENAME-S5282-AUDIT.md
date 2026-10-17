# Session 5282 generated-symbol audit: `__osViNext`

The bounded helper was run over `0x80039214..0x80039220` with the companion
symbol files. It renamed zero references in zero files and reported
`__osViNext = 0x80039214` as already synchronized.

Independent checks found the companion declaration in `libultra.txt`:
`__osViNext = 0x80039214; // type:OSViContext*`. The generated tree contains
only the instruction/data fragment at `0x80039214`; it has no callable body,
placeholder symbol, declaration, overlay record, or direct generated
reference at that address.

Conclusion: H1 is selected. `__osViNext` is typed data already carrying its
human name; no rename, build, or soak is needed.
