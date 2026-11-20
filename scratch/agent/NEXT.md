# NEXT (s7727)
HYPOTHESIS-ID: owner-looks-or-new-report

First: `python3 tools/crash_reports.py --since 2026-11-13` (a NEW report outranks everything), then any owner report, then any
new SOAK-RESULTS.md lines.
If you edit tools/agent/, `sh tools/agent/run_tests.sh` must stay green.

s7726 closed the Objective-C over-release thread for the L4 owner route: NSZombie census (tools/s7726_zombie_census.py) default
0 zombies boot+flight, MTL_OWN=0 control 163. Do not repeat it on the same route.

Optional bounded unit if nothing above applies: the same zombie census on the hangar route (owner normal boot into SELECT YOUR
CRAFT, scroll ships, start a mission) — the one Metal path s7726 did not cover (hangar 3D view, G5g camera). One game, two arms
(default vs ROGUESQ_MTL_OWN=0 control), then
`python3 tools/s7726_zombie_census.py --arm <default log> --control <own0 log>` (note: its boot/flight split keys on the
level-select cursorMask line; on the hangar route treat the whole log as one phase). Hypotheses H-clean vs H-hangar (a freed
object only on the hangar draw path). A nonzero default-arm class names the next writer; grep its factory and fix like s7725.
Owner defaults: never flip.
