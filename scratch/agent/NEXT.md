# NEXT: holo platform ring is ~7/8 as bright on RT64 as on angrylion (CURRENT-TRUTH item 38)
HYPOTHESIS-ID: g3-holo-ring-brightness
Why: s7181 found SELECT LEVEL / AVAILABLE CRAFT lit ring segments AL (248,248,198) vs RT64 (218,218,172) (x0.88) at the 849x788
ASPECT=4:3 window, and 248 -> 238 (x0.96) at the default 640x512 window (no ASPECT). Flat under presented-frame shifts -3..+3 and
the wall control box agrees (+0.5), so this is not animation lag. MISSION FAILED full-frame brights only -3..-8. s7155 called the
same 16:9 residual "animated holo"; that attribution is doubtful now.
Data kept: scratch/s7141/L17m.cap + .idx + L17mr replays (craft screen swaps 5113-5245, sel level 5041-5101), scratch/s7181/T0r.
Step 1 (offline, no run): decode the ring triangles in swap 5161: extend tools/s7146_opcensus.py (or a sibling) to print per-tri
SetCombine, SetOtherMode (cycle type, blender mux, force_blend, cvg_dest, alpha_cvg_sel, cvg_x_alpha, Z mode), prim/env/fog/blend
colours for tris whose screen bbox covers the ring (x ~140-390, y ~220-290 in the 512x339 fb). Use docs/F5-UCODE-REFERENCE.md.
Hypotheses:
- H-blend: the ring is drawn with a blend / alpha mode that RT64 evaluates differently from angrylion (e.g. alpha 0xE0 applied by
  RT64 while hardware's blender bypasses it with force_blend off, or a 2-cycle combiner overflow that angrylion clamps to 248).
  Predicts: the othermode shows a blend/alpha term ~7/8, and the loss is the same at every resolution once the capture is matched.
- H-res: RT64 at high internal resolution mixes in dark sub-pixel detail (edge AA, texture filtering at the native 3-point vs RT64
  filtering) that angrylion at native resolution does not. Predicts: loss grows with the resolution multiplier. Discriminator: one
  run at ASPECT=4:3 with ROGUESQ_RESMULT=1 vs the default (same window), ring bins via scratch/s7181/py/ringpx.py.
- H-capture: presentation scaling/gamma differs between the two window sizes. Predicts: the wall/text boxes also move with window
  size (they do not at 849x788: control +0.5), so least likely.
- H-retail: angrylion is wrong. Only if the othermode says hardware would dim it; then check against a second RDP model (parallel-rdp).
Then fix in RT64 (lib/: export.sh + commit) or report.
Still open from item 37: interlaced 512x448 level-description screen (press the level-description button on SELECT LEVEL; s7180
reached it after the L17 MISSION FAILED on another route), text crawl, pause menu at 4:3.
Disk >= 20 GB per run; one game run at a time; never write WORKING to STATUS; owner save rule stands.
