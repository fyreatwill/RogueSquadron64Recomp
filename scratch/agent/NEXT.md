# NEXT (s7830)
HYPOTHESIS-ID: g3-pose-port-input
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers in docs/OWNER-REVIEW-QUEUE.md, new
SOAK-RESULTS lines. Any crash/stall or owner report outranks this unit. G6c and all G5 items wait on the owner only.
Why: s7829 showed the port's lvl1 steady flight pitch (+0.00200 rad) belongs to ONE autopilot schedule (w1024 gate at 13.0 = s7826);
the same binary with the gate at 11.5 (presses 4-10 0.6 s / ~36 game frames later) matches retail 0/42. Retail did not move for a
1.5 s press shift. This is the LAST bounded iteration of this thread (2nd of 2); close it single-source if it does not split cleanly.
Hypotheses (which press picks the pose):
 - H-crawl/intro: press 10 (103.5, skips the intro cinematic into flight) or 7-9 decides the craft's hand-off attitude.
 - H-menu: an early press (4-6) lands in a different menu state (option/camera/craft selection differs) -> different flight setup.
 - H-port-transient: the press lands during a port-only transient (e.g. the 1024 phase) and that changes state retail never sees.
Discriminator: ONE port run per arm, the s7829 13.0 schedule with only one block delayed 0.6 s (all `env SAVE_FROM=scratch/s6779/r1/lvl1.eep
SECS=135 CAP0=12 XE="ROGUESQ_AUTOPILOT_CLOCK=vi RS64_RDP_BIN_PORT=$PWD/scratch/s7830/<arm>.bin RS64_RDP_BIN_PORT_MAX_MB=6000" zsh tools/g3_port_capture.sh scratch/s7830/<arm>`):
  A: AP=6:start,11:start,13:w1024,20.1:start,32.1:start,44.1:start,67.5:start,79.5:start,91.5:start,103.5:start  (presses 4-6 late)
  B: AP=6:start,11:start,13:w1024,19.5:start,31.5:start,43.5:start,68.1:start,80.1:start,92.1:start,104.1:start  (presses 7-10 late)
Score each: find the mission band with `python3 scratch/s7829/tl.py <bin>` (port bins: name without "ret"), then
`python3 tools/s7827_tri_yshift_census.py scratch/s7826/retail.bin.zst <bin> --win 3521:3825,<m0>:<end> --pose 3623:3825,<m0+140>:<end> --pairs`.
Controls in the same run: arm A or B reproducing +0.00200 vs -0.00035 (both are known endpoints from s7829; the census planted controls must PASS).
Outcomes: A pitched and B retail-like -> a press in 7-10 selects (H-crawl/intro); the reverse -> 4-6 (H-menu/H-port-transient: then diff the
two arms' [autopilot] fs and the menu state at that press). Both or neither -> interaction; close the thread single-source (sub-pixel,
not owner-visible) and take the next ladder item (CURRENT-TRUTH Next steps item 13 / owner-pending list).
