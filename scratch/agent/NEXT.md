# Confirm PAUSE=4 and make it default; then resume the 0x2C splice route

HYPOTHESIS-ID: factor5-overlay-0x2c-splice

s4785: PAUSE=4 survives where PAUSE=0/3 crash (+5808) and reaches VI 512 (n=1 per arm).
Work unit: (1) read the SOAK-RESULTS line for s4785_pause4_600s (loop runs it); if no crash in 540 s, make PAUSE=4 behaviour default-on in tools/apply_s4562_synth_pause.py (s_on default 4 unless ROGUESQ_S4562_PAUSE=0), regen-safe, rebuild. (2) rerun the VI640->hangar key route (ROGUESQ_S4562_PAUSE unset) and look for res=0x2C rows (the original s4761 blocker). Competing: if soak crashes, the crash site differs from +5808 => a second freed-arena reader (check pc-symbol); if it passes, +5808 class is closed.
Control: PAUSE=0 arm crashes +5808 at ~80 s (s4785_0).
ORIGIN: retail ordering (s4783/s4785).
