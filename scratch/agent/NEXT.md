# NEXT (s7569)
HYPOTHESIS-ID: retail-chain-simplification

19d: dpc trio DONE s7566, CUT_LIVE DONE s7567, SHADE_ORD_RESET DONE s7568 (all H-dead-parent or interlocked).
Unit: follow-draw mode 3 chain S7376_PQLOCK / S7383_FBPACK / S7384_LDGFX (parent: ROGUESQ_VI_FOLLOW_DRAW mode 3, port default
since s23). grep -rn 'S7376\|S7383\|S7384\|VI_FOLLOW_DRAW' src lib/rt64/src lib/N64ModernRuntime; read every writer/reader of
the last-drawn fb tuple and the targetMap insert.
Hypotheses: H-dead-parent (the torn read / second writer / unlocked insert cannot happen at defaults -> children are dead code),
H-confinable (the race is real only because the present thread does work it need not; move it to the Gfx thread and the
locks become redundant), H-interlocked (mode 3 needs cross-thread reads; keep all three).
Discriminator: offline thread map of each access; runtime witness ONE run set L1 dd1 default vs each child =0 with a
cross-thread access counter (positive control: =0 arm must show the second-thread write/torn pair > 0).
Then S7478 (canary), G1D_EDGE_CONTENT. Never flip a default; owner decides.
OWNER SAVE RULE: never clear ROGUESQ_NO_SAVE_WRITE; never touch build/saves.
Re-run after any lever change: python3 tools/s7557_gq_census.py --write && python3 tools/s7565_comp_chain.py --write --check
Run template: scratch/s7568/run.zsh (g1e_owner_quiet_arms, ALLOW_SLOW).
