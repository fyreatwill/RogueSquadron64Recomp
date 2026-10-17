# Session 5142 rename audit

Candidate: `osMotorStart = 0x8002D570`.

The bounded helper was run with the companion symbol files over
`0x8002D570..0x8002D88C`. It changed zero references and reported
`already-synchronized`; the helper also reported neighboring companion
`_MakeMotorData = 0x8002D710` as already synchronized.

Independent generated-tree inspection found only the existing
`osMotorStart_recomp` ABI declaration, one generated call site, and a
zero-size overlay record at `0x0002D130`. There is no placeholder or generated
body at the companion address, and the companion map places `osMotorInit` at
`0x8002D88C`. There is therefore no body or exact generated span to rename;
preserve the ABI name as an unmaterialized libultra entry. No build or soak is
needed.
