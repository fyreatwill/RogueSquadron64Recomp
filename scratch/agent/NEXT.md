# NEXT: G1d step 46 - verify 0x800159B4 is the flight-HUD sprite emitter, then bias the screen offset
HYPOTHESIS-ID: g1d-widescreen
s6154 static trace: consumer = 0x800159B4; x=(elem+0x18 + vp+0x18)*[0x800006F8] at pcs 0x800160A4..0x800160CC; callers loop lists vp+0xC and vp+0x8 in setupCameraMatrices.
Work unit (one build, one run): fixup-script hook in 0x800159B4 that (a) logs per element [elem addr, x, y, list id] once per distinct elem for ~120 frames of lvl1 flight, and (b) under env ROGUESQ_HUD_CPOS=<px> adds +px to x for elems with x<160 and -px for x>=160 after the 0x800160B0 add. Positive control: ring+disc+ally+counter all shift in one 16:9 frame vs scratch/agent/m6/s6149b baseline; the log must list those elements. Outcomes: elements logged and shift -> anchor at this site, wire to ROGUESQ_ASPECT; flight HUD not logged -> function is subtitle-only, fall back to lists in setupCameraMatrices / runtime read watch.
Also resolve the constant at 0x800006F8.
