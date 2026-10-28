# NEXT: lvl7 cap-bound at dd4/dd6 — find the cap that trims it and test raising it
HYPOTHESIS-ID: g1c-dd-phase2
State (s6585): lvl7 (93x96) cap-trimmed 3/6 at dd4 and 2/5 at dd6; lvl3 trims only at dd4 (1/9). lvl1/5/10 extent-bound. Harness mission-detect reports failure for lvl3/lvl7 (set MISSION_RE like lvl10's '6A2900|644D00' equivalent for those levels; origins seen: 0x62BD00/0x696100) so no 300 s hold exists yet.
Work unit: (1) find the lvl7 mission origins and set MISSION_RE so the harness passes; (2) in apply_s6036_dd.py/main.cpp bundle find where cap (2000-3500) is derived and add an env override ROGUESQ_DD_CAPX; (3) run lvl7 dd4 with CAPX=1x vs 2x in ONE run via a toggle (ROGUESQ_DD_TOGGLE style) and compare trim flags + post area in phase-gated windows; then 300 s hold.
Outcomes: trim 0 and area grows with CAPX => cap is binding, bundle it; trim persists => other limit (pool/px).
