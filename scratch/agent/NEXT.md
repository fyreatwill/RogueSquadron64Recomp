# NEXT: quantify sky-coloured holes in terrain across pose-matched windows
HYPOTHESIS-ID: g3c-edge-arm-route-gate

s6401: contact sheet shows holes (sky-colour where terrain should be) in dd2/aspect/combined, none in retail (1 frame/arm).
Work unit: for each arm's 31 matched frames (windows in PORTING-STATE s6401), count per-frame pixels that are sky-blue with terrain pixel above-and-below in the same column (or terrain below within 40px), report median/p90 per arm; retail must be ~0 (negative control) and a synthetic hole-injected retail frame must score high (positive control). If opt-in arms >> retail: dump RDP tri list/DL for one hole frame (ROGUESQ spike/RDP logging) to see if triangles are missing (terrain cell submit/budget) vs mis-coloured. Do not change defaults.
