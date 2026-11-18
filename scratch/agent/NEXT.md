# NEXT (s7599)
HYPOTHESIS-ID: guest-driven-container-growth-census

Class AZ closed s7598 (137 guest-sized alloc/createTexture sites, 0 open; AZ-1 SETTILE mask clamp to 10). FIRST fold soak
s7598_maskclamp_flight from SOAK-RESULTS (clamp lines per arm L1/L4: 0 = AZ-1 never touches retail data; >0 = take a same-run
framebuffer pair, ROGUESQ_S7598_MASK=0 vs default, at that scene and report whether the view changes).

Class GR = long-lived host containers (static/global/member vectors, maps, sets, deques, strings) that grow by
push_back/emplace/insert/operator[] once per GUEST event (draw call, DMA, RSP task, osCreateThread, message, texture hash,
framebuffer address) and are never cleared, capped or evicted in the owner recipe. Consequence: host RSS climbs over a long
mission (class LK s7585/s7586 measured RT64 memory flat after warm-up, so expect few hits; the census must prove it per site).
Per site: container lifetime (per-frame / per-workload / run-lifetime); clear/erase/cap present?; growth unit; gated?
Hypotheses: H-bounded (every run-lifetime container is capped or keyed by a bounded domain), H-grow (one grows per event ->
RSS slope), H-gated (growth only in env-gated diagnostics).
Tool: tools/s7599_gr_census.py --controls (plant an uncleared static vector push_back per draw in a copy of rt64_state.cpp + drop a
row; both caught). Runtime witness for any H-grow row: RSS + container size sampled over a 300 s owner-recipe hold (queue as a
soak with SOAK_NEEDS_IDLE=300 if the owner is active), old vs capped arm.
Never touch build/saves; never clear ROGUESQ_NO_SAVE_WRITE.
