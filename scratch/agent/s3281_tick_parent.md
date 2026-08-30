# Session 3281 — 1024-edge runVideoFrameTick parent is menuOverlayInit

HYPOTHESIS-ID: m5-osvimode-1024-tick-parent

## Competing hypotheses

- `H-TickParentMenu`: 17.2 s `runVideoFrameTick` `prev_pc` is
  `menuOverlayInit` `0x800C5A18`. The port already reaches this jal
  (s3278 `site=menu-jal` n=1) and is missing later ticks.
- `H-TickParentMainGameLoop`: `prev_pc` is `mainGameLoop` `0x8003E29C`
  or `0x8003E360`.
- `H-TickParentMission`: `prev_pc` is `initSceneForMission` `0x800A9C70`.
- `H-TickCoverageInvalid`: whole-RDRAM control or title 1024 gate
  missing, or the entry watch never fires.

## What ran

One independent retail Rice oracle, 25 s, eleven-Start. Watches are
physical. Exact recipe in `scratch/agent/NEXT.md` (pre-run).

```
tools/oracle/build/rs64_oracle
  --watch-write 0x0:0x800000
  --watch-write 0x128D58:0x128D5C
  --watch-pc 0x80001354
  --detail-watch 1 --pc-hist-watch 1
  --pc-phase-log-width 0x0066A500:640
  --pc-phase-log-width 0x0062BD00:640
  --pc-phase-log-width 0x00790400:1024
  --pc-phase-log-width 0x00790800:1024
  --secs 25 --hit-cap 10000 --vi-trace --vi-poll
```

`--pc-phase-log-width` sets `g_defer_exec_watches`, so the exec watch
armed at `[phase-arm] width=640 origin=0x0066a500` (2.3 s), not at
first VI. 320-phase ticks are therefore unevaluable. The 17 s
discriminator is after that arm. Lifetime `execution watch hits: 2`
matches the two printed execs; the function is not per-frame.

No audio behavior change. No M5 Step 3. No `PatchesLib` build.

Capture: `scratch/agent/s3281_tick_parent.log`.

## Same-run positive controls

- Whole-RDRAM watch reached 10000 and was removed (`rc=0`).
- `[gpr-ctl]` fired (first breakpoint, a write at `0x8002b608`).
- Exec watch at `0x80001354` fired twice after the 2.3 s phase-arm
  (lifetime `execution watch hits: 2`). A 640-phase tick is enough.
- Title `1024 @ 0x00790800` at 17.3 s, then `0x00790400`; phase bucket
  `1024 @ 0x00790400` had 233 VI.
- 1460 VI, 25.1 s wall / 24.3 s emulated.

## VI

| t | event |
|---|---|
| 0.7 s | 0 → 320 |
| 2.3 s | 320 → 640 @ `0x0066A500`; exec watch armed |
| 6.7–17.2 s | still 640; origins cycle (`0x0066A500`, `0x00696100`, `0x0062bd00`, …) |
| 17.3 s | 640 → 1024 @ `0x00790800` |

## Exec hits at `runVideoFrameTick` `0x80001354`

| t | live VI | `prev_pc` | parent | `$v0` | `$s1` / `$s0` |
|---|---|---|---|---:|---|
| 6.7 s | 640 @ `0x0066A500` | `0x800A9C70` | `initSceneForMission` | `0x00040000` | `0x80037560` / `0x13` |
| 17.0 s | 640 @ `0x00696100` | `0x800C5A18` | `menuOverlayInit` | `0x00028000` | `0x800d0000` / `0x80037560` |

`exec-prev` lifetime: `prev=0x800a9c70 n=1`, `prev=0x800c5a18 n=1`.
Zero `mainGameLoop` `0x8003E29C` / `0x8003E360`.

Slot +8 writes at `0x8001B6B0`: 0.8 s, 2.3 s, 7.0 s (0.3 s after the
mission tick), 17.2 s (0.2 s after the menu tick; 0.1 s before 1024 VI).
Join: the 17.0 s menu jal is the 1024-edge tick.

## Port already-reached path (Session 3278)

Port `site=menu-jal` n=1 ran while still VI 320 (`[slot-ret-caller]
site=menuOverlayInit` at origin `0x006BA280`), then `tick-jal` n=1
produced the 320→640 rewrite. `tickn=1` then `tick-exit`. No
`mission-jal`. No second tick. Phase stopped at `640 @ 0x0066A500`.

Retail's 1024-edge parent is that same jal site, but 14 s later, at
origin `0x00696100`, after a mission tick the port never ran.

## Classification

- `H-TickCoverageInvalid` refuted: 10000-write control, title 1024,
  exec watch fired after phase-arm.
- `H-TickParentMainGameLoop` refuted: neither `mainGameLoop` jal
  appears in printed hits or `exec-prev`.
- `H-TickParentMission` refuted for the 1024-edge: `0x800A9C70` is
  the 6.7 s tick at the port's stop origin, 10 s before 1024 VI.
- `H-TickParentMenu` selected: 17.0 s `prev_pc=0x800C5A18`
  (`menuOverlayInit` jal at entry+`0x178`). Single-source oracle plus
  s3278's port `menu-jal` n=1: the port is missing a later invocation
  of that jal, not a different parent.

`--pc-phase-log-width` deferred the exec watch, so a 320-phase tick
(the port's one `menu-jal`) is unevaluable here. That does not split
the 17 s parent.

Next discriminator: retail `menuOverlayInit` entry `0x800C58A0` vs
jal `0x800C5A18` timing in one run, with the exec watch armed at first
VI (no `--pc-phase-log-width`, or include 320 origins so defer arms
during 320). Early entry + late jal selects a wait-before-tick.
First entry at ~17 s selects late overlay entry. Do not change audio
behavior.
