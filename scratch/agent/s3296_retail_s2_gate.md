# Session 3296 — retail 19E80 always takes; 19E70 never stores

HYPOTHESIS-ID: m5-osvimode-viewer-frame-exit

## Competing hypotheses

- `H-RetailS2Cleared`: during 2.5–6.7 s, `0x80019E80` `$v0`
  is 0 or 2 (takes 19ED0). Physical `0x0011A89F` is written
  to 1 at `0x80019E70` and later cleared (expected clearer
  `0x80019F6C`) before the next 19E80.
- `H-RetailNoYieldStore`: viewer-window `0x80019E70` never
  stores; `0x0011A89F` stays 0/2 so 19E80 keeps taking. The
  port's yieldw=`0x80149470` path is extra.
- `H-RetailS2Stays1`: retail 19E80 `$v0` is also 1 during
  the viewer (fallthrough), so a different site must produce
  the 242 `0x8011A818` sends (would reopen s3292).
- `H-RetailCoverageInvalid`: whole-RDRAM 10000-write
  control, title `1024 @ 0x00790400`, viewer `0x800C28F0`,
  or `0x800C2E00` miss, or no 19E80 exec in 2.5–6.7 s.

## What ran

One independent retail Rice oracle, 25 s. Watches are
physical. Exec watches armed at first VI (no
`--pc-phase-log-width`). `--hit-cap 20000`. Extra logging
only: `--detail-watch` on the 89F/exec indices,
`--pc-hist-watch 1`, `--first-watch 1`, `--post-value-watch 1`
on the 1-byte range, and exec `0x80019F6C` (the hypothesized
clearer). No `--press`.

```
tools/oracle/build/rs64_oracle
  --core .../libmupen64plus.dylib
  --rom  .../rogue_squadron.z64
  --video .../mupen64plus-video-rice.dylib
  --watch-write 0x0:0x800000
  --watch-write 0x0011A89F:0x0011A8A0
  --watch-pc 0x80019E80,0x80019E70,0x80019ED0,0x800C28F0,0x800C2E00,0x80019F6C
  --secs 25 --hit-cap 20000 --vi-trace --vi-poll
```

Capture: `scratch/agent/s3296_retail_s2_gate.log`.

No skip, allow, restore, wait bypass, or M5 Step 3.

`0x80019E80` is `bne $v0, $s1, L_80019ED0` after
`lbu $v0, 0($s2)` at `0x80019E7C`. `$s2` is `0x8011A89F`.
The exec watch fires with `$v0` already loaded.

## Same-run positive controls

- whole-RDRAM write watch: 10000 hits; `[oracle] positive-control
  threshold reached`; `[gpr-ctl]` at 0.4 s.
- viewer entry `0x800C28F0` at 2.2 s (`prev_pc=0x800C5C98`,
  640 @ `0x0066aa00`).
- viewer return `0x800C2E00` at 6.4 s (`prev_pc=0x800C2DFC`,
  640 @ `0x0066aa00`, `$v0=1`).
- 19E80 live in the viewer window: 500 printed execs,
  2.2–6.4 s, width 640.
- 1473 VI, 25.0 s wall / 24.6 s emulated. `rc=0`.

Title `1024 @ 0x00790400` did not fire: `[vi]` stays
`640` through 24.3 s (origins `0x00696100` / `0x0062c200` /
`0x0062bd00` / `0x00696600`). s3292 on the same Rice/25 s
recipe hit `640 -> 1024` at 17.3 s. The 1024 rewrite is
after the viewer return, so it is not the viewer-window
gate. Failed instrument for the *viewer* discriminator
would have been a silent `0x800C2E00` or silent 19E80 in
2.2–6.4 s. Both fired.

Hit-cap printed through t=17.8 s (`n=20000`), covering the
viewer and ~11 s of cinematic 640. Lifetime exec-prev is
not capped.

## Lifetime watches

| watch | hits |
|---|---:|
| write `[0x0,0x800000)` | 18332 (removed at 10000) |
| write `[0x0011A89F,0x0011A8A0)` | **0** |
| exec `0x80019E80` | 2079, all `prev=0x80019E7C` |
| exec `0x80019E70` | **0** |
| exec `0x80019ED0` | 2079, all `prev=0x80019E80` |
| exec `0x80019F6C` | 2892 (`prev=0x80033554` n=1446, `prev=0x80019F6C` n=1446) |
| viewer entry `0x800C28F0` | 1 |
| viewer return `0x800C2E00` | 1 |

19ED0 count equals 19E80 count and every 19ED0 has
`prev_pc=0x80019E80`, so every 19E80 takes. Zero printed
19E80 rows have `$v0==1` (printed 1494 through 17.8 s:
`$v0=2` n=1016, `$v0=0` n=478; `$s1=1` on every row).

## Viewer window (2.2–6.4 s)

| site | n | notes |
|---|---:|---|
| 19E80 | 500 | `$v0=2` n=258, `$v0=0` n=242, `$v0=1` n=0; `$s1=1` |
| 19ED0 | 500 | all `prev=0x80019E80`; same `$v0` split |
| 19E70 | 0 | never executes |
| 19F6C | 258 | all `prev=0x80033554` |
| 89F byte writes | 0 | 1-byte watch |

The 242 `$v0=0` takes match s3292's 242 viewer
`0x8011A818` sends from `0x80019F1C`. The 258 `$v0=2`
takes match 258 `19F6C` visits (enter 19ED0, skip the
send, run the word-store clearer).

## 89F vs aligned 89C

The 1-byte watch never fired. Mupen reports word stores at
the aligned address `0x0011A89C`, so an `sw` to `$s4` does
not match `[0x0011A89F,0x0011A8A0)`. Printed 89C writes
(whole-RDRAM watch, still under hit-cap) in the viewer
include `0x80019FE4` n=500, `0x80019DD0`/`0x80019DD4`/
`0x80019F6C` n=258, `0x80019D34` n=242. Those leave the
LSB 0 or 2; they are not a store of 1.

`0x80019E70` is `sb` to 89F. A live store would have both
executed the PC and hit the 1-byte watch. Both are zero
for the whole 25 s, not only the viewer.

`--post-value-watch 1` samples=0 (no 89F callback). That
is consistent, not a missing instrument: the 19E70 exec
watch is the same-run positive that the sb site is armed
and silent.

## Classification

- `H-RetailCoverageInvalid` is not selected for the viewer
  discriminator: rdram 10000, `[gpr-ctl]`, `0x800C28F0`,
  `0x800C2E00`, and 19E80 in-window all fired. Title 1024
  is a post-viewer route-progress miss on this run.
- `H-RetailS2Stays1` is refuted: 0 printed `$v0==1`;
  lifetime 19ED0=19E80 with `prev=0x80019E80`.
- `H-RetailS2Cleared` is refuted: `0x80019E70` never
  executes, so it never stores 1. 19F6C is live but is a
  word store at 89C that does not produce `$v0==1`.
- Selected `H-RetailNoYieldStore`: retail 19E80 keeps
  taking because `$v0` stays 0 or 2; the port's
  yield-complete `sb` at `0x80019E70` (s3295, after
  19DFC `yieldw=0x80149470`) is extra relative to this
  retail attract viewer.

Single-source oracle evidence, compared with the s3295
port census (two-source for "port stores 1 / retail does
not"). No audio or M5 Step 3 change.

Next discriminator: during the same viewer, does retail
`0x80019E04` (`beq $v0, $zero, L_80019E7C` after
`lw $v0, -0x72C0($v0)` from `0x80128D40`) ever see
`$v0 != 0`?
