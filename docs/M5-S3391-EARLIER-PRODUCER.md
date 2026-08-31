# M5 Session 3391 — earlier producer/call-contract census

The independent retail oracle ran the canonical Rice route for 120 seconds
with whole-RDRAM control, target-span watch, and execution/field watches at
`0x8002BEE8`, `0x800078E0`, and `0x800078E8`. The whole-RDRAM control fired
223,338 times over 7,169 VI frames. Retail reached the 512 phase at
`0x006AB400`; the predecessor execution watch fired 37,635 times, and the
`rs_memset` body and delay-slot watch also fired.

The target-span watch produced no visible hit rows in this capture, so the
oracle arm is partial for payload attribution. Its execution and field rows
are valid positive-controlled evidence of the retail predecessor path, but do
not establish a target-span payload for this run.

The rebuilt port reached title `0x00790400` at 11.8 seconds and hangar
`0x006AB400` at 19.9 seconds. Phase, static-call, and PCM controls fired;
there were no crash or abort markers. The only target-overlap static-call row
was:

```
phase=5 width=512 origin=0x6AB400 entry=0x800078E0
caller_ra=0x8008F2CC dst=0x801797B0 val=0 len=0x298
```

No callback-writer row or matching earlier producer row appeared, and the
PCM source and consumer summaries were both `FNV=0xF59C39C5`, `nz=0`.

This selects `H-EarlierPortContract` at the observed boundary: retail exposes
the earlier `0x8002BEE8` execution family while the qualified port exposes
only the zero-fill `0x8008F2CC` path. It does not establish that the zero fill
is illegitimate, and because the retail target-byte watch was partial it does
not claim a like-for-like nonzero payload comparison. No output or audio
behavior changed.
