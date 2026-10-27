# NEXT: fold s6435_aspect_cap, then hangar height
HYPOTHESIS-ID: g1d-aspect-hangar
Fold s6435_aspect_cap from SOAK-RESULTS (arms capdefault vs cap16384, 16:9 lvl1): count "[ucode-cap] fired" per arm in soak_results logs; run tools/g1d_hole_count.py on the flight-width dumps of each arm.
Outcomes: control fires>0 and default 0 with fewer holes -> H-cap confirmed (fix already landed). Control 0 fires -> cap not the hole source; go to H-viewport/H-dump.
Then: hangar VI height/scissor at ASPECT vs 4:3 (~340/448 rows), owner contact sheet, G3 livery diff, G5.
