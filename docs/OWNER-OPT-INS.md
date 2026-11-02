# Owner opt-in settings (one page)

Everything here is OFF by default; unset = retail behaviour. Run from `build/` with the ROM beside it:

```sh
cd build && env ROGUESQ_FPS60=1 ./RogueSquadron64Recomp            # steady 60 fps (s6703)
cd build && env ROGUESQ_FPS60=1 ROGUESQ_DRAW_DISTANCE=2 ./RogueSquadron64Recomp   # more terrain, ~48-50 fps
cd build && env ROGUESQ_FPS60=1 ROGUESQ_DRAW_DISTANCE=3 ./RogueSquadron64Recomp   # far terrain, ~46 fps (s6789-s6790: dd3 and dd4 0 in-flight terrain dropouts on lvl1, lvl5, lvl10; dd4 ~43 fps)
```

| Goal | Setting | Verified state | Detail |
|---|---|---|---|
| 60 game frames/s (retail ~30) | `ROGUESQ_FPS60=1` | 300 s holds on levels 1, 5, 10: 0 crash, 0 VI stall; hangar soak clean. Craft path per real second unchanged (sim is delta-time); mission clocks time-based; audio tick is per-VI. Not checked: direct NPC position control, other levels. **Owner to judge feel.** Measured on the -O2 build (s6703-s6704, 300 s holds, mission seconds 140+): retail draw distance gives a solid **60.0 fps on levels 1 and 5** (p10 60). With more draw distance it drops: dd2 ~48-50, dd3 ~47, dd4 ~44 fps. The cap is the host cost of each graphics task, so for a steady 60 use FPS60 without DRAW_DISTANCE. | s6255-s6261, s6703-s6704 |
| Fast RSP DMA (on by default in normal play) | `ROGUESQ_G1E_FAST=0` turns it off | Copies RSP DMA in whole words and skips per-DMA debug hooks. Automatically on unless a debug/logging variable is set. lvl5 dd4 FPS60: dense graphics tasks 11.8 -> 9.3 ms, 46 -> 52 tasks/s; identical output (same bytes copied). | s6713 |
| Renderer overlap (higher fps with more draw distance) | `ROGUESQ_RDP_ASYNC=1 ROGUESQ_RDP_NODRAIN=1` | Hands each frame's RT64 render to a worker thread and lets the next graphics task start while it finishes (presents still wait). Graphics-thread cost per task 9.6 -> 5.2 ms at lvl5 dd4. Same-run lvl5 FPS60 dd4: 51.6 -> 55.9 game tasks/s (dips p10 30 -> 42); lvl10 dd4 and lvl1 dd1: 59.5 tasks/s. 300 s holds lvl1 dd1, lvl5 dd4, lvl10 dd4: 0 crash, 0 VI stall, frames sane (docs/img/g1e_s6709_dd4_nodrain_sheet.png). Not yet watched: hangar/menus, fb-effect scenes. **Owner to judge feel; default off.** | s6705-s6709 |
| More terrain drawn | `ROGUESQ_DRAW_DISTANCE=2` (2 qualified on levels 1/5/10; 3 qualified on levels 1/5/10 (s6446: holds 302 s/301 s, 'multiplier 3' echoed, alive_at_end=1, 0 VI stalls, 0 crash lines); >3 needs `ROGUESQ_DD_UNSAFE=1`) | Levels 1, 5, 10 clean for 300 s; triangles x2.3 on level 1. Look (pop-in, haze) unjudged. | `docs/DRAW-DISTANCE.md` |
| Widescreen | `ROGUESQ_ASPECT=16:9` or `21:9`, plus `ROGUESQ_OSMEM_MB=12`, `ROGUESQ_FP_XSCALE`, `ROGUESQ_HUD_ANCHOR` | Level-1 flight frames correct at 796 and 1024 wide, mission held ~182 s. KNOWN DEFECT: wide title screen shows a corrupt block / tiled background (defect B, unresolved, cosmetic, title only). | CURRENT-TRUTH "G1d widescreen" |
| Window fills your screen | `ROGUESQ_ASPECT=16:9` (TV) or `21:9` (ultrawide), or `auto` (match this display); add `ROGUESQ_FULLSCREEN=1` to start fullscreen. F11, Alt+Enter or Cmd+Ctrl+F toggles fullscreen. `ROGUESQ_WINDOW_FIT=0` = old 640x480 window | 16:9: window and fullscreen verified, flight fills it (s6688). 21:9: the forced-route hangar crash is fixed (s6690, our spike scanner's 8 MB mask); lvl1 21:9 missions 3/3 clean; 21:9 window verified s6717 (flight fills 1360x594, HUD at edges; the mission-intro flyover still shows side bars at 21:9). Window size is fixed at launch; resizing letterboxes. | CURRENT-TRUTH "G1f" |
| Faster build (not a game setting) | **ON by default** since s6700: game + host code compiled -O2 (`cmake -DROGUESQ_SRC_OPT=OFF -DROGUESQ_FUNCS_OPT=OFF` restores -O0 for debugging) | lvl5 dd4 ~22 -> 30.5 game fps; lvl1/7/10 + hangar route 300 s clean. Rebuild `build/` after pulling. | CURRENT-TRUTH s6700 |
| Real-microcode graphics (LLE) | **ON by default** since s6738; `ROGUESQ_LLE_FORCE=0 ROGUESQ_LLE_UNGATED=0 ROGUESQ_LLE_SOLO=0` restores the old HLE path | Before s6738 a plain launch drew everything outside the hangar with RT64's HLE path, which showed the boot intro cinematic as a white screen. All soak qualification always ran with these on. | s6738 |
| Seam lines in cutscenes (on by default) | `ROGUESQ_EXACT_EDGES=0` turns it off | Draws each RDP triangle on its exact edges so adjacent triangles leave no gap (s6794: the dark vertical line in AT THE MOVIES sky, 40/939 shots -> 0 seams). | CURRENT-TRUTH "s6794" |
| Spike lines in flight | **ON by default** since 2026-10-31; `ROGUESQ_CULL_SPIKE=0` shows them (retail) | Culls the ucode clip-plane wedge triangles (s6085; retail draws them too, s6454). Only 320-wide flight and >640 widescreen frames; 4:3 hi-res cinematics are never culled (s6792). | CURRENT-TRUTH "G3b/G3c" |
| Frame-time instrument | `ROGUESQ_G1B=1` | Per-VI timing log. | s6017 |

Combos: FPS60 + DRAW_DISTANCE=2 held 300 s clean on levels 1 and 5 (s6262, alive_at_end=1, 0 stalls, 0 crash lines). Widescreen + FPS60 (16:9 and 21:9, lvl1, s6264; needs TITLE_ORIGIN='0x[0-9A-F]*' MISSION_RE='[0-9A-F]+'): flight reached at width=796/1024, ~205 s hold (not the full 300 s), alive_at_end=1, 0 VI stalls, 0 crash lines.

TV (16:9): `cd build && env ROGUESQ_ASPECT=16:9 ROGUESQ_FULLSCREEN=1 ./RogueSquadron64Recomp`. Ultrawide: same with `ROGUESQ_ASPECT=21:9`. Any screen: `ROGUESQ_ASPECT=auto ROGUESQ_FULLSCREEN=1`.

Rules of thumb: combine settings freely only after checking the table. Kill the game with SIGKILL.
