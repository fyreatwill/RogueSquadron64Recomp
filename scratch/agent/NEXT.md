# NEXT: level-0 framebuffer class coverage from existing captures
HYPOTHESIS-ID: g1-coverage-cd

One offline experiment, no build or game launch. Level 18 now passes the
bounded snow arm (s6654); the recent numeric sweep omitted level 0.
The existing port frames were inspected in s5985/s5998, but no numeric
four-clause verdict is recorded in the current handoff.

Hypotheses:
- H-rule-holds: at least one saved level-0 flight image passes the unchanged
  classifier; numeric and visual content evidence agree.
- H-crop: saved 512x358 crops omit or relocate a fixed-window feature; visible
  flight can fail the rule. Attribute the miss to the exact window, do not
  lower a global threshold or declare a render defect.
- H-no-picture: neither image shows all terrain/craft/HUD; retain the earlier
  single-source visual claim with its limits and name the missing evidence.

Discriminator: score BOTH saved port images with every clause and inspect
both alongside the retail oracle. Report dimensions, clause failures and
which visible content falls outside each fixed window. Positive control:
full canonical table canon_bad 0, level-3 mission 11/13. Do not alter the
classifier in this unit. Do not reopen aim, wins or repeat crash holds.

Commands from repo root:
    python3 tools/g1_flight_class.py
    python3 tools/g1_flight_class.py docs/g3_port_lvl0_oracle_pair_f5000.png docs/g3_port_lvl0_flight.png docs/g3_retail_lvl1_flight_oracle.png

Use view_image for the three files. If a path is absent, locate its saved
source through `rg -n 'g3_port_lvl0|g1_lvl0_oracle_pair' PORTING-STATE.md | tail -15`
and read a <=60-line window; do not recreate a capture unnecessarily.
The oracle's filename says lvl1; s5998 calls it a same-level pair. Preserve
that provenance ambiguity rather than assert retail identity from a name.
