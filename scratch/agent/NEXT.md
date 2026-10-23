# NEXT: G1c - name the writer of the uninitialised terrain struct under dd2
HYPOTHESIS-ID: g1c-draw-distance
H1: stream fn runs before terrain load completes (struct 0x80136DC0 still zero) because the knob changes timing/branch; H2: struct/window freed or overwritten by an OOB write from a scaled-window loop (poison 0x7F7F7F7F pattern); H3: knob scaling corrupts DEAC float consumer elsewhere (dd3 wild pointer site +9960).
Discriminator (one build, one run): add a probe at stream-fn entry logging *(0x80136DC4), DB0..DBC, caller ra, phase, for dd1 (control, 1x semantic with knob=1.0000001) vs dd2 in the SAME recipe; plus lldb hw-watch on host addr of 0x80136DC4 in dd2 to catch the last writer. H1 => tbl==0 already at first entry in dd2 only; H2 => tbl nonzero at entry then zeroed (watch names writer).
Then: if root cause fixed, levels 5/10 at 2x with G1b frame-time baseline.
