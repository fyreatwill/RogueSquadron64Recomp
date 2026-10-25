# NEXT: G1d step 52 - reticle centring under HUD anchor, w683 check
HYPOTHESIS-ID: g1d-widescreen
s6160: radar law fixed (w796, w1024 aligned). Work unit: find which viewport/sprite the ROGUESQ_HUD_ANCHOR moves that displaces the green aiming reticle (compare reticle x at ASPECT=16:9 with and without anchor, fbdump frame 5000, script scratch/agent/s6159_run.sh <aspect>); then exempt it. Also run ROGUESQ_ASPECT=3:2 for w683 sanity.
