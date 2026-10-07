# Next work unit: M5 A11 — repeat the yield arm and make it default

HYPOTHESIS-ID: m5-a11-pretitle-slot-stall

s4197: ROGUESQ_WAITFORSLOT_YIELD=2000 removed the cap fire (1 -> 0) in one run; hangar reached with 535 VI-512 rows.
Next: rerun scripts scratch/agent/s4197_slot0_yield_ab.sh once more (control must show fires=1), then enqueue it as a soak;
if fires stay 0 and no crash, make unset default to 2000 (edit the fixup template + generated, regen order applies), then move to the next A-item in docs/M5-AUDIO-PLAN.md.
