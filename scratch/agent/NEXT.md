# NEXT: G1d step 50 - fold HUD anchor + disc region shift into ROGUESQ_ASPECT
HYPOTHESIS-ID: g1d-widescreen
s6158: disc moves with ROGUESQ_SHIFT_REGION (screen-space, size-capped). Work unit: derive A, R, region and disc shift from fb width (w796: A=142,R=334,region 520,630,20,135, shift 192; check w683,w1024 by scaling), apply automatically when ROGUESQ_ASPECT != 4:3, then fix the two leftovers: green reticle should stay centred (find which vp/elem the anchor wrongly moves), and the radar crescent. Verify with fbdump at 16:9 and 21:9 in one run each.
