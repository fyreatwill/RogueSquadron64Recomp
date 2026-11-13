# NEXT (s7280): G5c smallest QoS set: QOS_ALL minus GFX, vs GUEST+PRESENT
HYPOTHESIS-ID: g5c-qos-split
State (s7279, L4 CPU toggle): none 52.0 fps on-load / 48 gaps>=100 / 3 lit freezes; QOS_ALL 59.6 / 1 / 0;
GUEST only 55.0 / 1 / 0 (gpu95 2.67); GFX only 47.7 / 38 / 1. Guest carries the freezes; the leftover fps is render-side.
Hypotheses: H-present (GUEST+PRESENT ~= QOS_ALL); H-wl-upload (needs WL and/or UPLOAD too: GUEST+PRESENT ~55, noGFX ~59.6);
H-gfx-needed (noGFX ~55 too -> GFX only helps alongside the others).
Commands (one game at a time; HID idle >= 120 s, screen unlocked, AC power):
  env LOAD=cpu TAG=l4nogfx LEVEL=4 GXE="ROGUESQ_GUEST_QOS=1 ROGUESQ_PRESENT_QOS=1 ROGUESQ_WL_QOS=1 ROGUESQ_UPLOAD_QOS=1" zsh tools/s7277_toggle_load_arm.zsh
  env LOAD=cpu TAG=l4gp LEVEL=4 GXE="ROGUESQ_GUEST_QOS=1 ROGUESQ_PRESENT_QOS=1" zsh tools/s7277_toggle_load_arm.zsh
  python3 tools/s7277_toggle_score.py l4nogfx ; python3 tools/s7277_toggle_score.py l4gp
  grep ctl=0 scratch/s7272/l4{nogfx,gp}/sheet.txt   # held luma > 0 = real freeze, 0 = black transition
Check GXE with spaces passes through (tools/s7272_g5c_hold_arm.zsh XE); grep the run log for [s6985]/[s6987] lines.
Do not change the default without the owner.
