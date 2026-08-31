# M5 Session 3389 — producer predecessor edge

The retail oracle ran the canonical driven Start schedule under Rice for 120
seconds with a whole-RDRAM positive-control watch, target-span watches, phase
buckets, and execution watches at `0x8002BEEC` and `0x800078E8`. The positive
control recorded 10,693 writes and title VI `0x00790400` was reached. Both
execution watches fired there: `0x8002BEEC` had 322,412 hits with predecessor
`0x8002BEE8`, and `0x800078E8` had 21,232 hits with predecessor `0x800078E0`.
The target spans recorded 502 and 500 writes. The explicit hangar 512 bucket
had zero rows, so this arm did not provide a like-for-like 512-phase retail
result.

The rebuilt port reached title at 11.6 seconds and hangar at 19.8 seconds.
Its controls were live: the phase gates fired, 85 PCM source rows were
observed, and there were no crash or abort markers. In the hangar target phase
the only target-span row was the zero-fill `0x8008F2CC -> rs_memset`, with
`dst=0x801797B0`, `val=0`, and `len=0x298`. No callback-writer row and no
matching `0x800078E8`/`0x8002BEEC` producer row appeared; PCM source and
consumer samples remained `FNV=0xF59C39C5`, `nz=0`.

This reinforces an earlier producer/call-contract gap at the observed
boundaries, but does not by itself select a like-for-like hangar producer
hypothesis because the retail predecessor rows were title-phase rows and the
retail 512 bucket was absent. It does not establish that the port zero fill is
illegitimate. Evidence: `scratch/agent/oracle_s3389_predecessor.log` and
`scratch/agent/port_s3389/run.log`.
