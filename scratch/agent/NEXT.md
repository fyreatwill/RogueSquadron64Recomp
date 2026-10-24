# NEXT: G1c - prove the draw gain (fixed-camera) then dd15/dd3
HYPOTHESIS-ID: g1c-draw-distance
Hypotheses: H-gain (2x draws visibly more far terrain), H-nogain (a downstream cap L-lod/L-budget hides it; window req grows 1148->2048 but kept stays 1).
Discriminator: fix the [gridlog] kept counter (walk list head->next) AND capture a VI-phase-gated fb at the same phase in dd1 and dd2 on lvl1 (same ROGUESQ_PROBE phase, not an index into fbd/). Compare distant terrain pixel fraction. tools/g1c_fold.py DIR... folds frame time/gridlog. Positive control: a dd that visibly changes (e.g. dd0.5 shrinks).
Then dd15/dd3 on lvl1, then ask owner to judge the look. Default stays retail. Do not run macOS `timeout`; it does not exist.
