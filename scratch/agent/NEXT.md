# NEXT (s7287): L12 16:9 dd6 heavy-window flat 30 (R=88 auto stack) — split H-R88 / H-dd6 / H-host
HYPOTHESIS-ID: g1c-l12-169-dip
State: s7286 closed dd8 (terrain window binds from dd4; dd8 adds pool+cost only). Side datum: L12 16:9 dd6 win77-97 48.9/s 15.59 ms,
flat 30 t=77-85 (9 s); dd8 43.5/s flat t=76-88. L12 dd6 was qualified only at 21:9 R=48 (s7260, 8.94 ms p50); s7266 raised auto R to 88
and qualified it at L4 only.
Unit: fold the queued soak scratch/agent/soak_queue/s7287_l12_169_dip.sh (if the loop ran it, read SOAK-RESULTS tail + its log;
otherwise run it in-session: `zsh scratch/agent/soak_queue/s7287_l12_169_dip.sh`, ~20 min, needs idle host + AC).
Arms (L12 16:9, HOLD 240): r88 (auto), r48 (ROGUESQ_DD_WIDEWIN_R=48), d4 (dd4 auto), ctl (dd6 STACK=0 + DUTY 1.4, must be worse than r88).
Outcomes:
  - H-R88: r48 60/s in t=77-97 where r88 dips -> make auto R level/aspect-aware (e.g. R=48 on L12 at dd>=6) and re-qualify the side-edge gain there.
  - H-dd6: r48 dips too, d4 clean -> dd6 too costly on L12 16:9; document dd4 as the 16:9 owner ceiling (s7286: dd>4 adds no terrain anyway).
  - H-host: r88 clean this time -> s7286's dip was a one-run host event; note single-source and close.
