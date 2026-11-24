# NEXT (s7875)
HYPOTHESIS-ID: g3-det-render-coverage
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED' | head`, owner answers in docs/OWNER-REVIEW-QUEUE.md,
new SOAK-RESULTS lines. A crash or owner report outranks this.
Parked (s7874): g3-cinematic-half-frame-phase. Evidence table:
| hypothesis | test | result |
| H-dt | retail vs port dt trace (s7872) | refuted, identical from first frame |
| H-count (stall parity) | odd/even stalls (s7872) | refuted |
| H-snap | retail-valued snapshot arms (s7873) | refuted, island unchanged |
| H-phase raw clock | tools/s7874_clock_census.py | refuted, only timeSnapshotFiller reads raw time on render path |
| H-audio | AI_VI_CLOCK=3 arm (s7874) | refuted, island identical |
| H-index / H-retail-rdp | not measured | open; needs the element's DL source first (which function emits the 64 PRIM-FF tris) |
Reopen only with a way to name the element's animation driver (e.g. RDP-stream tri -> DL address -> emitting function).
Unit: extend the det render oracle to a 5th mission: `env RBIN=1 zsh tools/s7849_det_pair.sh 2 scratch/s7875/v2` (needs a new
retail r1, ~2 min oracle + 2 x 305 s port; screen unlocked). Score: `python3 tools/s7868_det_frame_cmp.py <r1/retail.bin> <p1.bin>
--plant --neg <p2.bin>`. Expect flight phase 100% exact (as m6/m11/m12/b17); a non-exact flight frame on a det-exact tick
would be a real render defect -> localise with tools/s7869_island_probe.py. Pre-flight island A should recur (check regression
with scratch/s7874/phase_a_p1.py, OFF/S0 env). Delete bins after.
