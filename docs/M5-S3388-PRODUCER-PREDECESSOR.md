# M5 Session 3388 — producer-family predecessor census

The retail oracle ran the canonical driven Start schedule under Rice for 120
seconds with a whole-RDRAM positive-control watch, both target-span watches,
phase writer histograms, post-value sampling, and execution watches at
`0x80007670` and `0x800078EC`. The positive control recorded 11,830 writes;
title VI `0x00790400` and hangar VI `0x006AB400` were both reached. The target
span watches recorded 705 and 1,125 writes. Their lifetime writer histograms
included 116 and 184 writes from `0x80007670`, and 512 and 816 from
`0x800078EC`; the execution histogram also identified `0x8002BEEC` as a
predecessor of `0x800078EC` in 387 rows. Both watched PCs fired, so the oracle
arm was valid.

The rebuilt port used the established LLE-only, spin-yield, real-audio route
and the phase, audio-task, callback-writer, static-call, PCM, and phase-gated
probe controls. It reached title at 11.7 seconds and hangar at 19.8 seconds.
At the target span it exposed only the zero-fill
`0x8008F2CC -> rs_memset` row (`dst=0x801797B0`, `val=0`, `len=0x298`), with no
matching `0x80007670` or `0x800078EC` producer row. Hangar PCM source and
consumer samples remained `F59C39C5`, `nz=0`.

This selects `H-RetailFamilyInput` / `H-RetailDrivenProducer` at the observed
boundary and refutes a matching port producer edge there. It does not prove
the port zero-fill is illegitimate, identify the missing producer's input, or
make nonzero transform behavior evaluable. The next useful boundary is the
retail predecessor/call chain around `0x8002BEEC` and `0x800078E8`;
no output or audio behavior was changed.
