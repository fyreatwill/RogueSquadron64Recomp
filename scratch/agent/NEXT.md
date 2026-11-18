# NEXT (s7566)
HYPOTHESIS-ID: retail-chain-simplification

19c CLOSED s7565 (docs/COMPENSATION-CHAINS.md: 12 retail-route chains). Unit: 19d, OFFLINE code read + at most one witness run,
dpc_bridge trio first (src/rsp/dpc_bridge.cpp):
  DPC_KEEP_PIPE  reads at :6492 (g_bf_keep_pipe) and :7425 (s_keep_pipe) -> undoes our bump-time PIPESYNC drop when g_defer_active
  DPC_WRAP_FLUSH :6629, WRAP_RESTORE :6711, S4272 shadow :8045 (restore needs the shadow; s4287 caveat)
Question per child: with the parent at its default, is the child's =0 path still reachable on the default route, and if the
parent were confined (e.g. never drop PIPESYNC at bump time while deferring) would the child become dead code with the SAME
default behaviour?
Hypotheses: H-confinable (parent's harmful branch is reachable only in the state the child repairs -> confine parent, child dead,
behaviour identical) vs H-interlocked (parent branch also does needed work elsewhere -> keep both, document why) vs H-dead-parent
(parent's drop never fires on the default route at all -> both are inert: say so).
Discriminator: read every write/branch of g_defer_active and the PIPESYNC drop path; if needed ONE build with an existing
breadcrumb (no new fields) counting drop-would-fire vs keep-pipe-saves on L1/L4 dd1 4:3 + positive control (KEEP_PIPE=0 arm must
show the s4272 garbage-cimg drop). Then CUT_LIVE vs s6418 (funcs: fixup for 0x8009DEB4 far cutoff), SHADE_ORD_RESET vs its map.
Never flip a default; owner decides. OWNER SAVE RULE: never clear ROGUESQ_NO_SAVE_WRITE; never touch build/saves.
Re-run after any lever change: python3 tools/s7557_gq_census.py --write && python3 tools/s7565_comp_chain.py --write --check
