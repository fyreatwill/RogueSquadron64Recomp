# NEXT (s7871)
HYPOTHESIS-ID: g3-det-render-coverage
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED' | head`, owner answers in docs/OWNER-REVIEW-QUEUE.md,
new SOAK-RESULTS lines. A crash or owner report outranks this.
State (s7870): the det render oracle line is CLOSED: flight frames of b17 (1120), m12 (5662), m6 (0x31=5, 2383) are bit-exact
vs retail on det-exact ticks; every non-exact frame seen so far is pre-flight (phase before tick 0) and state or timing class.
Unit (one det pair, ~25 min, one game run at a time): extend coverage to a mission with different render content - Bespin
0x31=10 (mission 11, cloud layers/transparency) - `env RBIN=1 zsh tools/s7849_det_pair.sh 10 scratch/s7871/v10`, then
`python3 tools/s7868_det_frame_cmp.py scratch/s7871/v10/r1/retail.bin scratch/s7871/v10/p1.bin --plant --neg scratch/s7871/v10/p2.bin`.
Read the "phases in exact span" table: flight = the final port phase (HUD texrects present).
Outcomes: H-clean = final phase 100% exact (4th mission, coverage); H-render = non-exact flight frames while det p1 is still
exact for that tick range -> print the differing tris (s7869_island_probe.py with p1 vs p2: identical wrong tris in both arms
inside flight = a real port render defect; find the DL op). If det p1 forks (audio-clock), score only up to the fork.
Delete the bins after scoring (6 GB per pair).
Fallback if the pair cannot run (host busy / screen locked): offline - measure what drives the s7870 cinematic half-frame
phase (port VI-clock phase at cinematic start vs retail; oracle.log + p1 run.log VI stamps), report-only.
