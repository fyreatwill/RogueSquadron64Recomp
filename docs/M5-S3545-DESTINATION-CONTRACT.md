# M5 session 3545 — texture-record destination contract

The paired phase-gated run selected `H-PortWrongDestination`.

The independent retail oracle passed its whole-RDRAM positive control (10,000
callbacks), reached title 1024 and hangar 512, and executed the family PCs in
both target phases. In hangar, retail used record bases around `0x8016F768`
with `s2=0x1A2`, `s3=s4=0x2004`, and `s1=0x3AC8`.

The same-build real-audio port passed its phase controls and reached title 1024
and hangar 512. Its witness logged 2,048 rows in each target phase. In hangar,
the corresponding rows used record bases `0x8016D440`/`0x8016D464`,
`s2=0xA8`/`0xA9`, `s3=s4=0x4004`, and `s1=0x17A0`/`0x17C4`. At
`0x8001FAF8`, the port destinations were `0x8016D44A`/`0x8016D46E`, while
retail's corresponding `v1+0xA` relation was distinct.

The writer PCs and values are legitimate texture-record writes, but the port
selects a different record destination/context. This is an origin diagnosis,
not a mitigation. The next boundary is the producer of the port's record
base/index selection; no writes or source/output state should be changed.
