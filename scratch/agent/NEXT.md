# NEXT (s7852)
HYPOTHESIS-ID: g3-retail-flight-det-sweep
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers in docs/OWNER-REVIEW-QUEUE.md, new
SOAK-RESULTS lines. Crash/owner report outranks this.
Why: s7851 closed 0x31=7 (record identical vs r1 once w135/w149, the VI-retrace-owned sound node 0x80137FC4, are TIMING-class;
tick lifecycle EXACT via tools/s7851_snd_node_cmp.py). Continue the sweep with the next mission value.
Unit: `zsh tools/s7849_det_pair.sh 8 scratch/s7852` (0x31=8, ~28 min; run in background, one game/oracle at a time).
 Then read scratch/s7852/score.txt: p1 (pinned) rand first-differing tick, rec_align first nonpose row, rumble-event check;
 p2 (unpinned) must fork (positive control).
Hypotheses / outcomes:
 - H-exact: p1 rand None + record None -> 0x31=8 = retail; next 0x31=9.
 - H-pin-gap: p1 rand forks at tick k -> a dt or seed pin is missing (check tools/s7849_det_pins.py output, RS64_ORACLE_FPR set).
 - H-new-fork: rand exact, record differs -> name the writer with an oracle --watch-write run. USE --hit-cap 100000
   --hit-vi-window 0:20000 (default cap 200 is eaten by exec hits; val= is the value BEFORE the store). Record base is
   0x80137DB0 (w_k = 0x80137DB0 + 4k). Words owned by SI-pass or VI-retrace threads are TIMING-class (s7850, s7851).
