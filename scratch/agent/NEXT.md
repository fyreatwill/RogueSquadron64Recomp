# NEXT (s7567)
HYPOTHESIS-ID: retail-chain-simplification

19d dpc trio DONE s7566 (KEEP_PIPE H-dead-parent; S4272/WRAP_RESTORE H-interlocked). Unit: 19d CUT_LIVE vs s6418.
Read src/main/upstream_compat.cpp :82-140 (s6418 far-cutoff scaling of 0x8009DEB4, s6919 ROGUESQ_CUT_LIVE default on) and
tools/apply_s6919_cutlive.py. Question: at dd1 (retail route) does the s6418 block write 0x8009DEB4 at all when CUT_LIVE=1?
Hypotheses: H-dead-parent (s6418 scale is a no-op at dd1 once CUT_LIVE leaves the game's value alone -> CUT_LIVE is s6418's own
dd-gate; say so) vs H-confinable (s6418 still runs at dd1 in some state, e.g. boot latch before level, gate it on dd>1 directly
and CUT_LIVE becomes dead) vs H-interlocked (CUT_LIVE also changes dd>1 behaviour; keep both).
Discriminator: offline read of every write to 0x8009DEB4 from our code; if a runtime witness is needed, ONE run pair at L1 dd1
default vs CUT_LIVE=0 logging the 0x8009DEB4 value per frame (existing log if any) with a dd2 positive control where the scale
must change the value. Then SHADE_ORD_RESET vs its diag map.
Never flip a default; owner decides. OWNER SAVE RULE: never clear ROGUESQ_NO_SAVE_WRITE; never touch build/saves.
Re-run after any lever change: python3 tools/s7557_gq_census.py --write && python3 tools/s7565_comp_chain.py --write --check
