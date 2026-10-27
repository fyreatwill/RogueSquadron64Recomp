# NEXT: find why the terrain submit path emits a shorter display list at dd3 than dd2
HYPOTHESIS-ID: g1c-dd8-limit
Known (s6471): dd3 median tri ~575 in 3 arms (NOFARCLIP, unpinned, pinned) vs dd2 905; DL len 116k vs 205k. Farclip + pin ruled out.
Hypotheses: H-scale (dd^2 scaled radius/count overflows a u8/u16 or hits a clamp at dd3), H-pool (terrain cell pool cap in rs_malloc arena), H-real (retail logic caps cell ring).
Work: read tools/apply_s6036_dd.py + apply_s6418_farclip.py scale constants; list every value scaled by dd or dd^2 and its width/clamp. Then one build that logs the scaled values at dd2 vs dd3 (positive control: dd2 prints, dd3 differs), one run.
Outcome: a value saturating/clamping at dd3 -> fix the width; none -> test pool cap via heap-usage counters.
