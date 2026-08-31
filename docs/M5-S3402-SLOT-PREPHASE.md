# M5 Session 3402 — Retail Slot 0x149764 Pre-Phase Initialization

Oracle run: 120s, `--watch-write 0x0:0x800000 --watch-write 0x149764:0x149768
--watch-write 0x1935E0:0x1935F0 --pc-hist-phase 0x00790400:1024
--pc-hist-phase 0x006AB400:512 --post-value-watch 1 --post-value-pc 0x800078EC`.
Log: `scratch/agent/s3402_retail_field348_owner/oracle.log`.

## Controls

| Control                   | Result      |
|---------------------------|-------------|
| Whole-RDRAM positive      | 10,046 hits |
| Title 1024 phase gate     | 633 VI      |
| Hangar 512 phase gate     | 1,316 VI    |
| `0x1935E0` watch          | 40 hits     |

## Slot 0x149764 (field348 owner-slot)

- Total writes: 6 from `pc=0x8008F2C8`, value=`0x801797B0` (fnv=`0x380f190b`, nonzero=4)
- Phase-qualified writes during title-1024: **0**
- Phase-qualified writes during hangar-512: **0**
- `0x800078EC` writes to slot range: 0 (expected — writes to buffer slot points to)

All 6 writes occurred before the first phase gate opened (pre-boot init sequence).
The slot is pre-initialized to `0x801797B0` and not re-touched during audio phases.

## Comparison with s3401 (port witness)

s3401 armed a durable port witness on `0x8008F2C8` and reported:
- Port stores `0x80178C80` to slot `0x80149764` during title-1024 phase
- Port stores `0x801797B0` to slot `0x80149764` during hangar-512 phase

Retail (s3402): stores only `0x801797B0`, exclusively pre-phase.

## Hypothesis discrimination (two independent lines)

| Hypothesis                       | Verdict for title-1024       | Verdict for hangar-512       |
|----------------------------------|------------------------------|------------------------------|
| H-PortStage3OwnerAbsent          | REFUTED (retail writes slot) | REFUTED (retail writes slot) |
| H-PortStage3Field348ProducerGap  | SELECTED (wrong value in port: 0x80178C80 vs 0x801797B0) | REFUTED (both store 0x801797B0) |
| H-PortStage3DownstreamGap        | N/A (value differs)          | SELECTED (same value, port PCM zero) |

## Implication

For the hangar-512 audio scope (the active route): `field348` is correctly set in
the port. The PCM production gap is downstream of the slot — specifically in the
dispatch of `0x8002BEEC` (the instruction that JALs to `0x800078EC`). That PC
fires 37,635 times in retail but 0 times in the port. The caller chain for
`0x8002BEEC` is the next probe target.
