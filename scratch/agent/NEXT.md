# NEXT: isPointXzWithinRangeOfRef (0x80047DAC) radius gate: read 0x8003A7D4 (scale) / 0x8003A7D8 (threshold) and the [rng] in/out split at dd1 vs dd3
HYPOTHESIS-ID: g1c-dd8-limit
Known (s6483): processGridCellByDistance floats 0x8003A80C/10 are 0.8/0.5 against a constant 1.0 arg: dead gate, no lever. s6482: inserts have no distance gate.
H-xz-radius: threshold th (0x8003A7D8) bounds which objects/cells are admitted; [rngsum] out>>in at dd3 and scaling th by dd^2 raises populated cells / terrain fraction.
H-not-binding: out count ~0 at dd1 and dd3 => not the limit; pivot to L-lod (0x80137CE4) or fog.
Work: read 0x8003A7D4/7D8 from funcs_8.c data listing (grep 8003A7D); run dd1 vs dd3 with ROGUESQ_LOG_HUDBIT=1 phase-gated (existing soak recipe style), compare [rngsum] per ra. Positive control: [rng] shown[] samples must show both res=0 and res=1 for some ra. Only then add an env lever scaling 7D8 by dd^2 in the s6036 hook (pattern: tools/apply_s6418_farclip.py).
