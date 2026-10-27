# Owner opt-in settings (one page)

Everything here is OFF by default; unset = retail behaviour. Run from `build/` with the ROM beside it:

```sh
cd build && env ROGUESQ_FPS60=1 ROGUESQ_DRAW_DISTANCE=2 ./RogueSquadron64Recomp
```

| Goal | Setting | Verified state | Detail |
|---|---|---|---|
| 60 game frames/s (retail ~30) | `ROGUESQ_FPS60=1` | 300 s holds on levels 1, 5, 10: 0 crash, 0 VI stall; hangar soak clean. Craft path per real second unchanged (sim is delta-time); mission clocks time-based; audio tick is per-VI. Not checked: direct NPC position control, other levels. **Owner to judge feel.** | s6255-s6261 |
| More terrain drawn | `ROGUESQ_DRAW_DISTANCE=2` (2 qualified on levels 1/5/10; 3 qualified on levels 1/5/10 (s6446: holds 302 s/301 s, 'multiplier 3' echoed, alive_at_end=1, 0 VI stalls, 0 crash lines); >3 needs `ROGUESQ_DD_UNSAFE=1`) | Levels 1, 5, 10 clean for 300 s; triangles x2.3 on level 1. Look (pop-in, haze) unjudged. | `docs/DRAW-DISTANCE.md` |
| Widescreen | `ROGUESQ_ASPECT=16:9` or `21:9`, plus `ROGUESQ_OSMEM_MB=12`, `ROGUESQ_FP_XSCALE`, `ROGUESQ_HUD_ANCHOR` | Level-1 flight frames correct at 796 and 1024 wide, mission held ~182 s. KNOWN DEFECT: wide title screen shows a corrupt block / tiled background (defect B, unresolved, cosmetic, title only). | CURRENT-TRUTH "G1d widescreen" |
| Remove spike lines in flight | `ROGUESQ_CULL_SPIKE=1` | Culls the ucode clip-plane wedge triangles (s6085). | CURRENT-TRUTH "G3b" |
| Frame-time instrument | `ROGUESQ_G1B=1` | Per-VI timing log. | s6017 |

Combos: FPS60 + DRAW_DISTANCE=2 held 300 s clean on levels 1 and 5 (s6262, alive_at_end=1, 0 stalls, 0 crash lines). Widescreen + FPS60 (16:9 and 21:9, lvl1, s6264; needs TITLE_ORIGIN='0x[0-9A-F]*' MISSION_RE='[0-9A-F]+'): flight reached at width=796/1024, ~205 s hold (not the full 300 s), alive_at_end=1, 0 VI stalls, 0 crash lines.

Rules of thumb: combine settings freely only after checking the table. Kill the game with SIGKILL.
