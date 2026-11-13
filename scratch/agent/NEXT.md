# NEXT (s7245): judge the s7244 WIDEWIN merge + R combo by image, not tog kpx
HYPOTHESIS-ID: widewin-heavy-window-cost
State (s7244): merge gate fixed (thr = frac^2 * pass-max node+8). Same-run tog, L4 21:9 dd4+WW+MELT:
m40+R56 win dsd -4.46 ms kpx -0.1%, flight -3.58 ms kpx -6.6%; m40 alone win -2.31; null arm m99 flight kpx +4.7%
-> tog kpx floor ~+-5% in flight: the s7238 flight kpx bar is unresolvable with tog kpx. Logs scratch/s7244q, scratch/s7244r.
Before any rs64_s7239 edit: `zsh tools/s7241_merge_test/run.sh` must print 0 failures (22 cases).
Work unit: an image judgement, ONE build (current), owner idle (check HID idle >= 180 and screen unlocked):
- Arms without TOG (fixed settings, same route, framebuffer capture at the same VI-phase-gated frames, tools/g3_port_capture.sh
  WITHOUT SAVE_FROM): A = WW+MELT (merge off), B = WW+MELT+MERGE=0.4+WIDEWIN_R=56, C = MERGE=0.4 only.
- Score each frame pair with the s7232 kpx classifier AND a far-band pixel diff (side edge / L4 far-left shoreline region),
  then build an owner sheet vs docs/owner_sheet_s7009_widewin_219.png with crack close-ups.
Hypotheses: H-clean (B differs from A only inside haze, no cracks) -> add the B recipe to OWNER-OPT-INS as the 21:9 WW
speed setting, owner judges; H-crack (T-junction gaps visible at merge borders) -> skirt the merged edge or raise frac to 0.55;
H-R-loss (the B flight kpx -6.6% is R=56 cutting visible far cells) -> keep the merge, drop R or raise it to 64.
The queued soak s7237_widewin_r2 (R=48/64/72) is still useful for the H-R-loss arm; leave it queued.
