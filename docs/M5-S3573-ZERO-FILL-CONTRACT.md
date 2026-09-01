# M5 s3573 — zero-fill call/input contract

The required oracle preflight used the debug core and retail ROM, passed the
whole-RDRAM positive control with 11,058 writes, reached the 512-wide hangar
origin `0x006AB400`, and observed 1,058 writes in the watched source span.
The retail execution watch at `0x800078EC` was also live, with 7,159,689
execution hits.

The target-valid port run reached title `1024 @ 0x00790400` and hangar
`512 @ 0x006AB400`. Its regeneration-safe `rs_memset` entry witness fired in
the hangar with the target tuple:

```
dst=0x801797B0 fill=0x00 len=0x298
```

The existing source-range writer rows immediately following the target entry
were zero-payload DMA writebacks into `0x1797B0..0x179930`. The source-DMA
control was live. No crash or route failure occurred before deliberate
SIGKILL.

This establishes that the port enters its target zero-fill with the expected
source-span destination, zero fill, and `0x298` length. It does not establish
retail tuple parity: the retail watch was at the loop body `0x800078EC`, not
the `rs_memset` entry `0x800078E0`, and therefore its sampled `$a0/$a2` values
describe other loop invocations. Ordering parity is likewise unresolved
because the retail run did not provide an entry-to-first-source-DMA join.

The result is single-source for the port tuple and independent-source for
retail writer execution/source-span activity. It refutes neither
`H-ZeroFillParity`, `H-ZeroFillPortInput`, nor `H-ZeroFillPortOrdering`. The
next discriminator must watch retail entry `0x800078E0` while retaining the
whole-RDRAM and source-span controls, then compare entry tuples and their
ordering against the already-captured port source-DMA ordinal.

ORIGIN: diagnostic-only entry witness. No game state, output, PCM, task, DMA,
or source contents were changed.

Evidence:

- Port log: `scratch/agent/s3573_zero_fill_contract_run/run.log`
- Retail oracle log: `scratch/agent/m5_s3573_oracle/oracle.log`
