# Session 3280 — 1024-edge initVideoSubsystem caller is advanceVideoFrame

HYPOTHESIS-ID: m5-osvimode-1024-rewrite-caller

## Competing hypotheses

- `H-RewriteCallerPreTitle`: 1024-edge `initVideoSubsystem` `prev_pc` is a
  caller the port already reaches during VI 640. Missing that later call
  is a cause of `H-MissingTableRewrite`.
- `H-RewriteCallerTitleEntry`: that `prev_pc` is a title-entry / post-640-only
  caller. The missing 1024 copy is a symptom of never leaving VI 640.
- `H-RewriteNotANewEntry`: `0x8001A098` does not execute at the ~17.3 s copy;
  `0x8001B6B0` runs inside a long-lived activation.
- `H-CallerCoverageInvalid`: whole-RDRAM control or title 1024 gate missing,
  or the entry watch never fires.

## What ran

One independent retail Rice oracle, 25 s, eleven-Start. Watches are
physical. Exact recipe in `scratch/agent/NEXT.md` (pre-run).

```
tools/oracle/build/rs64_oracle
  --watch-write 0x0:0x800000
  --watch-pc 0x8001A098
  --watch-write 0x128D58:0x128D5C
  --detail-watch 1 --pc-hist-watch 1
  --pc-hist-phase 0x0066A500:640 --pc-hist-phase 0x00790400:1024
  --secs 25 --hit-cap 10000 --vi-trace --vi-poll
```

`--watch-pc` occupied watch index 1, so `--detail-watch 1` / `--pc-hist-watch 1`
histogrammed the exec watch, not the slot. Slot writes still counted
(4 hits). Exec hits print past `--hit-cap` (EXEC_LOG_CAP 64). That does
not affect the entry/`prev_pc` discriminator.

No audio behavior change. No M5 Step 3. No `PatchesLib` build.

Capture: `scratch/agent/s3280_initvideo_caller.log`.

## Same-run positive controls

- Whole-RDRAM watch reached 10000 and was removed (`rc=0`).
- `[gpr-ctl]` fired (first breakpoint, a write at `0x8002b608`).
- Exec watch at `0x8001A098` fired 3 times (lifetime `execution watch hits: 3`).
- Title `1024 @ 0x00790800` at 17.3 s, then `0x00790400`; phase bucket
  `1024 @ 0x00790400` had 233 VI. Hangar not reached (title window).
- 1463 VI, 25.1 s wall / 24.4 s emulated.

## VI

| t | event |
|---|---|
| 0.7 s | 0 → 320 |
| 2.3 s | 320 → 640 @ `0x0066A500` |
| 6.8–17.2 s | still 640; origins cycle (`0x0066A500`, `0x005d4500`, `0x00696100`, `0x0062bd00`, …) |
| 17.3 s | 640 → 1024 @ `0x00790800` |

## Exec hits at `initVideoSubsystem` `0x8001A098`

All three `prev_pc=0x80018378` (`advanceVideoFrame` jal). `exec-prev n=3`
matches the lifetime count. Sole generated jal sites into `0x8001A098` are
`advanceVideoFrame` `0x80018378` and `initVideoBootWrapper` `0x80018564`;
the boot wrapper did not appear.

| t | live VI | `$a0` | `$a1`/`$s1` | `$a2` | `$s0` |
|---|---|---:|---:|---:|---:|
| 2.2 s | 320 @ `0x006dd280` | `0x280` (640) | `0x1e0` (480) | 0 | `0x10` |
| 6.8 s | 640 @ `0x0066A500` | `0x280` (640) | `0x154` (340) | `0x10` | `0x10` |
| 17.2 s | 640 @ `0x0062bd00` | `0x200` (512) | `0x1c0` (448) | `0x10` | `0x10` |

The 17.2 s row is 0.1 s before the 1024 VI callback. Stored slot +8 width
is the stack OSViMode template (`lw $a0, 8($a2)` at `0x8001B6B0`), not
the entry `$a0`. Session 3279 already measured that store as 1024 while
title 1024 was live.

Slot watch counted 4 writes vs 3 entries: the missing entry is the 0.8 s
boot 320 copy (same gap as Session 3279's unsampled first copy). That
does not affect the 17.2 s discriminator.

## Port already-reached path (Session 3278)

`advanceVideoFrame` is the port's `initVideoSubsystem` caller for the
320→640 rewrite (s3278 call 3, `[vi-gate]` n=1 width 640). Port
`[avf-gate] site=tick-jal` ran once; `[vi-gate] initVideoSubsystem`
stopped at n=1. No third `initVideoSubsystem` `osViSetMode`.

`advanceVideoFrame` has one generated caller: `runVideoFrameTick`
(`0x80001354`) jal `0x800014F0`. `runVideoFrameTick` callers:

| jal | function |
|---|---|
| `0x800C5A18` | `menuOverlayInit` |
| `0x8003E29C` | `mainGameLoop` (site a) |
| `0x8003E360` | `mainGameLoop` (site b) |
| `0x800A9C70` | `initSceneForMission` |

s3278's one tick-jal was `site=menu-jal`. This session does not name
which of those four parents is live at 17.2 s.

## Classification

- `H-CallerCoverageInvalid` refuted: 10000-write control, title 1024,
  exec watch fired.
- `H-RewriteNotANewEntry` refuted: a new `0x8001A098` entry at 17.2 s,
  0.1 s before 1024 VI.
- `H-RewriteCallerTitleEntry` refuted: `prev_pc` is `advanceVideoFrame`
  `0x80018378`, already on the port's VI-640 path, not a title-only
  overlay function.
- `H-RewriteCallerPreTitle` selected: the 1024-edge jal is the same
  site the port already uses for 640. The port is missing later
  invocations (retail 6.8 s still-640 at the port's stop origin
  `0x0066A500` with `$a0=640`, then 17.2 s with `$a0=0x200`).

The 17.2 s invocation itself is at origin `0x0062bd00`, which the port
has not reached. The 6.8 s same-caller call at `0x0066A500` still
publishes 640, so extra ticks at the stop origin would not by themselves
write 1024. Next discriminator: which `runVideoFrameTick` parent is
`prev_pc` at the 17.2 s edge.
