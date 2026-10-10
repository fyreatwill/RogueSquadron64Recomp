# NEXT: where does the post-free 128-record array sit relative to the node array, retail vs port?

HYPOTHESIS-ID: musyx-stale-stream-node-after-teardown

Context: docs/M5-STREAM-NODE-LIFETIME.md (s4524). Hypotheses A/B refuted; D open: retail overlays the freed block too but its synth rebuilds nodes (0x8008FBB4) each frame.
Work unit (one oracle run + one port run, both phase-gated to hangar VI 512 / post-free): record the first physical address written by retail PCs 0x8001FAE4/0x8001FAEC (the 128-record init; reuse the s4317 Rice + --vi-trace recipe, whole-RDRAM control first) and the port's loadLevelTextureCache array base (rs_malloc log, ptr/size) and the node array base 0x17DBE0.
Outcomes: retail array disjoint from live nodes => port heap layout differs (chase earlier rs_malloc history). Retail array overlaps node romA/romB => port fails to run the 0x8008FBB4 rebuild (compare caller of that PC in port).
