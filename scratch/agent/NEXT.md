# NEXT (s7837)
HYPOTHESIS-ID: g3-port-onset-determinism
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers in docs/OWNER-REVIEW-QUEUE.md, new
SOAK-RESULTS lines. Any crash/stall or owner report outranks this unit. G6c and all G5 items wait on the owner only.
Why: s7836 closed lvl3 flight as H-dtpath (render exact; the path forks at the onset dt). But the port's lvl3 onset dt was 616172 ticks =
0.79 VI: host VI-wake jitter (stamps 1.21 then 0.79 VI apart after a load) reaches the guest through the osGetTime stamp written at
0x8001993C (awaitFrameSyncMesgBlock). On retail, stamps come from Count and are VI-exact. If the jitter varies run to run, two identical
port runs fly different paths: a port determinism defect (owner-invisible today, but it makes every det pair a lottery and could matter
for replays/inputs).
Unit: two identical port runs, one at a time, of the s7836 p1 recipe:
  `env SAVE_FROM=scratch/s7836/lvl.eep SECS=150 CAP0=140 AP=6:start,11:start,11.5:w1024,19.5:start,31.5:start,43.5:start,67.5:start,
   79.5:start,91.5:start XE="ROGUESQ_AUTOPILOT_CLOCK=vi ROGUESQ_S7834_RAMDUMP=1 ROGUESQ_G3C_CAMLOG=1 ROGUESQ_S7835_DT=1"
   zsh tools/g3_port_capture.sh scratch/s7837/pA` (and pB). scratch/s7836/p1/run.log is a third sample already.
Score: onset dt (the `[dt7835] fr` line printed just before the first diverging `[ramdump]` row, ~n=735) and the full-run ramdump rows
(scratch/s7836/rd.py pattern: exact-equal row count between runs, first differing row, last camera words 436-447). Control: the same
run vs itself must give all rows equal; the s7836 retail r1d log vs p1 must show the known fork at row 3.
Hypotheses / outcomes:
 - H-det: onset dt and all ramdump rows identical across pA/pB/p1 -> the jitter is reproducible (load-shaped), port deterministic. Close.
 - H-jitter: onset dt differs (e.g. 0.79 vs 1.00 VI) and the rows fork after it -> port flight depends on host timing. Fix candidate:
   quantise the guest stamp to VI multiples (stamp = VI count * VI period in ultramodern's osGetTime at VI wake, or a fixup at
   0x8001993C writing a VI-counter-derived time); qualify with pA/pB identical after the fix, and an fps/VI-rate check (G1b).
 - H-other: rows fork before the onset dt with equal dt -> another host-timing input (RNG seeded from time, input sampling); name it.
