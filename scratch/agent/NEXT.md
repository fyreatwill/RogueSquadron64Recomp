# NEXT work unit — retail skip-allow source into 0x800A6274

HYPOTHESIS-ID: m5-osvimode-postviewer-continuation

Session 3312 selected `H-RetailFlagSet`: retail
`cinematicLoopBody` never takes time-pred `0x800A626C`
(`$v1=1` on 1189 printed rows). Skip-allow `$a0` stays 0
until 48.1 s, then `$a0=1` so `0x800A6274` falls through,
first `0x800A6288` `$v0=0`, `jal 0x800A62B4` fires. Port
Session 3311 keeps `$a0=0`. Ask retail which operand sets
that `$a0`.

## Resume context

Skip-allow `$a0` at 6274 is computed just above:

- `0x800A6208` `andi $v0, $v0, 0x9000` after
  `getControllerNewButtonsPressed` (Start `0x1000` / A
  `0x8000`). Result copied to `$a0` at `0x800A6220`.
- `0x800A6238` `bne $v0, $zero → 6250`: incoming `$a0!=0`
  forces skip-allow=1 and skips the byte load.
- `0x800A6244` `lbu $v0, 0xB1C($t1)` from `0x800B0B1C`
  (physical `0x000B0B1C`).
- `0x800A6248` `beq $v0, $zero → 6254`: byte 0 leaves
  skip-allow 0.
- Prologue `0x800A5EE8` `sb $zero, 0xB1C` zeros the byte
  at cinematic entry.

This run is undriven (no `--press`).

## Competing hypotheses

- `H-RetailIncomingA0`: 6238 is `taken=1` (`$a0!=0`) at
  48.1 s; no nonzero write of `0x000B0B1C` before the jal.
  Hardware skip-allow is the Start/A new-press path.
- `H-RetailB1CWrite`: 6238 stays `taken=0`; physical
  `0x000B0B1C` is written nonzero then 6248 is `taken=0`;
  6274 `$a0=1` follows. Name the writer PC.
- `H-RetailBoth`: incoming `$a0` and a 0xB1C write both
  fire in the 48.1 s window.
- `H-CoverageInvalid`: missing 10000-write, `[gpr-ctl]`,
  VI `640 @ 0x0066A500`, cinematic entry, or 62B4.

## Discriminator

One independent retail Rice 90 s run. Watch exec of 6238 /
6248 / 6274 / 62B4 / 5EE8 plus write `0x000B0B1C:0x000B0B1D`.
Detail those PCs so `$v0`/`$v1`/`$a0` print. Whole-RDRAM
write watch is the positive control.

62B4 n>=1 plus 6238 `taken=1` at the jal window with no
nonzero 0xB1C write selects `H-RetailIncomingA0`. A
nonzero 0xB1C store then 6248 `taken=0` with 6238
`taken=0` selects `H-RetailB1CWrite`. Both firing selects
`H-RetailBoth`. Missing whole-RDRAM / VI-640 / entry /
62B4 is coverage-invalid.

## Exact commands

Follow `scratch/agent/s3312_retail_cine_init_path/run.sh`:

```
tools/oracle/build/rs64_oracle
  --core .../libmupen64plus.dylib
  --rom  .../rogue_squadron.z64
  --video .../mupen64plus-video-rice.dylib
  --watch-write 0x0:0x800000
  --watch-write 0x000B0B1C:0x000B0B1D
  --watch-pc 0x800A5D80,0x800A5EE8,0x800A6238,0x800A6248,0x800A6274,0x800A62B4
  --detail-watch on 0xB1C, 5EE8, 6238, 6248, 6274, 62B4
  --secs 90 --hit-cap 20000 --vi-trace --vi-poll
```

No `--press`. No port build. No M5 Step 3. No audio/output
change. Require 10000-write, `[gpr-ctl]`, VI
`640 @ 0x0066A500`, cinematic entry `0x800A5D80`, and 62B4.
