# NEXT: G1c dd6 cost split — cells vs the dd multiplier (same run)
HYPOTHESIS-ID: g1c-dd-headroom
Context (s7019, L1 21:9 WIDEWIN owner path, separate runs): dd4 59.5 fps rsp 12.6 run 3.13; dd6 55.8 rsp 13.9 run 3.78; dd8 53.3 rsp 14.0
run 3.99. POOLX is clamped to 5 (src/main/main.cpp rs64_g1c_apply_dd_policy) so dd>=5 = 10240 cells, window 128x80; dd8 = dd6 cells but
costs more. G5i: fixed, owner look only — check CURRENT-TRUTH item 1 first anyway.
Hypotheses: H-cells (the extra cost is the 8192->10240 cells: at dd6 with cap 8192 the cost returns to dd4's), H-mult (cost scales with the dd
multiplier itself — grid radius/auto-far/object draw distance/LOD — and stays at cap 8192), H-both.
Discriminator, ONE run: dd6 with ROGUESQ_DD_WIDEWIN=tog3-style cap cycling (ROGUESQ_DD_WIDEWIN_CAP=8192,10240,10240 per s7012, check the env
form in tools/apply_s7012_widewin_cap.py / rs64_s7012_cap), analysed with tools/g5e_cost_by_parity.py --phases 3. rsp/run delta 10240-8192
~= dd6-dd4 (1.3 ms rsp, 0.65 run) => H-cells; ~0 => H-mult (then name which multiplier term with the dd8 run's extra run time).
Recipe: copy scratch/s7019/all.zsh (one arm, NOCAP=1 — captures are 2 MB/frame and filled the disk in s7019; never capture >30 s), dd6, 320 s.
Drop GLUE_TOG=3 if tog3 prints the anchor itself. Positive control: the 0.33-period-shifted split must smear the delta.
