# NEXT: read s6101 dd4x soaks, then explain the dd3 vs dd4 split (G1c phase 2)
HYPOTHESIS-ID: g1c-phase2-drawdist
Facts (s6098): dd3+DLPOOLX still dies at begin~6600 after 19 grows (arena not exhausted); crash is a null node in the finder (x4=0x8018B490); dd4+DLPOOLX held 152 s with 1 grow. So pool size is not the limiter and failure is not monotone in dd.
Do: tail scratch/agent/SOAK-RESULTS.md for s6101_dd4x_a/b. Outcomes: both hold 300 s -> dd4 usable; compare dd3 vs dd4 game state at begin~6506 (VI/frame at that begin, mission_t, objects) from fail_att1.log vs run.log; one crash -> dd4 flaky too, take a lldb/ASan backtrace of the finder null (iron rule: name the writer of the empty material list 0x80128EF8).
Budget: 5th iteration on this thread; if s6101 does not split, STOP and cap ROGUESQ_DRAW_DISTANCE to the highest clean setting behind the knob, then take G1d.
