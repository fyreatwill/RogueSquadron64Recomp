# NEXT (s7571)
HYPOTHESIS-ID: retail-chain-simplification

19d: dpc trio s7566, CUT_LIVE s7567, SHADE_ORD_RESET s7568, follow-draw trio s7569, S7478 s7570 DONE. Last chain:
Unit: ROGUESQ_G1D_EDGE_CONTENT vs its parent ROGUESQ_G1D_EDGE (src/rsp/dpc_bridge.cpp rs64_g1d_pillar_scan ~5870-5960;
PORTING-STATE '^## Session 6726 ' and '^## Session 6736 '). G1D_EDGE (s6726) trims right-edge source columns no draw reaches,
keyed on scissor; EDGE_CONTENT (s6736) re-keys it on content-draw reach and holds the decision across VI-epoch changes.
Hypotheses: H-dead-parent (with EDGE_CONTENT on, the s6726 scissor rule never decides a trim -> parent's scissor branch is dead),
H-interlocked (both rules contribute trims on the 4:3 debrief / flight), H-confinable (EDGE_CONTENT could replace the scissor rule).
Discriminator: one build counting per-epoch trim decisions by rule (scissor vs content) at defaults, on the 4:3 debrief route and
L1 flight; positive control: EDGE_CONTENT=0 arm must show scissor-rule trims > 0 on the debrief (s6726's own case).
If no debrief route is drivable, use L1 flight 4:3 (s6736: cw 512 flight last column) and say the debrief is unmeasured.
Then close 19d in CURRENT-TRUTH; next = item 20 (new idiom-class audit or ladder rung). Never flip a default; owner decides.
OWNER SAVE RULE: never clear ROGUESQ_NO_SAVE_WRITE; never touch build/saves.
Re-run after any lever change: python3 tools/s7557_gq_census.py --write && python3 tools/s7565_comp_chain.py --write --check
Run template: scratch/s7570/run.zsh (g1e_owner_quiet_arms, ALLOW_SLOW; ARMS "level:tag:ENV+ENV").
