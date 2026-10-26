# Next: scan s6320 RAM snapshots for the player/camera position triple
HYPOTHESIS-ID: g3c-owner-visual
Prereq: SOAK-RESULTS has s6320_g3c_ramsnap; snaps in scratch/agent/m6/s6320_g3c/snaps (delete after analysis, 320 MB).
Run: python3 -I tools/g3c_ramscan.py scratch/agent/m6/s6320_g3c/snaps
Outcomes: H-ramscan = a triple with plausible travel (hundreds of units) -> positive control: its x/z should track AA94 ring cell indices (mod 64 * cell size); then hook the fade with it. H-matrix = no triple -> read translation row from view matrix loaded by the terrain pass. H-none = abandon fade, ask owner whether jagged edge still matters.
If the soak has no snaps (rc!=0), check runner.log first (boring: dir path / env passthrough XENV_EXTRA).
