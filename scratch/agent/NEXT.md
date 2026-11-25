# NEXT (s7921)
HYPOTHESIS-ID: g5c-preflight-43s-hold
s7920: G5c in-flight bar met on all owner-recipe rings s7694-s7919 (tools/s7920_hold_class.py; the s7806 L4 holds were a mission
restart). One IN-SCENE hold remains, deterministic in every run: ~300-400 ms on fb pair 9DE900/A62B80 at t=43.4 s of the owner
route (and 15.3 s after each mission-restart transition), gen/frame 176 -> ~390 across it.
0. `python3 tools/crash_reports.py --since 2026-11-24` first; a new report outranks this.
1. Name the scene: which screen is on 9DE900/A62B80 at 43.4 s (the route: 17 s load at 11 s, flight keys from 95 s; candidates
   briefing/text crawl, level select, hangar). Use an existing capture first (s7919_g5c log_q4.txt: phase ordinal / osViSetMode /
   [s7528] lines nearest the 43 s mark by VI count = 43.4*60), or one short run with ROGUESQ_VI_STAMP=1 + a framebuffer dump at VI
   ~2600.
2. Is it retail? Retail VI-origin timeline over the same scene from the oracle det-pair captures (s7891-s7917 det_cmp / retail
   p1 captures under scratch/s79*; `grep -n 'oracle' docs/CURRENT-TRUTH.md`), counting VIs with an unchanged origin at the same
   scene transition. Port hold is ~18-24 VIs.
Hypotheses: H-retail (retail also holds the origin ~18-24 VIs there: a game-side load/decompress on a static screen -> close G5c),
H-port-load (retail swaps through it; our host does a synchronous load/compile there, e.g. RT64 pipeline creation on the scene's
first frame or a file/DMA burst -> find and fix), H-present (guest swaps but VI origin reporting lags).
Discriminator: retail hold length at the same scene (VIs) vs port's; plus whether the port's gfx tasks continue during the hold.
