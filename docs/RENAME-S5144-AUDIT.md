# Session 5144 rename audit: `osMotorInit`

Candidate: `osMotorInit = 0x8002D88C`.

The bounded rename helper reported `already-synchronized` and made zero
edits. The generated tree contains the ABI declaration `osMotorInit_recomp`
and four direct generated call sites, but no generated function body or
placeholder at the companion address. The overlay table entry has offset
`0x2D44C` and `rom_size = 0`. The next companion entry is
`osPfsAllocateFile = 0x8002EBE0`.

Conclusion: classify `osMotorInit` as an unmaterialized libultra/ABI entry
and preserve its `_recomp` name. There is no generated body or semantic body
span to rename.
