# Next work unit: split H4 (RT64 rejects flown geometry) from H3 (partial fb dump)
HYPOTHESIS-ID: m6-flown-render-fidelity

State (s5424): flown RDP stream has 2.40M tri vs hangar 349k at ~1.7 tri/submission, so H1 (upstream DL drop) is refuted. Live pair: H4 RT64 clip/cull/depth/scissor drops flown geometry; H3 the fb dump (ROGUESQ_FB_DUMP_DIR, every 500th VI in src/main/upstream_compat.cpp) captures a partial frame. H2 (truly empty sky) disfavoured.

Steps (one build, one run):
1. Add to src/main/rt64_render_context.cpp run_rdp_submission, gated by ROGUESQ_LOG_RT64_DRAWN=1, a log of RT64's per-workload drawn counts after app->processDisplayLists (find the draw-call / triangle counters in lib/rt64 workload structs; if lib/ is edited run ./submodule-patches/export.sh and commit in the same session). Print them with rs64_phase_ord() like [tricnt].
2. Build: DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build -j8
3. Add ROGUESQ_LOG_RT64_DRAWN=1 and ROGUESQ_FB_DUMP_DIR=$OUT/fbd to COMMON in scratch/agent/m6_keyed_hold.sh, then run: zsh scratch/agent/m6_keyed_hold.sh s5425_drawn 200 (screen must be unlocked; no 'r' key). Positive control: hangar phase 0x6ab400 must show nonzero drawn counts and a non-sky hangar frame.
4. Offline: per VI origin sum submitted tri ([tricnt]) vs RT64 drawn; view mission frames with tools/ppm2png.py.

Outcomes: submitted high and drawn ~0 in mission => H4 (next: bisect scissor/viewport/depth in RT64 for that phase). Drawn high and mission frame is sky-only => H3 or readback bug (next: compare dump path vs RT64 framebuffer). Drawn high and the dump shows terrain => H2/H3 resolved, flown render is fine; close the thread.
