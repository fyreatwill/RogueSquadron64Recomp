# NEXT: G1e higher frame rate - measure real game frame rate
HYPOTHESIS-ID: g1e-framerate
s6432: G1d wide-edge hole not reproduced (see PORTING-STATE s6432); G1d considered done pending owner look.
Work unit: per level (1,5,10) count distinct framebuffers/sec vs VI/sec in a 60 s flight window (ROGUESQ_FB_DUMP_EVERY=1 hash, or VI-origin changes). H-30 (game presents every 2 VIs), H-20 (every 3), H-60. Positive control: FPS60 opt-in arm must show ~60 distinct/s. Then read the game retrace divisor lever (CURRENT-TRUTH FPS60 notes).
