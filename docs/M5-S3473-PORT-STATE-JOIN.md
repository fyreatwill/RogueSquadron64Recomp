# M5 Session 3473 — joined port table selection and output state

The prescribed image-arm port capture reached title origin `0x00790400` at
width 1024 and later reached the 512-wide hangar phase. The existing positive
controls fired: `[m5-output-state-fields-positive]` and
`[m5-state-pointer-checkpoint-positive]`. There was no crash or abort marker.

The title-gated witnesses were live and complete at their expected scopes:
2,048 table-selection rows (1,024 each at `0x800644DC` and `0x80064524`),
1,024 producer-input rows, and output/state rows at the four target PCs in
counts 514/510/510/514 for `0x80001C98`/`0x80001CB8`/`0x80001CC8`/
`0x80001F84`.

The in-run producer rows loaded `s0=0x801B4F00` 183 times and
`s0=0x801B5E70` 4 times, alongside zero and non-state values. The table
selection rows also selected the `0x801B4F00`/`0x801B5E70` family. These are
the qualified retail producer values from Session 3468, so the port producer
family is not absent at this boundary. However, the downstream output/state
witness reported state pointers in the `0x80110xxx` family (for example
`0x80111028`, `0x80110E58`, and `0x80110ECC`), rather than the qualified retail
tuple's `0x801B1590` pointer.

This selects `H-PortPointerSelection`: the port reaches the qualified table
value family but selects a different downstream state pointer before the
consumer contract. It rules out `H-PortObservationInvalid` because both
positive controls and all target buckets fired. It does not yet identify the
writer or transformation producing the `0x80110xxx` pointer. The retail
value-family comparison is the independent second evidence line; the port
capture is the new line. No runtime behavior or mitigation changed.
