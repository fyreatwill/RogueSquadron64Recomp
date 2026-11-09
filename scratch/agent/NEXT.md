# NEXT: G1c — cull off-map cells only past k x fog end (s7033: the height gate is image-neutral but saves 0 ms)
HYPOTHESIS-ID: g1c-offmap-fogdepth
Context: L1 21:9 dd6 WIDEWIN cap 10240 MELT FPS60. Ungated OFFMAPCULL=2 saves rsp ~8-10 ms (-> 60 fps) but voids the sky at frozen poses 5/6 (|d| 10.6/39.0).
s7033's height gate (ROGUESQ_DD_OFFMAPCULL_H, default on) keeps 99% of the cells (eye above the edge tops) -> rsp +0.01. s7030: FOGCULL k=0.5 (all cells,
on or off map) rsp -4.9 and looked invisible on L1 in a mean image; k03 = FOGCULL 0.3 at the frozen poses 0.5-4.0 (visible).
G5i/owner items: nothing to run (CURRENT-TRUTH items 1-14).
Hypotheses:
 H-fogdepth: off-map cells far enough into the fog are fully fogged (fog colour), so culling off-map cells only when depth > k*fe (k ~0.6-0.8) is
   image-neutral at all 7 poses (incl. 5/6) and keeps >= 3 ms of the rsp win (most off-map cells are 17+ rings out, s7031).
 H-skyfog: the void at poses 5/6 differs from the fogged plateau colour even at k*fe ~0.9 (MELT fog colour != sky band, s7007), so any depth cut
   shows -> only a fill (draw something cheap in the hole) could work; report the trade to the owner.
 H-nearwin: the visible plateau cells at poses 5/6 sit at depth < 0.5 fe, so a k cut that keeps them also keeps most cells (cost win < 2 ms).
Work, ONE build: in rs64_s7031_cell add ROGUESQ_DD_OFFMAPCULL_K=<k> (default 0 = no depth condition): off-map cell past R is culled only if
 d - 0.71 > k * fe (s7030_fe already per frame). Also log, per phase, the off-map culled cells per depth bin (s7031_off hist exists).
Arms (scratch/s7033/run_L1h.zsh as template, frozen poses, separate same-pose runs): offA, r2k06 (R=2 K=0.6), r2k08 (R=2 K=0.8), r2 (_H=off K=0, void control),
 k03 (control). All with ROGUESQ_DD_OFFMAPCULL_H=off. Score tools/s7032_pose_cull_score.py --show r2k06,r2k08,r2. Then cost: scratch/s7033/run_cost.zsh with
 a K tog (or two runs RR=-1,2,2 K=k on phase 1): rsp per phase.
Outcome map: a K at the A/A floor at all 7 poses with rsp win >= 3 ms -> H-fogdepth: add to OWNER-OPT-INS as an opt-in, repeat on L4.
 Every K that keeps >= 3 ms shows a void at 5/6 -> H-skyfog. Image clean only at a K whose win < 2 ms -> H-nearwin: close the off-map cull, report.
