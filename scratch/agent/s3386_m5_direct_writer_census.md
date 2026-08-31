# Session 3386 — M5 direct-writer edge census

## Ground truth

The retail oracle ran for 120 seconds with a whole-RDRAM positive-control
watch plus execution watches for `0x8002BEEC` and `0x800078EC`, and title and
hangar phase buckets. The positive control reached 10,000 callbacks and was
removed automatically. Retail executed `0x800078EC` 9,667 times; the
undriven route executed `0x8002BEEC` zero times. The oracle instrument was
therefore live, but this route did not supply a driven `0x8002BEEC` row.

## Port census

The rebuilt port ran through `tools/probe.sh`, gated at title VI 1024, with
the existing LLE/audio/task/callback/PCM controls and static `rs_memset`
caller/entry census. It reached title `1024 @ 0x00790400` and hangar
`512 @ 0x006AB400`, with no `[CRASH]` or `[ABORT]` marker. The phase,
real-audio task, and PCM controls all fired.

In the hangar target phase, the only target-overlap entry row was:

```
entry=0x800078E0 caller_ra=0x8008F2CC dst=0x801797B0 val=0 len=0x298
```

There were no target-phase rows with a `0x8002BEEC` caller edge and no
callback-writer rows. Paired PCM source/consumer rows continued to report the
same zero payload (`768` bytes, `FNV=0xF59C39C5`, `nz=0`).

## Decision

The port still takes the observed target span through the zero-fill path and
does not exhibit the retail `0x8002BEEC -> 0x800078EC` edge. Together with
the independent retail execution watch and live same-run controls, this
selects `H-EarlierProducerGap` for the driven port route and refutes a
port-side dispatch alias at the observed boundary. The zero-fill's
legitimacy and the missing earlier producer/dispatch edge remain unresolved;
no output or audio behavior changed.
