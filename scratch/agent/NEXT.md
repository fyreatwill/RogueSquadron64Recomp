# NEXT: G1c - fold s6054_dd{1,2}_l{1,10}
HYPOTHESIS-ID: g1c-draw-distance
Hypotheses: H-gain (2x window draws visibly more far terrain on lvl1), H-nogain (window grows but a downstream cap - L-lod/L-budget/node list - hides it), H-regress (frame time or crash at 2x).
Discriminator: per level, from scratch/agent/m6/g1_lvl{1,10}g1cdd{1,2}l*f/: crashes/VI stalls in summary; G1B frame time p50/p99 dd1 vs dd2; distant-terrain pixel fraction in matching-phase fb captures (fbd/). Note gridlog kept==1 is non-discriminating; fix the counter (walk list head->next properly) only if H-nogain needs it.
Then dd15/dd3 on lvl1, then ask owner to judge the look. Default stays retail.
