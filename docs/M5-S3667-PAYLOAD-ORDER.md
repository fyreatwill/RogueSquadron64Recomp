# M5 Session 3667 — source payload precedes selector/task publication

Two identical 55-second retail-oracle captures were run; the fixed capture
added `--first-watch 1 --detail-watch 1` so the source-span writes were
timestamped. The whole-RDRAM control, four descriptor watches, both title
origins, both hangar origins, and the type-2 task dump all fired. The fixed
run recorded 343,741 whole-RDRAM writes, 674 writes to physical
`0x1797B0..0x179930`, and 1,809 valid type-2 task rows with zero invalid
pointers or overflow.

The first source-span writes occurred at 6.8 seconds from `0x8001E2C0`; the
bulk began at 7.0 seconds from `0x80007670`. Title VI began at 17.4 seconds,
and hangar VI began at 38.4 seconds. The source-span writer histogram was
`0x800078EC` 384, `0x80007670` 172, and twelve smaller writer sites totaling
118. The selector/task execution watches remained active through title and
hangar, with `0x80091060` and `0x80091074` each firing 2,259 times.

This selects `H-PayloadBeforeSelector` for the watched image source span and
refutes `H-DmaAfterSelector` for that span: no source-span writes occurred in
the phase-gated title or hangar buckets, while the payload was already being
written before either target phase. The multiple source writers mean
`H-SeparatePayloadWriter` remains open; this capture does not join each writer
to an individual selector object or expose a DMA event.

ORIGIN: diagnostic-only physical write and execution watches; no selector,
task, audio, descriptor, or output state was rewritten, skipped, or guarded.

Evidence: `scratch/agent/s3667_m5_payload_order_fixed/oracle.log` and the
same-run control capture in `scratch/agent/s3667_m5_payload_order/oracle.log`.
