# NEXT (s7911)
HYPOTHESIS-ID: g3-preflight-load-class-census
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED' | head`, docs/OWNER-REVIEW-QUEUE.md answers,
new SOAK-RESULTS lines. A crash or owner report outranks this.
State (s7910): m11 island B closed. Post-load content is time-keyed, so the port's shorter load stall shifts the frame lag
by stallDelta/2 (71 -> 99, tools/s7910_fork_lag.py, control lag 71 err 0).
Work unit (one bounded census, offline): every det-pair mission with a pre-flight non-exact span (s7870 phase report; m6 island B
N212/N1182 under SNAP=3, m16 intro phase 6 -98 -> -99, b16 723-frame lead-in) gets classified as H-loadshift or unexplained.
H-loadshift: the s7910 lag tool gives a constant post-fork lag = pre-fork lag + (retail stall - port stall)/2, with the stalls
from tools/s7909_window_vi.py on the same runs.
Unexplained: no constant lag, or a lag that does not match the stalls. That makes the mission a candidate render/scene diff.
Hypotheses: H-all-load (every pre-flight island is the load-time class -> close the pre-flight G3 class), H-mixed (one or more
islands with a non-matching lag -> that mission becomes the next G3 unit). Needs retained retail+port bins per mission:
list them first with tools/retained_captures.txt; missions without both bins are "na", not exact.
If all classify H-loadshift: close the class in CURRENT-TRUTH item 0 and take the next ladder rung (owner queue items, or G1e).
