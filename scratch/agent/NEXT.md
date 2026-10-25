# Wide title/select-game art x-origin (+241 vs 0)
HYPOTHESIS-ID: g1d-widescreen
(Rewritten s6223 after the CURRENT-TRUTH maintenance compaction; the work unit is unchanged from s6222. CURRENT-TRUTH "G1d widescreen" is now the distilled state; the old log is in PROJECT-OVERVIEW.md.)

s6222: wide phase-4 title art = same 64x32 texrect grid as 4:3 but at x 241..753 (centred would be 142); stride refuted.

Hypotheses:
- H-origin-global: the menu layout x-offset derives from the width global 0x8011A838 or a widened constant, e.g. (W-314)/2 or 160*scale. Predicts a constant 241 across all phase-4 frames.
- H-slide: the art slides in and 241 is an animation phase. Predicts x varying across frames, converging to a constant.
- H-hook-side-effect: the s6113 menu-dimension hook rewrites a value later used as texrect x. Predicts the offset tracks the hooked dimensions, and disappears when the hook is off for the 512x340/512x448 rewrites.

Discriminator: log the minimum x of the 64-wide tiles per submit for every phase-4 frame in the wide arm (do not use the 4000-row cap). Constant 241 over 100+ frames means H-origin-global or H-hook; varying means H-slide. Then use lldb or a guest write-watch on the caller of the texrect emitter at PC 0x80007904 to find the x-origin operand and its source.

Run: adapt scratch/agent/s6222_run.sh. First `pkill -f m6_god` and `pkill -f '_run.sh'`, and pgrep for orphan games (one game at a time). Analyse fail_att1.log; the route gate fails for wide arms by design. Positive control: the c43 (4:3) arm must report column 0 / x origin 0 in the same run.
Kill the game with SIGKILL. Run from build/ with the ROM beside it.
