# Session 3283 — first menuOverlayInit returns at 6.9 s; cinematic occupies the gap

HYPOTHESIS-ID: m5-osvimode-menu-return-vs-cinematic

## Competing hypotheses

- `H-FirstReturnsThenCinematic`: continuation `0x8003E094` fires at
  ~2 s; `cinematicLoopBody` jal `0x8003E10C` / entry `0x800A5D80`
  occupies the gap; `0x8003E13C` at ~17 s.
- `H-FirstStaysResident`: `0x8003E094` fires only at ~17 s, immediately
  before `0x8003E13C`. First `menuOverlayInit` is the long inner loop.
- `H-GapIsOtherMainWork`: `0x8003E094` at ~2 s, zero classifiable
  cinematic exec, `0x8003E13C` still at ~17 s.
- `H-ReturnCoverageInvalid`: whole-RDRAM control or title 1024 gate
  missing, or the 17 s `0x8003E13C` watch silent (failed instrument).

## What ran

One independent retail Rice oracle, 25 s, eleven-Start. Watches are
physical. Exec watches armed at first VI (no `--pc-phase-log-width`).
Exact recipe in `scratch/agent/NEXT.md` (pre-run).

```
tools/oracle/build/rs64_oracle
  --watch-write 0x0:0x800000
  --watch-pc 0x8003E094,0x8003E10C,0x800A5D80,0x8003E13C
  --secs 25 --hit-cap 10000 --vi-trace --vi-poll
  --video rice
```

No audio behavior change. No M5 Step 3. No `PatchesLib` build.

Capture: `scratch/agent/s3283_menu_return_vs_cinematic.log`.

## Same-run positive controls

- Whole-RDRAM watch reached 10000 (`watch write [0x00000000,0x00800000):
  10000 hit(s)`).
- `[gpr-ctl]` fired (first breakpoint, a write at `0x8002b608`).
- Exec watch at `0x8003E13C` fired once at 17.0 s (the 17 s second jal
  is enough to prove the watch). Lifetime `execution watch hits: 4`
  (one per watched PC).
- Title `1024 @ 0x00790400` at 17.3 s, then `0x00790800`.
- 1448 VI, 25.1 s wall / 24.1 s emulated. `rc=0`.

## VI

| t | event |
|---|---|
| 0.9 s | 0 → 320 |
| 1.9 s | 320 @ `0x006ba280` |
| 2.6 s | 320 → 640 @ `0x0066a500` |
| 6.6 s | 640 @ `0x0066aa00` |
| 7.6–16.8 s | 640; origins cycle (`0x00696600` / `0x00696100` / `0x0062c200` / `0x0062bd00`) |
| 17.3 s | 640 → 1024 @ `0x00790400` |

## Exec hits

| t | pc | `prev_pc` | live VI | `$a0` | `$a1` | `$a2` | `$v0` |
|---|---|---|---|---|---:|---|---|
| 6.9 s | `0x8003E094` continuation | `0x800C5D94` (`menuOverlayInit` `jr ra`; size `0x4FC`) | 640 @ `0x0066a500` | `0x80037560` | `0x800cff60` | `0x50` | `0x80130000` |
| 6.9 s | `0x8003E10C` jal | `0x8003E108` (fall-through) | 640 @ `0x0066a500` | `0x13` | 2 | `0x15b0` | `0x80030000` |
| 6.9 s | `0x800A5D80` entry | `0x8003E10C` (`mainGameLoop` jal, not overlay-alias) | 640 @ `0x0066a500` | `0x13` | 2 | 0 | `0x80030000` |
| 17.0 s | `0x8003E13C` jal | `0x8003E138` (fall-through) | 640 @ `0x0062c200` | `0x80130b40` | 2 | `0x2ec0` | 0 |

`exec-prev` lifetime n=1 each. Combined with Session 3282's 2.0 s
`0x8003E08C` entry (`$a1=9`, VI 320): first `menuOverlayInit` is
resident 2.0–6.9 s (spans the 320→640 rewrite), then returns, then
`cinematicLoopBody` is a single blocking call until 17.0 s.

## Classification

- `H-ReturnCoverageInvalid` refuted: 10000-write control, title 1024,
  `[gpr-ctl]`, and the 17.0 s `0x8003E13C` watch all fired.
- `H-FirstStaysResident` refuted: `0x8003E094` fires at 6.9 s, not at
  17 s.
- `H-GapIsOtherMainWork` refuted: `0x800A5D80` executed once with
  `prev_pc=0x8003E10C` (the `mainGameLoop` jal).
- `H-FirstReturnsThenCinematic` selected, with a timing refinement:
  the first return is 6.9 s, not ~2 s. The ~2 s figure was the
  Session 3282 entry time. Cinematic occupies 6.9–17.0 s.

`docs/game-architecture.md` sketched menu `$a1=9`, then menu
`(s3, 2, 0xB)`, then cinematic. Boot attract is menu `$a1=9`, then
cinematic, then menu `$a1=2` at `0x8003E13C`. The unused `0x8003E0CC`
site remains unused.

Combined with s3278: the port's 320-phase `menu-jal` is the first
activation and it never reaches `0x8003E13C`. Retail must leave that
activation at 6.9 s and finish cinematic before the 1024 rewrite.
The port log from that census had `menu-entry`/`menu-spin`/`menu-jal`
n=1, zero `menu-exit`, zero `[cp]`, and one `[m5-postwait]` entry at
`runMenuModelViewerScreen` (`0x800C28F0`) at `640 @ 0x66A500` with
no return row. That is single-source port context for the next unit,
not a selected hypothesis here.
