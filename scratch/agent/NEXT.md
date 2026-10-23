# NEXT: G1c - fold s6048_dd1b/dd2b/dd3b (spanbound guard)
HYPOTHESIS-ID: g1c-draw-distance
Read SOAK-RESULTS.md lines for s6048_dd{1,2,3}b and grep '[spanbound]' in their logs. Control: dd1b must show no skips and rc=0 (retail path); dd2b/dd3b rc=0 with skips = the writer is confirmed (two lines of evidence: lldb + soak). Still crashing -> next lldb watch on the next corrupted word. Then record distant-terrain fraction per step (gridlog) and, if skips are large, bound the footprint row range upstream instead of skipping stores.
