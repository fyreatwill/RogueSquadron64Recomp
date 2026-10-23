# NEXT: G1c - fold far-plane arms
HYPOTHESIS-ID: g1c-draw-distance
Fold SOAK-RESULTS lines s6031_g1c_{farret,far025,far2,far4,near4}. Read `[g1c] state=` bins (tri>=50) and `[far]` log lines. Outcomes: far025 cuts tri/task (positive control) AND far2/far4 raise it => far clip is the extend lever, expose as ROGUESQ_DRAW_DISTANCE; far025 cuts but far2/far4 flat => projection far is not the limiter (grid radius/software cull is), go L-budget (grid buffer 0x80137A68) or software cull on camera struct +0x28; far025 flat => hook not effective, check `[far]` log fired first.
