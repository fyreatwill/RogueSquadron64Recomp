# Next work unit: view mission framebuffer (H3) and, if sky-only, bisect GPU-side drops (H4b)
HYPOTHESIS-ID: m6-flown-render-fidelity

State (s5426): RT64 parser accepts ~100% of submitted triangles in the mission, so drops are post-parse or the dump is partial.
Steps: 1. add `mkdir -p $OUT/fbd` to scratch/agent/m6_keyed_hold.sh before launch (or mkdir in upstream_compat.cpp:495). 2. zsh scratch/agent/m6_keyed_hold.sh s5426_fbd 200 (screen unlocked). 3. convert mission-phase PPMs with tools/ppm2png.py and view; hangar frame is the positive control.
Outcomes: mission frames show terrain => render fine, close thread. Sky-only => H4b: bisect RT64 scissor/viewport/depth/cull for that phase (single run, toggle within run). Partial frames => H3 readback bug.
