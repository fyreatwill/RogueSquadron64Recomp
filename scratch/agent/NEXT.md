# NEXT: G1 mission coverage — mission count, then levels >= 10

HYPOTHESIS-ID: g1-mission-coverage

OWNER REDIRECT (2026-10-22): the autopilot aim/steer/bolt thread (s5841-s5930,
ROGUESQ_AIM) is closed as harness work. Do not continue it. G1 is per-mission
coverage, defined in tools/agent/ITERATION.md item 3c.

Work unit:
1. Establish the real mission count. Read the level table the s5704-s5705
   level-select hooks index (unlock clamp 0x80130B2F, selector 0x80130B40,
   ROM callback table 0x10B050) and count valid entries; cross-check against a
   second source (level-select menu entries or init-table length).
2. For each level >= 10 up to that count, derive a recipe from s5716_lvl9{a,b}
   (only TAG, ROGUESQ_FORCE_SAVE_MISSION and ROGUESQ_FORCE_UNLOCK change; keep
   ROGUESQ_NO_SAVE_WRITE=1) and queue two runs each.

Hypotheses:
- H1: every remaining level initialises and holds 300 s clean, like 1-9.
- H2: some levels fail (crash, stall, no flight hand-off); each is a datum.
- H3: the forced route cannot select levels >= 10 (unlock clamp or table bound),
  so the lever must be extended first.

Discriminator: per level, the same-run control (forced a1 bit == 1<<level, as in
s5716-s5719) plus alive/crashlines/vi_stalls30s. A run without the control
firing is unevaluable, not a pass.
