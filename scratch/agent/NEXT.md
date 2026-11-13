# NEXT (s7242; s7241 unit-tested the merge host code 17/17, soaks still queued): score the queued soaks: s7237_widewin_r2 (WIDEWIN_R bracket, R=48/64/72) and s7240_widewin_merge (2x2 merge, MERGE=0.4/0.55/0.7)
HYPOTHESIS-ID: widewin-heavy-window-cost
Before any rs64_s7239 edit or after the soak: `zsh tools/s7241_merge_test/run.sh` must print 0 failures.
State (s7240): the merge is BUILT and off by default (tools/apply_s7239_widewin_merge.py, rs64_s7239_* in src/main/upstream_compat.cpp,
[g1cf] wm=, [s7239] tallies, scorer `tools/s7233_widewin_r.py --merge`). Neither soak has run because the owner was active.
Step 1: tail SOAK-RESULTS.md. For a soak that is still queued or came back rc=2: if HID idle >= 180
(`ioreg -c IOHIDSystem | awk '/HIDIdleTime/{print $NF/1e9; exit}'`), run it by hand in the background
(`zsh scratch/agent/soak_queue/<name>.sh > scratch/<dir>/soak.log 2>&1`, then move it to done/). Merge first: it is the new build.
Merge control (iron rule 1): ph1 merged > 0, drop == 3*merged, unm == 0; ph0 anc == 0 and cand > 0.
If the control FAILS, the [s7239] fields name the reason:
- noww >> grp: g_rs64_ww is not set at emit time. Drop the ww gate, or latch ww per frame.
- miss ~ all candidates: the H1 elem does not match the emit list. Re-read node+0x14 / +0x20.
- near ~ all: the frac/farcut units are wrong. Compare maxd2 with farcut.
- flat ~ 0: the flat rule is misread.
- unm > 0: an anchor was never emitted, which leaves holes. Must be 0.
Decide (s7238 bar: window dsd <= -2.5 ms AND flight |dkpx| <= 1%):
- A merge arm meets the bar: take owner sheets at that frac (side edge, L4 far-left shoreline, crack close-ups vs
  docs/owner_sheet_s7009_widewin_219.png), then add the opt-in to OWNER-OPT-INS.
- A WIDEWIN_R arm meets the bar and the merge does not: R wins, so shelve the merge.
- Both meet it: prefer the merge if its flight dkpx is smaller.
- Neither meets it: report the tri removed per merged block. If it is ~6 but ms/ktri is low, the cost is not in the triangles.
  Re-split it with tools/s7231_cost_decomp.py.
