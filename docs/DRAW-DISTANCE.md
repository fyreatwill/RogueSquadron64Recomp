# Extended draw distance (G1c) - owner guide

Opt-in only. Default is retail behaviour (`ROGUESQ_DRAW_DISTANCE` unset = 1.0).

```sh
cd build && env ROGUESQ_DRAW_DISTANCE=2 ./RogueSquadron64Recomp
```

| Env | Effect |
|---|---|
| `ROGUESQ_DRAW_DISTANCE=<m>` | Scales the terrain-window radius (and, for m>1, the projection far plane automatically). Clamped to >=0.25. |
| `ROGUESQ_DD_FAR=<m>` / `ROGUESQ_DD_NEAR=<m>` | Override the far / near plane scale independently of the radius. |
| `ROGUESQ_UCODE_CAP=<n>` | Synthetic LLE ucode iteration guard (hardware has none). Default 65536 at every setting since s6762: 16384 dropped the HUD and engine glows in dense dd1 frames (lvl9) that retail draws. =16384 restores the old cap. |
| `ROGUESQ_BYPASS_MAXCELLS=<n>` | Span-reject bypass cells per frame. dd>1 default -1 (unlimited) since s6788: the old 120 cap made terrain flicker between full and less-than-retail (the owner's terrain dropouts). The dd>1 bundle also sets `ROGUESQ_UCODE_CAP=1048576`. |
| `ROGUESQ_DD_POOLX=<k>` | Terrain stream-pool capacity multiplier (1..2.5 fit the guest heap; 3+ exhausts it). |

## What is measured (see CURRENT-TRUTH s6070-s6076 for evidence)
- The limit lives in three places: terrain-window radius, the far clip plane, and the ucode iteration cap. All three have to move.
- Level 1, dd2 + auto-far: triangles x2.3 (643 -> 1465), terrain pixel fraction 0.030 -> 0.074.
- 300 s holds at dd2 on levels 1, 5, 10: 0 crashes, 0 VI stalls; dd3 on level 1 also clean. VI stays 60/s; RSP host cost about +10 ms per second of play.
- Cost on the fixed build (s6697, ROGUESQ_G1B, 180 s holds; s6390-s6695 cost figures are void): lvl1 dd1 29.7 game fps / 10.9 ms per gfx task -> dd4 24.1 fps / 24.0 ms; lvl5 dd1 30.0 / 14.7 ms -> dd4 19.6 / 33.9 ms. dd4 costs real frame rate (lvl1 dd1 figure is from the s6696 run, not same-run).

## Phase 2 result (s6699-s6703, -O2 build)
- Owner sheets: `docs/img/g1c_phase2_dd_sheet_vi3000.png` and `..._vi4500.png` (rows lvl1, lvl5; columns dd1, dd4, dd8). Each
  column is a different run, so the camera differs per cell: these show that each setting renders sanely, not a fixed-camera A/B.
- dd4 is the useful ceiling on lvl1/lvl5: above it the clamped terrain window already covers the whole level table (lvl5 64x64,
  3904-3968 cells at dd4/dd6/dd8, triangles flat), so dd6/dd8 add no terrain.
- dd8 needed two fixes, both on by default: the far-plane cap at 65534-near (s6701; without it guPerspective perspNorm drops to 1
  and the scene shrinks into a centre box; `ROGUESQ_DD_PNORM_CAP=0` = old) and a free list for the 4 MB spill arena at 0x80800000
  (s6702; it used to leak every block and lvl1 dd8 crashed at ~219 s; `ROGUESQ_SPILL_LEAK=1` = old).
- Cost on -O2 with STORE_DIAG=0: lvl5 dd4 ~30 game fps (retail rate), dd6/dd8 the same. FPS60 at dd4 reaches ~45, not 60.
- Suggested owner setting: `ROGUESQ_DRAW_DISTANCE=2` until the dd3/dd4 sheets are fixed (s6895: dd2 had none in any test, dd3 and dd4 did). Default stays retail until the owner chooses.

## Map edge (s6874)

Any multiplier other than 1 used to cut the plain that retail draws past the map edge, leaving the edge against the sky. `ROGUESQ_DD_EDGE` (default on) keeps it; `=0` restores the old clamp. Retail (no multiplier) is unaffected.

## Not established
- How it looks (pop-in, haze) - needs the owner's eyes.
- Per-step frame time against the G1b baseline (only single-source tri/RSP-time figures).
- Level 10 terrain-fraction scoring (space/sky saturates the heuristic).

## Far terrain and camera heading (s6901)

Above dd1 the terrain window is at most 64x64 cells. Before s6901 it stayed anchored at its low end and the area cap trimmed z before x reached 64, so on some headings forward reach fell from 63 cells to 37 and about half the terrain vanished, and passing a diagonal cut it for ~0.2 s. The window is now placed from the camera heading and moves smoothly as you turn. `ROGUESQ_DD_FWDWIN=0` restores the old placement, `=tog` alternates each second, `ROGUESQ_DD_FWDWIN_K=<cells>` sets the forward bias (default 26). dd1 is untouched. The square window is a limit that remains: what it can hold still differs a little between axis and diagonal views.

