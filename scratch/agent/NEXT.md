# NEXT (s7262): fold s7261_dd4_stack_levels — does the auto WIDEWIN stack engage and hold 60 at dd4 21:9 on L1/L5/L12?
HYPOTHESIS-ID: widewin-heavy-window-cost
State (s7261): stack auto at dd4 confirmed on L4 (auto 9.77 ms vs off 13.91, merged 3.24M, control PASS). Coverage beyond L4 queued:
scratch/agent/soak_queue/s7261_dd4_stack_levels.sh (results scratch/s7261q).
Hypotheses: H-general (every level: [s7258] dd4 line, merged>0, unm 0, 0 beyond-route dips, alive) vs H-L4-only (some level merges 0 -> gate thr
is level-specific; check [s7239] thr= per level) vs H-crash (an arm alive=0 -> backtrace it, the merge rewrite is the first suspect).
1. Fold: control l12d must show clearly more <55/s s than l12 (else re-run). Then per level as above; update OWNER-OPT-INS "Other levels at distance 4 are queued".
2. If all pass: close this thread (H-ww done at dd4/dd6, L4/L12, + levels); take the next CURRENT-TRUTH item / ladder rung G3 (in-flight frame diffs vs retail).
3. If the soak did not run (owner active): do not wait; take G3 offline work.
