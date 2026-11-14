# NEXT (s7301): same-pose R88 <-> R128 far-ring A/B at dd8 (in-run toggle), 16:9, L1 + L4
HYPOTHESIS-ID: g1c-window-bind
State (s7300): horizon look sheet docs/owner_sheet_s7300_horizon_dd.jpg says dd8 ~= dd6 on sky-band fog% (H-same), but the arms'
poses diverge across runs, and the far terrain at dd>1 is a dark grid-textured band that a sky-band score cannot see into. Far cutoff
0x8009DEB4 is x dd^2 (s6418) -> beyond the window at dd>=6, so it does not bind. The open question: does the R88 -> R128 ring
(+4400 cells/call, s7292/s7293) put anything visible on screen?
Unit: ONE run per level, toggled in-run (iron rule 2). tools/g1e_owner_quiet_arms.zsh, 16:9 windowed, HOLD=200, same B env as
scratch/s7300/run.zsh plus `ROGUESQ_DD_WIDEWIN_R=88+ROGUESQ_DD_WIDEWIN_R_TOG=1` at dd8 (R88 only on rs64_tog_odd seconds, else the
auto R128; check the apply_s7233 [s72..] tally shows the alternation = positive control). SHOTS every 1 s over t=120..180, so
adjacent shots (one R88, one R128) are ~1 s apart and share a pose. Arms: l1d8t (LEVEL 1), l4d8t (LEVEL 4).
Analysis (offline, new small script): per adjacent pair, map each shot to its toggle phase via the [s7010-clk] anchor, then the mean
abs pixel diff in the far band (12-50% height) minus the same diff in the near band (60-90%), R128-vs-R88 pairs vs R88-vs-R88/R128-vs-R128
pairs 2 s apart (same-phase control for motion).
Hypotheses / outcomes:
  - H-ring-visible: far-band diff of cross-phase pairs > same-phase pairs by a clear margin (and the R128 shot has fewer sky pixels)
    -> R128 draws visible terrain; H-same in s7300 was the score's blindness. Next: G5e fog on the dark far band (owner sheet).
  - H-ring-hidden: cross-phase == same-phase -> the extra ring is behind haze/the far plane or hidden by nearer terrain; R128 costs
    ~1 ms for nothing -> consider dropping dd8 R128 back to R88 (owner decides), next: perspective far plane / haze check.
  - H-toggle-dead: the tally does not alternate -> fix the toggle under the [s7293] auto (auto sets R after the env read?) first.
Then: G5e (fog on extended draw distance) for the dark grid band seen at dd>1 on L1 (s7300 sheet, l1d8 t=250/290).
SOAK_NEEDS_IDLE=180 header if queued (window/keys + screencapture).
