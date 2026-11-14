# NEXT (s7300): horizon-in-view dd6-vs-dd8 owner look sheet (16:9 + 21:9)
HYPOTHESIS-ID: g1c-window-bind
State (s7299): dd8 px8 auto ([s7293]) qualified at 16:9 (s7294) and 21:9 (s7298): 300 s, 0 crash, 60/s on L1/L5/L9/L10/L12 (+L4).
s7295 look sheet (docs/owner_sheet_s7295_dd6_dd8.jpg, SHOTS t=100-140) was camera-limited: route banks under cliffs, horizon off-frame.
Unit: one capture, analysed offline. tools/g1e_owner_quiet_arms.zsh with SHOTS spread wide (e.g. t=90..290 every 10 s), arms L1 and
L4 x {dd1, dd6, dd8} at 16:9 (same autopilot timeline -> column k = same route second). Score with tools/s7295_dd_look_sheet.py
(fog% band score, built-in CONTROL PASS line), pick the seconds where the dd1 arm shows the most sky band (horizon in view) and
build the sheet from those columns.
Hypotheses / outcomes:
  - H-more: dd8 fog% < dd6 fog% by >=3 points on the horizon-in-view columns of both levels -> dd8 visibly draws more; send sheet.
  - H-same: |dd8-dd6| < 3 points while dd1-dd6 >= 3 -> the far cutoff (0x8009DEB4 / far plane) or haze hides the extra cells;
    next unit = the game far cutoff 0x8009DEB4.
  - H-none-in-view: dd1 arm never shows a sky band -> route unusable; pick a different level/second (L5 sea level) or add a pose lock.
Controls: the script's painted-band CONTROL PASS, and dd1 > dd6 fog% (real-scene control).
SOAK_NEEDS_IDLE header if queued (window/keys + screencapture).
