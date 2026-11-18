# NEXT (s7568)
HYPOTHESIS-ID: retail-chain-simplification

19d: dpc trio DONE s7566, CUT_LIVE DONE s7567 (H-dead-parent). Unit: SHADE_ORD_RESET vs its diag map (s6902).
grep -rn 'SHADE_ORD' src tools/*.py; read the map's writers/readers. Question: does the never-cleared shade-order map get filled
at defaults with its log off? Hypotheses: H-dead-parent (map only filled when its log env is on -> reset is dead at defaults),
H-confinable (map filled unconditionally but only read by the log -> gate the fill on the log env and the reset becomes dead; that
is a real engineering change with identical default output), H-interlocked (map feeds a live decision; keep both).
Discriminator: offline read of every insert/read; runtime witness ONE run pair L1 dd1 default vs SHADE_ORD_RESET=0 with a map-size
counter (positive control: size grows without bound at =0 / or with log on).
Then the remaining 19d retail-route chains in docs/COMPENSATION-CHAINS.md (S7376/S7383/S7384, S7478, G1D_EDGE_CONTENT).
Never flip a default; owner decides. OWNER SAVE RULE: never clear ROGUESQ_NO_SAVE_WRITE; never touch build/saves.
Re-run after any lever change: python3 tools/s7557_gq_census.py --write && python3 tools/s7565_comp_chain.py --write --check
