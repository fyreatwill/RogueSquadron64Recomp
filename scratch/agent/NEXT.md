# NEXT (s7296): fold s7296_219_dd8_px — does dd8 px8(+R128) fit at 21:9 on L4?
HYPOTHESIS-ID: g1c-window-bind
State (s7295): dd8 px8+R128 auto ([s7293], 16:9 only, FB_WIDTH<=796) qualified 300 s on L1/L5/L10/L12 (s7294, ctl PASS).
Look sheet docs/owner_sheet_s7295_dd6_dd8.jpg is camera-limited (horizon off-frame at route t=100-140).
Unit: fold scratch/agent/soak_queue/s7296_219_dd8_px.sh (if still queued/voided, run it in-session, ~12 min).
Outcomes:
  - H-219-ok: px8r128 total_emit >> ref, win77-97 60/s, ms < ~15 -> drop the FB_WIDTH<=796 gate in main.cpp [s7293] (21:9 too),
    verify auto in-session.
  - H-219-px: px8 fits, px8r128 dips -> 21:9 auto = POOLX_MAX=8 + R88.
  - H-219-cost: px8 itself dips -> keep the 16:9 gate, record it.
Positive controls: px8 arms trace depth 128 (s7289_window_bind), ctl flat 30.
After: a horizon-in-view dd6-vs-dd8 sheet (later route seconds where the craft levels out, or ROGUESQ_POSE_LOCK), then the
game far cutoff 0x8009DEB4 as the next distance limit.
