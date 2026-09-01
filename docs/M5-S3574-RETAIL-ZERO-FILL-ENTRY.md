# M5 s3574 — retail zero-fill entry qualification

The required retail oracle runs passed the whole-RDRAM positive control and
the target source-span watch. The driven run recorded 10,674 whole-RDRAM
writes, 674 writes in physical `0x1797B0..0x179930`, and 3,165 executions of
`0x800078E0` in the explicit `0x006AB400:512` phase bucket. The port run also
passed its phase and route controls, reaching title `1024 @ 0x00790400` and
hangar `512 @ 0x006AB400`.

The port's regeneration-safe entry table recorded the target call as:

```
dst=0x801797B0 fill=0x00 len=0x298
```

The retail entry watch was positive in the target bucket, but the oracle's
bounded execution output did not retain a caller-filtered target row for
`0x8008F2CC`. Its target-bucket rows therefore cannot establish that the
retail call with the port's tuple is the same invocation, nor can they order
that call against the first source DMA. This does not select
`H-ZeroFillParity`, `H-ZeroFillPortInput`, or `H-ZeroFillPortOrdering`.

The next discriminator must watch both the retail caller instruction
`0x8008F2CC` and entry `0x800078E0` in the same `0x006AB400:512` bucket, retain
the source-span watch, and join caller-to-entry chronology and arguments in a
single run.

ORIGIN: diagnostic-only entry and oracle watch qualification. No game state,
output, PCM, task, DMA, or source contents were changed.

Evidence:

- Port log: `scratch/agent/s3574_zero_fill_contract_entry/run.log`
- Retail preflight: `scratch/agent/s3574_zero_fill_contract_oracle/oracle.log`
- Retail phase run: `scratch/agent/s3574_zero_fill_contract_oracle_phase/oracle.log`
