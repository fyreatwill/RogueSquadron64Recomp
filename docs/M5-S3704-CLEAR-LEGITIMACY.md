# M5 s3704 — clear object and ordering

The paired real-audio and silent arms both reached the qualified 512 hangar VI
and fired their phase/task/DMEM controls. The caller-side probe found the
target clear at `0x8008F2CC`, not the previously suspected `0x800052C4` site.

Both arms reported the target contract `dst=0x801797B0`, `len=0x298`, and
`value=0`. The real arm joined it at `ordinal=523`, `row=523`,
`arm=factor5_ucode_b`; the silent arm independently reported the same range
and zero fingerprint under `arm=musyx_stub`. The real arm's later
`0x1798B0..0x179930` source-DMA payload remained zero.

This selects `H-ClearLegitimateButEarly`: the clear object and length are the
expected image-source range, and the clear precedes the producer/output
handoff. It refutes `H-ClearWrongObject` and `H-ProducerAfterClear` for the
measured boundary. The paired arms are independent route evidence; the prior
retail writer census is the independent ground-truth line.

The caller probe was added through `tools/apply_s2448_m5_static_callers.py` and
the existing exit join was restored with `tools/apply_s2447_m5_static_calls.py`.
No guest or RDRAM behavior was changed.
