# M5 Session 3443 — frequency output value join

The independent retail oracle was run first with a whole-RDRAM positive
control, both title origins, the hangar origin, and execution watches at
`0x80001C0C` and `0x80001CC8`. The control fired, both PCs were live, and the
`0x80001CC8` field dump fired in the 512 phase. The relevant retail rows used
`s1=0x80194B20`; their output `v1` values were `{1,4,5,6,9,10,0x1A}` in
origin `0x006AB400` and `{3,4,5,6,7,8,9,10,0x1A}` in origin `0x006AB800`.

The fresh-build port pair used the existing regeneration-safe post-consumer
witness. Silent and Factor 5 image both reached title 1024 and hangar 512,
passed the consumer/output positive controls, and had 512 consumer rows and
343 output rows, with no crash or abort markers. Their output rows matched
each other. At `0x80001CC8`, the port output was `0x2` for the sampled rows;
the associated port state keys were in the `0x801BBD..` range rather than
retail's `0x80194B20`.

This selects `H-PortOutputUseGap` at the observed first-output boundary:
the port consumer is live, but its joined state/output shape does not match
the retail target-state rows. It refutes `H-OutputValueJoinUnevaluable` for
the value-level portion and does not establish that message zero is corrupt.
The state-pointer/caller divergence before this output use remains open.
No waits, slots, dispatch, clear behavior, or PCM writeback changed.
