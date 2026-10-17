# Session 5145 rename audit: `osPfsAllocateFile`

Candidate: `osPfsAllocateFile = 0x8002EBE0`.

The bounded rename helper reported `already-synchronized` and made zero
edits. The generated tree contains only the ABI declaration
`osPfsAllocateFile_recomp` and one direct generated call site, at the call
from `0x80005C64` in `funcs_2.c`; it has no generated function body or
placeholder at the companion address. The overlay table entry has offset
`0x2E7A0` and `rom_size = 0`. The next companion entry is
`__osPfsDeclarePage = 0x8002F064`, giving a companion span of `0x484` bytes,
but no generated body occupies that span.

Conclusion: classify `osPfsAllocateFile` as an unmaterialized libultra/ABI
entry and preserve its `_recomp` name. There is no generated body or semantic
body span to rename.
