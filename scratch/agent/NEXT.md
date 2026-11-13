# NEXT (s7268): fold s7267_169_r88_cost + s7267_r88_edge_sheet — does R=88 hold 60 and soften the sides on the 16:9 TV?
HYPOTHESIS-ID: widewin-169-tv
State (s7267): auto R=88 qualified at 21:9 dd4 (s7266) and 21:9 dd6 (s7267: win 12.30 ms 60/s, control PASS). 16:9 only measured at R=48.
Results: scratch/s7267q (cost: log_a88/a48/w0d) and scratch/s7267e (edge_*.txt, sheet_s88/w88/c219.png).
Controls: w0d must show flat 30 / many beyond-route s; c219 must drop hard80 >=3 on a side (else void, re-queue).
Outcomes:
- H-keep16: a88 win77-97 60/s <~13 ms, 0 flat, beyond-route within ~2 of a48, AND s88 L/R hard80 drop >=3 -> thread closes:
  copy sheet_s88.png + sheet_w88.png to docs/owner_sheet_s7268_widewin_r88_{169,219}.png (check them by eye first: left OFF, right ON,
  no missing ground / cracks), add to OWNER-OPT-INS WIDEWIN paragraph, CT closed note, new slug.
- H-cost16: a88 dips / flat that a48 lacks at 16:9 -> aspect-dependent auto R in main.cpp (~12461), smoke-boot, OWNER-OPT-INS.
- H-nogain16: s88 no side drop -> 16:9 WW shows nothing at R=88; check s7265_ww_r_predict on the 16:9 log for the skip share.
- Any crash -> backtrace first.
If the soaks have not run (owner active): do not wait; take ladder 3c next open owner-look item (G5h cutscenes background at dd2/dd4).
