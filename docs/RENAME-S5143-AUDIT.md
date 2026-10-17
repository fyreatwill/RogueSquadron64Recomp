# Session 5143 rename audit

Candidate: `_MakeMotorData = 0x8002D710`.

The bounded helper was run with the companion symbol files over
`0x8002D710..0x8002D88C`. It changed zero references and reported
`already-synchronized`.

Independent evidence is consistent with an unmaterialized libultra/ABI entry:
the generated tree has no placeholder or generated body at `0x8002D710`, no
overlay record for the candidate, and no direct generated callers. The
companion map places `osMotorInit` at `0x8002D88C`, giving the candidate span
`0x17C`, but there is no generated body to which that span can be applied.
Preserve the ABI name; no build or soak is needed.
