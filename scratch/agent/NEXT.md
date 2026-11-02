# NEXT: G3 cinematic sweep via SHOWROOM > AT THE MOVIES (MAESTRO + DIRECTOR)
HYPOTHESIS-ID: g3-cinematic-sweep

Done s6787: AT THE MOVIES is gated by passcode DIRECTOR in both arms; with it the cutscenes play back to back (VI width 640)
and the first ~90 s match retail at RDP level (1184 aligned frames, tri median |d| 1, 521 full-signature exact, wrong-lag
control 417 vs 23). Concert Hall track changes match. G3 front-end has nothing undriven.
Unit: cover the WHOLE playlist (ending cutscenes are unreachable any other way without winning).
1. Run (~12 min, one game + oracle; check the screen is unlocked):
   `env PASS2=DIRECTOR GAP=16 DWELL=660 RBW=all RMAX_MB=20000 PMAX_MB=12000 EXTRA="12:down,15:a" zsh tools/g3_showroom_pair.sh scratch/s6788/pl`
   (disk: ~324 GB free; retail dump ~1.4 GB menus + cinematics). If the playlist ends/returns to SHOWROOM earlier, the
   1024-wide texrect frames come back: note the time.
2. Offline: extend scratch/s6787/tools/cine.py to load the whole 640-wide span (not just the tail; raise k or walk records by
   VI width from the header), split each arm into cutscenes at hard cuts (tri-count jumps + black frames + the 1-texrect
   title cards), align each cutscene independently (align.py), report per cutscene: frames, tri median |d|, exact-signature
   fraction, control (wrong cutscene pairing) cost. Port window captures per cutscene for an owner contact sheet.
Hypotheses: H-match (every cutscene aligns, residual = cut-transition frames) vs H-diff (a cutscene with a persistent tri
or texrect gap: name the missing draw (PRIM/texture) and its writer, as in the s6762 ucode-cap case) vs H-crash/stall (the
port dies or freezes in a later cutscene: a datum, backtrace it).
If the playlist is longer than one run, a START press may skip to the next cutscene: test it in both arms (retail first).
After this: G1d owner-judgement items stay parked; next ladder rung per ITERATION 3c (G5 renaming last).
