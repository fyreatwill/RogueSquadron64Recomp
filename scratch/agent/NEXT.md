# NEXT: WIDEWIN caps below 6144 vs the VI cliff, one same-run 3-phase toggle (G5e side edge, s7012)
HYPOTHESIS-ID: dd-wide-window
Context: s7012 (21:9 dd4 L4, CULL=1, ROGUESQ_DD_WIDEWIN=tog3 ROGUESQ_DD_WIDEWIN_CAP=4096,6144,8192): rsp 13.62/15.64/16.94 ms, fps 57.3/37.5/34.9,
P(>=2VI) 0.04/0.60/0.72; side-third hard80 left 22.5/17.2/17.6, right 18.2/13.5/14.4. Edge gain saturates by 6144; the fps cost is a cliff at the
16.7 ms VI budget (rsp + guest run ~15.6 ms at 4096). So the question is whether a cap between 4096 and 6144 stays under the cliff and keeps the gain.
Hypotheses:
 H-room: some cap c in 4608..5632 keeps fps >= ~55 (P(2VI) <= 0.1) and keeps >= half of the 6144 side-edge gain -> make c the WIDEWIN default cap.
 H-no-room: P(2VI) rises steeply at the first extra cells (4608 already >= 0.3) -> WIDEWIN is a frame-rate trade; report to the owner (60 fps window
   needs cheaper RSP, e.g. the s6975 gfx QoS / async path, not fewer cells).
 H-edge-late: fps holds at 5120-5632 but edge gain only appears above 5632 -> same owner trade.
Runs (one at a time, scratch/s7012/arm.zsh; tools take --phases 3 / 6th arg 3):
 (1) env NOCAP=1 ASP=21:9 CULL=1 zsh scratch/s7012/arm.zsh 4 4 k2 "ROGUESQ_DD_MELT=1 ROGUESQ_DD_WIDEWIN=tog3 ROGUESQ_DD_WIDEWIN_CAP=4096,5120,5632
     ROGUESQ_G1B=1 ROGUESQ_G1E_TL=$PWD/scratch/s7012/tl_k2.bin" -> python3 tools/g5e_cost_by_parity.py scratch/s7012/tl_k2.bin.<pid>
     scratch/agent/m6/g1_lvl4s7012k2/run.log --phases 3 (positive control: s7012 p0 rsp ~13.6 must repeat; p2 vs p0 must be > 0).
 (2) env CW=1260 CH=540 ASP=21:9 CULL=1 zsh scratch/s7012/arm.zsh 4 4 c2 "<same env minus G1B/TL>" -> python3 tools/g5e_edge_score.py
     scratch/s7012/c2.raw 6 1000000000 50 24e6 3. The raw is ~19 GB: check df first (needs >= 22 GB free), score, make the sheet, delete the raw at once.
Delete run.log files after grepping the [s7012]/[s7010-clk] lines (~300 MB each).
