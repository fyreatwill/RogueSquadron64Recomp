# Session 3284 — first menuOverlayInit enters runMenuModelViewerScreen then returns

HYPOTHESIS-ID: m5-osvimode-first-menu-model-viewer

## Competing hypotheses

- `H-RetailViewerThenReturn`: `0x800C28F0` fires during 2.0–6.9 s
  (first `$a1=9` activation); `0x8003E094` still at ~6.9 s. Retail
  enters and leaves the model viewer; the port is stuck inside a
  screen retail also uses.
- `H-RetailNoViewer`: `0x800C28F0` silent before `0x8003E094`.
  The port's model-viewer entry is a mis-dispatch, not retail's
  first-menu path.
- `H-RetailViewerAfterCine`: `0x800C28F0` fires only after the
  17 s `0x8003E13C` (second menu). The port entered it too early.
- `H-ViewerCoverageInvalid`: whole-RDRAM control or title 1024
  gate missing, or the 6.9 s `0x8003E094` watch silent (failed
  instrument).

## What ran

One independent retail Rice oracle, 25 s, eleven-Start. Watches are
physical. Exec watches armed at first VI (no `--pc-phase-log-width`).
Exact recipe in `scratch/agent/NEXT.md` (pre-run).

```
tools/oracle/build/rs64_oracle
  --watch-write 0x0:0x800000
  --watch-pc 0x800C28F0,0x8003E094,0x800A5D80,0x8003E13C
  --secs 25 --hit-cap 10000 --vi-trace --vi-poll
  --video rice
```

No audio behavior change. No M5 Step 3. No `PatchesLib` build.

Capture: `scratch/agent/s3284_first_menu_model_viewer.log`.

## Same-run positive controls

- Whole-RDRAM watch reached 10000 (`watch write [0x00000000,0x00800000):
  10000 hit(s)`).
- `[gpr-ctl]` fired (first breakpoint, a write at `0x8002b608`).
- Exec watch at `0x8003E094` fired once at 6.7 s (the first-return
  watch is enough to prove coverage). Lifetime `execution watch hits: 4`
  (one per watched PC).
- Title `1024 @ 0x00790400` at 17.3 s (VI transition was
  `640 -> 1024` origin `0x00790800`, then the pair `0x00790400`).
- 1463 VI, 25.1 s wall / 24.4 s emulated. `rc=0`.

## VI

| t | event |
|---|---|
| 0.6 s | 0 → 320 |
| 2.3 s | 320 → 640 @ `0x0066a500` |
| 17.3 s | 640 → 1024 @ `0x00790800` / `0x00790400` |

## Exec hits

| t | pc | `prev_pc` | live VI | `$a0` | `$a1` | `$a2` | `$v0` |
|---|---|---|---|---|---:|---|---|
| 2.5 s | `0x800C28F0` entry | `0x800C5C98` (`menuOverlayInit` jal; in `0x800C58A0..0x800C5D9C`) | 640 @ `0x0066aa00` | 0 | 0 | 0 | `0x800c5c98` |
| 6.7 s | `0x8003E094` continuation | `0x800C5D94` (`menuOverlayInit` `jr ra`) | 640 @ `0x0066a500` | `0x80037560` | `0x800cff60` | `0x50` | `0x80130000` |
| 6.7 s | `0x800A5D80` entry | `0x8003E10C` (`mainGameLoop` jal) | 640 @ `0x0066a500` | `0x13` | 2 | 0 | `0x80030000` |
| 17.0 s | `0x8003E13C` jal | `0x8003E138` (fall-through) | 640 @ `0x0062c200` | `0x80130b40` | 2 | `0x2ec0` | 0 |

`exec-prev` lifetime n=1 each. Overlay-alias test: the single
`0x800C28F0` hit has `prev_pc=0x800C5C98`, inside `menuOverlayInit`
(size `0x4FC`). That is the same jal the port logged in s3278
(`menuOverlayInit->runMenuModelViewerScreen caller=0x800C5C98`).

## Classification

- `H-ViewerCoverageInvalid` refuted: 10000-write control, title 1024,
  `[gpr-ctl]`, and the 6.7 s `0x8003E094` watch all fired.
- `H-RetailNoViewer` refuted: `0x800C28F0` executed once at 2.5 s,
  before the 6.7 s first return.
- `H-RetailViewerAfterCine` refuted: the viewer hit is 2.5 s, not
  after the 17.0 s `0x8003E13C`.
- `H-RetailViewerThenReturn` selected: retail enters the model
  viewer during the first `$a1=9` activation and leaves it before
  cinematic. The port is stuck inside a screen retail also uses.

Combined with s3278 (single-source port): one `[m5-postwait]` entry
at `runMenuModelViewerScreen` at `640 @ 0x66A500`, zero return, and
zero `[slot-ret-caller] site=runMenuModelViewerScreen` over 60 s.
The generated body only calls `anyAudioSlotActive` on the post-loop
tail (`L_800C2DB0`); the port therefore never left the frame loop
(`$s5` / `$f24` fade). That is context for the next unit, not a
selected hypothesis here.

No audio or M5 Step 3 change.
