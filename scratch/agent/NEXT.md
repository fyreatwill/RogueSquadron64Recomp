# NEXT (s7923)
HYPOTHESIS-ID: hold-metric-animating-label
s7922: the pre-flight route is retail-paced (6/6 transitions port <= retail). Remaining ladder items are owner-look. One bounded
engineering unit: the soak summary field `max_vihold_ms` (tools/g1e_owner_quiet_arms.zsh / tools/s7919_gap_check.py) reports
17318 ms on every owner-recipe run, which is the single-buffered ANIMATING title (gen advances on 100% of rows, s7921/s7922),
not a freeze. Any future G5c regression check reading that field is blind (a real 5 s freeze hides under 17 s).
0. `python3 tools/crash_reports.py --since 2026-11-24` first; a new report outranks this.
1. Find where max_vihold_ms is computed (grep max_vihold_ms tools/). Add the s7922 rule (hold > 2 s with gen advancing on >= 90%
   of rows = animating, excluded) and print `max_vihold_ms` (freezes only) + `max_animhold_ms` (separately).
2. Planted controls in the same tool run: a synthetic 1 s hold with gen frozen must count; a 17 s hold with gen advancing must
   not. Re-score scratch/s7919_g5c/ring_q4.txt and scratch/s7921_port2/ring_q4.txt: expected max_vihold_ms ~300-390 ms.
3. Keep the old field's meaning documented in the session entry (soak verdict lines before s7923 used the raw value).
Hypotheses: H-title-only (the 17 s value is always the title; after the fix max_vihold <= 400 ms on both rings) vs H-other (some
other >2 s hold appears with frozen gen = a real freeze the field was hiding -> root-cause it).
