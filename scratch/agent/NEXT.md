# NEXT: farclip multiplier A/B at dd3 (H-farclip-scale)
HYPOTHESIS-ID: g1c-dd8-limit
Established (s6474): per-node emit fraction ~5% at dd2 and dd3 (no dd3-specific bail); meshlog shows list d2max (2400-6400 at dd3) >> DEB4 cutoff (1289 at dd3, 573 at dd2), chain=0 in late rows both arms.
Hypotheses: H-cutoff-small (cutoff dd^2*base too low vs list d2 range: raising it x2/x4 restores tris at dd3), H-other (tri count unchanged by cutoff -> limit is elsewhere, e.g. later in the chain walk).
Work: add env ROGUESQ_DD_FARCLIP_MUL (float, default 1) to tools/apply_s6418_farclip.py (extra factor on c.f), regen via fixup, build; queue pinned recipe s6474_sublog.sh style with dd3 x1/x4 (and dd2 x1) + MESHLOG/SUBLOG; compare chain and stripN and per-frame tri count (s6470 metric). Positive control: chain must grow with x4.
