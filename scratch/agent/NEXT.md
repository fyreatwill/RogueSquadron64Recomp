# NEXT (s7723)
HYPOTHESIS-ID: sweep-needs-input-retain

First: `python3 tools/crash_reports.py --since 2026-11-13` (a NEW report outranks everything), then any owner report.
If you edit tools/agent/, `sh tools/agent/run_tests.sh` must stay green.

s7722 closed sweep-report-tools: of the 5 REPORT tools, s7082 (jal census) and s7083 (jr/jump-table lowering census) carry
open-class rows, so they now have `--check` (s7082 also `--plant`) and ARGS rows over the retained pristine front-end pass
(scratch/s7082/regen + regen.work/n64recomp.log.gz). RED controls: an extra unexplained jal line -> OPEN 1 rc 1; one mutated
case label -> "tables all OK FAIL" rc 1. s7031/s7210/s7441 stay REPORT (H-report: pure tables of one capture, reasons updated).

Sweep s7722: 196 gates {GREEN 193, REPORT 3}, 0 RED 0 HOLLOW, 0 NEEDS-INPUT rows, all sweep controls PASS.
Remaining gap of the same kind: the 39 tools s7718 classified NEEDS-INPUT (scorers of one capture) are NOT in the sweep at all
(scratch/s7718/classification.tsv). Unit (offline, no game run, <=2 jobs):
1. For each NEEDS-INPUT row of scratch/s7718/classification.tsv: does its last input still live on disk (grep PORTING-STATE for
   the tool name; scratch/<sNNNN>/), and does its output carry an open-class row?
2. H-retainable (input on disk, <~20 MB compressed): add an ARGS row with its PASS regex, like s7658. H-gone (input deleted):
   leave NEEDS-INPUT, record it. H-dead (superseded tool): mark DEAD with the superseding session.
3. A planted control per newly scored gate (mutate one input row -> RED), sweep ends 0 RED 0 HOLLOW.
Close the slug after one iteration whatever the count; then the ladder has only owner looks left (CURRENT-TRUTH Next steps
2-9; the title plume SIGSEGV is CLOSED s7660, G4 crash hunts are parked). Do not open another sweep step after this.
Owner defaults: never flip.
