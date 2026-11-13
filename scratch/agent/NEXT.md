# NEXT (s7292): fold s7292_r_px — is WIDEWIN_R=88 the next limit to raise at dd8?
HYPOTHESIS-ID: g1c-window-bind
State (s7291): real total cells/call (tools/s7291_wide_cells.py) L4 16:9 dd4 5528, dd6 6878, dd8 6809 (px clamp 5), dd6 px8 7453;
R=88 skips 1578 of px8's 5457 wide cells; px8 cost 0 ms (11.20 vs 11.24). OFFMAPCULL acts downstream of the tally.
Unit: fold scratch/agent/soak_queue/s7292_r_px.sh (L4 16:9 dd8: ref / POOLX_MAX=8 / POOLX_MAX=8+WIDEWIN_R=128). If voided or still
queued, run in-session: `zsh scratch/agent/soak_queue/s7292_r_px.sh` (~8 min, idle host, AC).
Outcomes (total_emit + win77-97):
  - H-R: px8r128 total_emit well above px8, 60/s, ms < ~16 -> bundle dd>=8: px8 + R=128 (main.cpp [s7258]/[s7037]), then a look sheet
    (dd6 vs dd8 same camera) and a 300 s hold on L1/L5/L10.
  - H-cost: px8r128 below 60/s -> R88 stays; land px8 alone at dd>=8 if px8 holds 60/s.
  - H-flat: px8r128 ~= px8 -> the game's own far cutoff (0x8009DEB4 farcut, compared at 0x800434E0) binds; scale it with dd next.
Positive control: px8 arms trace depth 128 (tools/s7289_window_bind.py), px8r128 skip ~0, ref depth 80.
