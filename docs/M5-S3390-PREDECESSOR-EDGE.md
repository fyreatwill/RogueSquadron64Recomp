# M5 Session 3390 — producer predecessor census

The retail oracle ran the canonical driven Start schedule under Rice for 120
seconds with whole-RDRAM and target-span write controls, phase buckets, and
execution watches at `0x800078E0`, `0x8002BEE8`, `0x800078E8`, and
`0x8002BEEC`. The whole-RDRAM control recorded 11,830 writes and the target
span recorded 1,830 writes. Retail reached hangar `0x006AB400` at width 512;
the predecessor watches fired there. The target writer's hangar phase bucket
recorded 664 samples, including 189 nonzero post-store samples.

The rebuilt port reached title `0x00790400` at 11.9 seconds and hangar
`0x006AB400` at 20.0 seconds. Phase, audio/task, static-call, and PCM
controls were live. Its target span again exposed only the zero-fill
`0x8008F2CC -> rs_memset` edge (`dst=0x801797B0`, `val=0`, `len=0x298`),
with no matching producer or callback-writer row. PCM source and consumer
rows remained `FNV=0xF59C39C5`, `nz=0`. After leaving hangar at 39.9 seconds,
the run hit the existing unaligned-ROM DMA assertion in `recomp::do_rom_read`;
that was after the discriminating window.

This selects `H-EarlierRetailProducer`: retail has valid predecessor activity
and nonzero target writes in the like-for-like hangar phase, while the port
has no corresponding producer edge at the observed boundary. It refutes
`H-PortPredecessorMatch` and `H-LegitimateZeroBoundary` at this scope. The
result does not identify the missing earlier input or prove that the port's
zero fill is illegitimate. No output or audio behavior changed.

Evidence: `scratch/agent/oracle_s3390/predecessor.log` and
`scratch/agent/port_s3390/run.log`.
