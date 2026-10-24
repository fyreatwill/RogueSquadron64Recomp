# NEXT: G1d step 2c - read s6105 extreme-k soaks
HYPOTHESIS-ID: g1d-widescreen
Look at the last fb dump (sort numerically, sips -s format png) in scratch/agent/m6/g1_lvl1g1ds6105_k3p0/fbd and ..._k0p4/fbd. H1: r7 is the aspect -> craft/terrain visibly stretched/squeezed (k3 narrow, k0.4 wide). H2: no visible change -> aspect arrives elsewhere (FP reg f14 or stack); inspect setupCameraMatrices call site in funcs_4.c. If H1: next ONE build widens game colour image/scissor/VI width under ROGUESQ_ASPECT, then 16:9 window screenshot. Then HUD x anchoring.
