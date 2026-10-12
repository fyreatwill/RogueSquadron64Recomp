# M5 session 4691 — A11 wait/slot boundary

The rebuilt real-audio/LLE/ungated/solo/spin-yield port and the independent
Rice retail oracle ran together for the same 120-second phase window. Both
positive controls fired: the port produced 2,416 title and 187 hangar VI rows;
retail's whole-RDRAM watch produced 6,643,096 writes and reached title 1024
and hangar 512 at `0x006AB400`.

In the port's title/hangar phase-gated A11 census, `waitForAnyAudioSlot` had
three hangar entries and three corresponding `wait-post-any-slot` returns.
The returned active masks were `0x11`; no `waitforslot-guard-fire` row was
emitted. The wait path therefore completed through its normal terminal branch,
not through the 500,000-iteration escape. The same run also showed the named
service/tick path executing while the slot table was being read.

Retail independently wrote the complete physical status-table range
`0x154620:0x1658A0` 6,633,096 times. The exact service writer execution watches
recorded six executions each for `0x8009B7CC` (publish `03`) and `0x8009B7EC`
(clear `00`); the `0x8009B7A8` control had zero executions. These writer hits
occurred in the qualified 512 route, and the whole-RDRAM control was positive.

This selects H-A11-slot-writer-valid for the covered title/hangar route:
normal wait returns and the independent retail terminal writer are present,
with no cap escape. It does not authorize removing the cap or changing the
wait. Artifact logs and the self-contained recipe are in
`scratch/agent/s4691_m5_a11_wait_boundary/` and
`scratch/agent/run_s4691_m5_a11_wait_boundary.sh`.
