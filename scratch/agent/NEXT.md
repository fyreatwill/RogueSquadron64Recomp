# NEXT: fold s6532 dd4+bypass lvl5 repeats (r1-r3); catch the rare SIGBUS
HYPOTHESIS-ID: g1c-span-reject-predicate

s6531 folded: dd4 bypass lvl5 and dd4 optout lvl5 BOTH clean (alive_at_end=1, crashlines=0). s6529's SIGBUS
(si_addr 0x109a0e834, gfx ucode thread) is therefore a rare event, not bypass-dependent at 1/1 each.
1. Read SOAK-RESULTS.md for s6532_dd4_bypass_lvl5_r1..r3; use scratch/agent/m6/*s6532*/summary (alive_at_end, crashlines), NOT rc.
2. Any crash: read run.log backtrace; check whether the faulting host ptr = rdram+>16MB (H-16MB: unmasked ucode DL/vertex read). Fix by masking/relocating in apply_s6036_dd.py.
3. All clean (0/3 + 0/2 earlier): rate <~1/5; add lldb to the recipe or move to ORIGIN work on the -128 span saturation writer (0x80042820/0x800426D8).
