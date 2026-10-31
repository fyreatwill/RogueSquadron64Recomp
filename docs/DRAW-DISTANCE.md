# Extended draw distance (G1c) - owner guide

Opt-in only. Default is retail behaviour (`ROGUESQ_DRAW_DISTANCE` unset = 1.0).

```sh
cd build && env ROGUESQ_DRAW_DISTANCE=2 ./RogueSquadron64Recomp
```

| Env | Effect |
|---|---|
| `ROGUESQ_DRAW_DISTANCE=<m>` | Scales the terrain-window radius (and, for m>1, the projection far plane automatically). Clamped to >=0.25. |
| `ROGUESQ_DD_FAR=<m>` / `ROGUESQ_DD_NEAR=<m>` | Override the far / near plane scale independently of the radius. |
| `ROGUESQ_UCODE_CAP=<n>` | LLE ucode iteration cap (default 16384 = retail). Retail cap truncates frames once more terrain is submitted; raised automatically by the dd path's recipes. |
| `ROGUESQ_DD_POOLX=<k>` | Terrain stream-pool capacity multiplier (1..2.5 fit the guest heap; 3+ exhausts it). |

## What is measured (see CURRENT-TRUTH s6070-s6076 for evidence)
- The limit lives in three places: terrain-window radius, the far clip plane, and the ucode iteration cap. All three have to move.
- Level 1, dd2 + auto-far: triangles x2.3 (643 -> 1465), terrain pixel fraction 0.030 -> 0.074.
- 300 s holds at dd2 on levels 1, 5, 10: 0 crashes, 0 VI stalls; dd3 on level 1 also clean. VI stays 60/s; RSP host cost about +10 ms per second of play.
- Cost on the fixed build (s6697, ROGUESQ_G1B, 180 s holds; s6390-s6695 cost figures are void): lvl1 dd1 29.7 game fps / 10.9 ms per gfx task -> dd4 24.1 fps / 24.0 ms; lvl5 dd1 30.0 / 14.7 ms -> dd4 19.6 / 33.9 ms. dd4 costs real frame rate (lvl1 dd1 figure is from the s6696 run, not same-run).

## Not established
- How it looks (pop-in, haze) - needs the owner's eyes.
- Per-step frame time against the G1b baseline (only single-source tri/RSP-time figures).
- Level 10 terrain-fraction scoring (space/sky saturates the heuristic).
