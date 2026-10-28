# NEXT: same-run SPANFORCE toggle to measure whether dd4 span rejects hide terrain
HYPOTHESIS-ID: g1c-span-reject-predicate

s6527: clamp irrelevant to the reject; SPANFORCE (tools/apply_s6527_spanforce.py, built) renders sane terrain but cross-run pose differs, so 0.031 vs 0.265 terrain fraction is confounded.
Hypotheses: H-rejects-hide-terrain (toggle raises fraction at identical camera), H-rejects-offscreen (fraction ~equal; rejects are out-of-view = harmless, close thread).
Discriminator: make s6527_force() read a runtime flag flipped every N VIs (e.g. 300) in ONE run with pose pinned; dump fb at the last frame of each phase; score pairs with tools/g1c_fixed_score.py. Positive control: [spanforce] phase log. Raising fraction >2x at same pose -> design a safe dd>1 accept rule; ~equal -> close thread.
