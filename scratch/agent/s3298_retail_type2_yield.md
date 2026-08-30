# Session 3298 — retail type-2 always idle-starts; 19DC0 silent

HYPOTHESIS-ID: m5-osvimode-viewer-frame-exit

## Competing hypotheses

- `H-RetailNoType2`: during 2.5–6.7 s, `0x80019D90` is
  silent. Retail never dispatches type 2, so the yield
  publisher is dead because its caller is dead.
- `H-RetailType2Idle`: `0x80019D90` is live and
  `0x80019DCC` is live; `0x80019DAC` / `0x80019DC0` stay
  0. Type-2 arrives while SP is idle (`0x8011A89C==0`), so
  no yield.
- `H-RetailType2Yields`: `0x80019DC0` executes (would
  contradict s3297's zero writes unless the store watch
  missed).
- `H-RetailCoverageInvalid`: whole-RDRAM 10000-write
  control, viewer `0x800C28F0`, or `0x800C2E00` miss, or
  no scheduler exec in 2.5–6.7 s.

## What ran

One independent retail Rice oracle, 25 s. Watches are
physical. Exec watches armed at first VI (no
`--pc-phase-log-width`). `--hit-cap 20000`. Extra logging
only: `--detail-watch 1`, `--first-watch 1`,
`--pc-hist-watch 1`, `--post-value-watch 1` on the
4-byte yield-pointer word. No `--press`.

```
tools/oracle/build/rs64_oracle
  --core .../libmupen64plus.dylib
  --rom  .../rogue_squadron.z64
  --video .../mupen64plus-video-rice.dylib
  --watch-write 0x0:0x800000
  --watch-write 0x00128D40:0x00128D44
  --watch-pc 0x80019D90,0x80019DAC,0x80019DC0,0x80019DCC,0x800C28F0,0x800C2E00
  --secs 25 --hit-cap 20000 --vi-trace --vi-poll
```

Capture: `scratch/agent/s3298_retail_type2_yield.log`.

No skip, allow, restore, wait bypass, or M5 Step 3.

`L_80019D90` is the type-2 handler (`lbu $v0, 0($s3)` with
`$s3=0x8011A8A0`), reached from `beq $v1, $s5` at
`0x80019CE0` (`$s5=2`). If `0x8011A8A0==0`, set it, then
`lbu $v0, -4($s3)` (`0x8011A89C`). Zero → `L_80019DCC`
(idle `osSpTaskLoad`/`StartGo`, and `sb $s5, 0x8011A89F`).
Nonzero → `jal osSpTaskYield` at `0x80019DAC` and `sw`
msg+4 into `0x80128D40` at `0x80019DC0`.

The exec watch at 19D90 fires on the `lbu`; `$v0` is still
the `0x80019CE0` delay-slot `slti` result (`type 2 < 3` →
1), not the loaded busy byte. 19DCC `$v0` is the already-
loaded `0x8011A89C`.

## Same-run positive controls

- whole-RDRAM write watch: 10000 hits; `[oracle] positive-control
  threshold reached`; watch index 1 remained armed.
- `[gpr-ctl]` at 0.5 s (first VI 320).
- viewer entry `0x800C28F0` at 2.2 s (`prev_pc=0x800C5C98`,
  640 @ `0x0066aa00`).
- viewer return `0x800C2E00` at 6.4 s (`prev_pc=0x800C2DFC`,
  640 @ `0x0066aa00`, `$v0=1`).
- 19D90 and 19DCC live in the viewer window: 259 printed
  each, 2.2–6.4 s, width 640. Lifetime 1447 each, all
  printed (`--hit-cap 20000` not truncated: 12896 total
  hits).
- 1474 VI, 25.0 s wall / 24.6 s emulated. `rc=0`.

Title `1024 @ 0x00790400` did not fire: `[vi]` stays
`640` through 24.4 s (origins `0x00696100` / `0x00696600` /
`0x0062c200` / `0x0062bd00`). Same Rice/25 s miss as
s3296/s3297. The 1024 rewrite is after the viewer return,
so it is not the viewer-window gate. Failed instrument for
the *viewer* discriminator would have been a silent
`0x800C2E00` or silent 19D90/19DCC in 2.2–6.4 s. Both
fired.

## Lifetime watches

| watch | hits |
|---|---:|
| write `[0x0,0x800000)` | 10000 (removed at 10000) |
| write `[0x00128D40,0x00128D44)` | **0** |
| exec `0x80019D90` | 1447, all `prev=0x80019CE0` |
| exec `0x80019DAC` | **0** |
| exec `0x80019DC0` | **0** |
| exec `0x80019DCC` | 1447, all `prev=0x80019DA4` |
| viewer entry `0x800C28F0` | 1 |
| viewer return `0x800C2E00` | 1 |

`--post-value-watch 1` samples=0 unique=0. Shutdown
snapshot: 4 bytes, nonzero=0, FNV `0x4b95f515` (FNV-1a of
four zero bytes). Writer-PC histogram for watch 1 is
empty. First type-2 is t=0.6 s, width 320,
`$a0=0x80128C80`.

## Viewer window (2.2–6.4 s)

| site | n | notes |
|---|---:|---|
| 19D90 | 259 | all `prev=0x80019CE0`; `$v0=1` (slti delay slot); `$a0=0x80128C80`; origins `0x0066aa00` n=129 / `0x005d4500` n=121 / `0x0066a500` n=9 |
| 19DAC | 0 | `osSpTaskYield` never entered |
| 19DC0 | 0 | yield-pointer store never entered |
| 19DCC | 259 | all `prev=0x80019DA4`; `$v0=0` (`0x8011A89C` idle); same origins as 19D90 |
| `0x00128D40` writes | 0 | 4-byte aligned word watch |

19D90 and 19DCC are 1:1 for the whole 25 s (1447/1447).
Zero 19D90 visits take the 19D94 busy skip (`0x8011A8A0`
already set) or the 19DAC yield arm.

## Classification

- `H-RetailCoverageInvalid` is not selected for the viewer
  discriminator: rdram 10000, `[gpr-ctl]`, `0x800C28F0`,
  `0x800C2E00`, and in-window 19D90/19DCC all fired. Title
  1024 is a post-viewer route-progress miss on this run.
- `H-RetailNoType2` is refuted: 259 viewer 19D90 from
  `0x80019CE0`, `$a0=0x80128C80` (same type-2 message the
  port logs).
- `H-RetailType2Yields` is refuted: 19DAC exec=0, 19DC0
  exec=0, zero writes to `0x00128D40`, zero snapshot.
- `H-RetailType2Idle` is selected: every type-2 visit
  reaches `L_80019DCC` with `0x8011A89C==0`. Combined with
  s3297, the yield publisher is silent because SP is idle
  at type-2, not because type-2 is absent. Combined with
  s3296, idle start stores `$s5=2` into `0x8011A89F`, which
  is the `$v0=2` 19E80-taken population.

Single-source oracle evidence, compared with the s3295
port census (two-source for "port has a live yield
pointer / retail type-2 never publishes one"). No audio
or M5 Step 3 change.

Next discriminator: on the port, does type-2 take 19DCC
(idle, like retail) or 19DC0 (yield-publish of
`0x80149470`), especially in the gap after last 19ED0
where s3295 first saw `yieldw=0x80149470`?
