# Next work unit (s4475): M5-AUDIO-PLAN Step 9 matrix check (is there a MORT-owned gap?)

HYPOTHESIS-ID: m5-mort-gap
Read docs/M5-AUDIO-PLAN.md Step 9, A20. Steps 7, 8, 10 closed (s4473, s4474, s4434).
H1: complete task/voice matrix shows a MORT-owned gap; H2: no gap (pipelines independent) -> close M5.
Discriminator: tools/mort_probe.py reference output vs guest descriptor/type/rate for the live hangar speech path. Include a same-run positive control.
Optional cheap add: force a guard to fire once (positive control for the s4474 census).
