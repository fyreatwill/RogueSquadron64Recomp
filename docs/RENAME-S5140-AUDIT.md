# Session 5140 rename audit

Candidate: `osMapTLBRdb = 0x8002D370`.

The bounded helper was run with the companion symbol files over
`0x8002D370..0x8002D3D0`. It changed zero references and reported
`already-synchronized`.

Independent generated-tree inspection found no placeholder, ABI declaration,
generated body, overlay record, or direct generated caller for this address.
The companion map independently defines `osMapTLBRdb` and places the next
entry, `osMotorStop`, at `0x8002D3D0`. There is therefore no generated artifact
to rename; preserve the companion ABI name as an unmaterialized libultra entry.
No build or soak is needed.
