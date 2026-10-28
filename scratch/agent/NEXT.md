# NEXT: fold s6531 lvl5 dd4 bypass/optout soaks; name the SIGBUS address source
HYPOTHESIS-ID: g1c-span-reject-predicate

1. Read SOAK-RESULTS.md for s6531_dd4_bypass_lvl5 / s6531_dd4_optout_lvl5; use m6/*/summary (alive_at_end, crashlines), NOT rc.
2. Both crash => dd4 address-range crash (H-16MB: unmasked gfx read above 0x81000000); only bypass => bypass owns it; neither => rare race, ask lldb loop.
3. If H-16MB: find which pool addresses >0x81000000 feed the ucode (grep DL/vertex segment setup in apply_s6036_dd.py), relocate below.
4. Then ORIGIN work on the -128 span saturation writer.
