# NEXT: G1d step 53 - 21:9 (w1024) full-frame check after reticle fix, then menus/hangar under ASPECT
HYPOTHESIS-ID: g1d-widescreen
s6161: reticle fix verified at w796. Work unit: run scratch/agent/s6161_run.sh 21:9 _fix "" and inspect fbdump 5000 (reticle near craft, ring/disc right edge, counter left); then ROGUESQ_ASPECT=16:9 through title/hangar (TITLE_ORIGIN route) fbdump to see whether menus/hangar are correct or need a per-screen policy. Then prepare owner contact sheet (16:9 and 21:9).
