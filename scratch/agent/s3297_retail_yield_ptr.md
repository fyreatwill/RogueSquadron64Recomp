# Session 3297 — retail 19E04 yield pointer stays 0; no 0x80128D40 writer

HYPOTHESIS-ID: m5-osvimode-viewer-frame-exit

## Competing hypotheses

- `H-RetailYieldPtrZero`: during 2.5–6.7 s, `0x80019E04`
  `$v0` is 0 (beq to 19E7C). Physical `0x00128D40` stays 0
  or is written only as 0. 19E70 remains silent because the
  nonzero-yield successor is dead.
- `H-RetailYieldPtrLive`: `0x80019E04` `$v0` is nonzero at
  least once in the viewer, so retail has a yield pointer
  but still does not execute 19E70 (different successor
  than the port).
- `H-RetailYieldPtrUnpublished`: `0x80019E04` runs with
  `$v0==0` and no write to `0x00128D40` in the viewer; the
  port's `0x80149470` publisher is extra.
- `H-RetailCoverageInvalid`: whole-RDRAM 10000-write
  control, title `1024 @ 0x00790400`, viewer `0x800C28F0`,
  or `0x800C2E00` miss, or no 19E04 exec in 2.5–6.7 s.

## What ran

One independent retail Rice oracle, 25 s. Watches are
physical. Exec watches armed at first VI (no
`--pc-phase-log-width`). `--hit-cap 20000`. Extra logging
only: `--detail-watch 1`, `--first-watch 1`,
`--pc-hist-watch 1`, `--post-value-watch 1` on the
4-byte yield-pointer word, plus exec `0x80019E0C` (the
19E04 fallthrough / `osSpTaskYielded` poll). No `--press`.

```
tools/oracle/build/rs64_oracle
  --core .../libmupen64plus.dylib
  --rom  .../rogue_squadron.z64
  --video .../mupen64plus-video-rice.dylib
  --watch-write 0x0:0x800000
  --watch-write 0x00128D40:0x00128D44
  --watch-pc 0x80019E04,0x80019E70,0x800C28F0,0x800C2E00,0x80019E0C
  --secs 25 --hit-cap 20000 --vi-trace --vi-poll
```

Capture: `scratch/agent/s3297_retail_yield_ptr.log`.

No skip, allow, restore, wait bypass, or M5 Step 3.

`0x80019E04` is `beq $v0, $zero, L_80019E7C` after
`lw $v0, -0x72C0($v0)` from `0x80128D40`. The exec watch
fires with `$v0` already loaded. Fallthrough is
`L_80019E0C` (`osSpTaskYielded` of `gspTask`).

## Same-run positive controls

- whole-RDRAM write watch: 10000 hits; `[oracle] positive-control
  threshold reached`; watch index 1 remained armed.
- `[gpr-ctl]` at 0.5 s (first VI 320).
- viewer entry `0x800C28F0` at 2.3 s (`prev_pc=0x800C5C98`,
  640 @ `0x0066aa00`).
- viewer return `0x800C2E00` at 6.5 s (`prev_pc=0x800C2DFC`,
  640 @ `0x0066aa00`, `$v0=1`).
- 19E04 live in the viewer window: 500 printed execs,
  2.3–6.5 s, width 640. Lifetime 2075, all printed
  (`--hit-cap 20000` not truncated: 12077 total hits).
- 1470 VI, 25.0 s wall / 24.5 s emulated. `rc=0`.

Title `1024 @ 0x00790400` did not fire: `[vi]` stays
`640` through 24.4 s (origins `0x00696100` / `0x00696600` /
`0x0062c200` / `0x0062bd00`). Same Rice/25 s miss as
s3296. The 1024 rewrite is after the viewer return, so it
is not the viewer-window gate. Failed instrument for the
*viewer* discriminator would have been a silent
`0x800C2E00` or silent 19E04 in 2.3–6.5 s. Both fired.

## Lifetime watches

| watch | hits |
|---|---:|
| write `[0x0,0x800000)` | 10000 (removed at 10000) |
| write `[0x00128D40,0x00128D44)` | **0** |
| exec `0x80019E04` | 2075, all `prev=0x80019E00`, all `$v0=0` |
| exec `0x80019E70` | **0** |
| exec `0x80019E0C` | **0** |
| viewer entry `0x800C28F0` | 1 |
| viewer return `0x800C2E00` | 1 |

`--post-value-watch 1` samples=0 unique=0. Shutdown
snapshot: 4 bytes, nonzero=0, FNV `0x4b95f515` (FNV-1a of
four zero bytes). Writer-PC histogram for watch 1 is
empty.

## Viewer window (2.3–6.5 s)

| site | n | notes |
|---|---:|---|
| 19E04 | 500 | `$v0=0` n=500; origins `0x0066aa00` n=250 / `0x005d4500` n=242 / `0x0066a500` n=8 |
| 19E0C | 0 | fallthrough never taken |
| 19E70 | 0 | never executes |
| `0x00128D40` writes | 0 | 4-byte aligned word watch |

Lifetime 19E04 is also `$v0=0` n=2075 from 0.6 s
(width 320) through 25.0 s. Zero printed 19E04 rows have
`$v0 != 0`.

## Classification

- `H-RetailCoverageInvalid` is not selected for the viewer
  discriminator: rdram 10000, `[gpr-ctl]`, `0x800C28F0`,
  `0x800C2E00`, and 19E04 in-window all fired. Title 1024
  is a post-viewer route-progress miss on this run.
- `H-RetailYieldPtrLive` is refuted: 0 printed `$v0 != 0`;
  19E0C exec=0 so the beq always takes.
- `H-RetailYieldPtrZero` is selected: every 19E04 `$v0`
  is 0, 19E70 stays silent, 19E0C stays silent.
- `H-RetailYieldPtrUnpublished` is also selected: zero
  writes to the aligned word while the watch was armed,
  plus a zero snapshot at shutdown. The loaded value at
  19E04 is independently 0, so a missed unaligned store
  would still have shown up in `$v0`.

The scheduler's only nonzero store to this word is
`0x80019DC0` (`sw` of the incoming task pointer after
`osSpTaskYield`, type-2 dispatch at `L_80019D90`). Combined
with s3295, the port's `19DFC yieldw=0x80149470` is extra
relative to this retail attract viewer.

Single-source oracle evidence, compared with the s3295
port census (two-source for "port has a live yield
pointer / retail does not"). No audio or M5 Step 3 change.

Next discriminator: during the same viewer, does retail
enter type-2 dispatch `L_80019D90` and/or the idle
successor `L_80019DCC`, or is the publisher `0x80019DC0`
silent because type-2 never arrives?
