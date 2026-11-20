# NEXT (s7690)
HYPOTHESIS-ID: g6c-pair-partner-cull

First: `python3 tools/crash_reports.py --since 2026-11-13` (a NEW report outranks everything), then any owner report.
s7689: the L1 dd2 bunker loss is not the handover knobs, not the route, not the scorer, not frame-parity aliasing. Items that pass the
add test flip between runs at pair granularity (sub 0x14 pairs 803CEB08/CEBC4, CEC80/CED3C, CEDF8/CEEB4; old vs new same-run arms
differ on 10/34 items). The never-added partner is culled every frame.
Hypotheses: H-variant (the pair is one object per difficulty/variant; build_state reads a per-run field so one partner gets a bad
position/scale) vs H-coloc (partners share a position; the game's bucket/view test keeps only one per spot, order decides) vs
H-viewexit (the culled partner fails a specific view-test exit, e.g. far or behind, because its state differs).
Discriminator, ONE build, ONE run (L1 dd2 STANDINS=frame, copy scratch/s7689_handoff_ab.sh, one arm, HOLD 150): at stand-in build log
per item: sub, state pos xyz, scale, model name, item +0x6C..+0x78 (hp per difficulty), item flags; and per item a view-test exit
tally (vt_class of every culled submit, not just held). Join with par= adds:
  - partners have different pos/scale and the culled one is off (zero / far) -> H-variant; fix build_state.
  - same pos/scale, culled one fails at a bucket/link step not the view test -> H-coloc.
  - same pos, culled one fails a view exit -> H-viewexit; read that exit.
One game at a time, SIGKILL only, <=2 CPU-heavy jobs, screen unlocked. Default STANDINS stays off; owner judges the look.
