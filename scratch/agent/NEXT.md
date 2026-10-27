# NEXT: G3c(c) measure VI sleep-then-spin (s6456 change)
HYPOTHESIS-ID: g3c-shake
Change landed s6456 (events.cpp, spin last 2 ms; ROGUESQ_VI_NOSPIN=1 = old). Queue two soaks (same recipe as s6455 [g3c] logging): default vs NOSPIN. Compare VI dt sd and alternation. sd drops from ~2 ms to <0.5 ms with spin only -> timer oversleep was the cause, keep spin, tell owner. No change -> sd is upstream of the sleep (scheduler/logging); close G3c(c) as retail 30 Hz judder, move to G1c phase 2.
