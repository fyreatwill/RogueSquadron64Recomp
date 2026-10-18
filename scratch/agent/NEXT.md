# Next work unit: is mission ground coverage missing (H4b) or just camera pitch?
HYPOTHESIS-ID: m6-flown-render-fidelity

State (s5427): mission framebuffer renders (sky, horizon sliver, green ship, HUD); readback OK. Ground is only ~10px at frames 3500/4500 (dumps in scratch/agent/m6/s5427_fbd/fbd, every 500 VIs).
Hypotheses: (A) camera pitched up, scene correct; (B) terrain triangles lost post-parse (RT64 depth/scissor/cull); (C) terrain draws never submitted by the game.
Discriminator: one run, dump every ~50 VIs in the mission phase (find the dump interval env near FB_DUMP in upstream_compat.cpp) and view ~6 frames: horizon moves with pitch -> A; ground never exceeds the sliver across varied pitch -> B/C; then compare LOG_RDP_TRICOUNT vs LOG_RT64_DRAWN for terrain-sized DLs.
Command: zsh scratch/agent/m6_keyed_hold.sh s5428 200 (screen unlocked; script now mkdirs fbd).
