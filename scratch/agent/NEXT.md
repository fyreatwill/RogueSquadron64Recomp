# NEXT: G1e FPS60 front-end per-tick sites - classify the dR~1 rows from the s6829 capture
HYPOTHESIS-ID: g1e-fps60-frontend-quanta

Context: s6829 fixed the hangar tilt. The same capture (scratch/s6829/{a30,fix,off}.tick.bin, owner save, title -> SELECT YOUR
CRAFT, 62 s) shows the mission tick runs in the front end, and
`python3 tools/g3_float_quanta_rates.py scratch/s6829/a30.tick.bin scratch/s6829/fix.tick.bin` lists front-end rows with
dR ~1.0 and exR ~2 (a per-tick quantum running 2x per game second at FPS60): 0x80044938 (+1 per tick), 0x8002E5A4 (+128,
exR 1.43), 0x80077180 / 0x80077188 (dR 1.00 / 0.75), 0x800B2804 (dR 1.40), 0x80017A4C.
Step 1 OFFLINE first (no build): name each site's function and field (nm / funcs_*.c), check whether it is already in
fixup_fps60_ticks.py FIX/UNFIX sets (s6821-s6825), and what reads the field (timer -> visible? animation phase? edge-
counted input like s6824?). Pass --sites float_sites.tsv if the analyzer needs it for labels.
Hypotheses per site: H-quantum-visible (a front-end animation / timer runs 2x fast at FPS60: fix with the s6821 step or
dt*30), H-benign (counter consumed as a count, or already dt-normalised downstream), H-edge (input/edge-driven, like
s6824: must stay 1 per execution).
Verify (one build, if any fix): rerun scratch/s6829/arms.sh; fixed rows must read dR 0.5 / per-game-s rate = a30.
Done = every front-end dR~1 row fixed or classified with numbers; then G1e rate work is closed and the ladder's next rung
is G3 in-flight frame diffs vs retail on a level not yet matched (s6744-s6748 did lvl1/lvl2).
