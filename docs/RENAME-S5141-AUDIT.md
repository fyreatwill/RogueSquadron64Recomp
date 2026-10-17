# Session 5141 rename audit

Candidate: `osMotorStop = 0x8002D3D0`.

The bounded helper was run with the companion symbol files over
`0x8002D3D0..0x8002D570`. It changed zero references and reported
`already-synchronized`.

Independent generated-tree inspection found no placeholder or generated body
at the companion address. The only generated artifacts are the existing
`osMotorStop_recomp` ABI declaration and a zero-size overlay record at
`0x0002CF90`; four generated call sites reference that wrapper. The companion
map independently defines `osMotorStop` at `0x8002D3D0` and places
`osMotorStart` at `0x8002D570`. There is therefore no body or exact generated
span to rename; preserve the ABI name as an unmaterialized libultra entry. No
build or soak is needed.
