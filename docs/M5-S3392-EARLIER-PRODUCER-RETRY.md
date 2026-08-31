# M5 Session 3392 — earlier producer target attribution retry

The independent retail oracle ran first with whole-RDRAM and target-span
watches plus execution watches for `0x8002BEE8`, `0x800078E8`, and
`0x800078EC`. The whole-RDRAM control was live; the raw trace contained
20,716 `0x8002BEE8` rows and 2,652 `0x800078E8` rows. The target-span watch
produced no recognizable target-address rows, so retail payload attribution
was partial in this run.

The first port attempt crashed before the 1024 phase in the existing
`filterVoiceSampleBlock` path (`last-guest-pc=0x8000834C`). A same-build retry
reached title `0x00790400` at 11.9 seconds and hangar `0x006AB400` at 20.2
seconds, with no crash or abort markers. Its target-phase row remained:

```
phase=5 width=512 origin=0x6AB400 entry=0x800078E0
caller_ra=0x8008F2CC dst=0x801797B0 val=0 len=0x298
```

The retry emitted PCM source and consumer controls in the hangar phase, all
with `FNV=0xF59C39C5`, `nz=0`; no callback-writer or earlier-producer row
appeared. This reinforces `H-EarlierPortContract` at the observed port
boundary and refutes a matching port predecessor edge for this run. It does
not provide a like-for-like retail payload comparison and does not establish
that the port zero fill is illegitimate. No output or audio behavior changed.
