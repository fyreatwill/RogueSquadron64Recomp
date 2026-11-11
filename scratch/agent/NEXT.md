# NEXT: NEARLIFT sampling-depth arm (residual near-wall losses sit at terrain 1.0-1.5 near, beyond the lift's 1.05)
HYPOTHESIS-ID: fps60-wall-frame
Context (s7117, tools/s7117_tickjoin.py on scratch/s7115 d-g): a swap shows the previous tick's camera (k=-1 join). 27/31 lift-on losses do not pierce
the near pyramid (to 1.0 near) at any offset; 26/31 have the surface at 1.0-1.5 near, vs ~0.31 of lift-on flight. The lift (tools/apply_s7115_nearlift.py)
samples t = 0.25 s nr, s = 1..4 (to 1.0 near) and lifts need + 0.05 nr.
Hypotheses: H-margin (the visible loss starts before the surface reaches the near plane: real clip distance, guard band or the eye-cell clip
uses more than 30/256, or the triangle straddling near is lost whole), H-proj (the render projection differs from f20/half-tans 1.368/0.637), H-other
(losscan rule false positives at these swaps).
Change: add ROGUESQ_S7115_NEARK=<k> (default 1.0) to apply_s7115_nearlift.py: sample s = 1..ceil(4k) at t = 0.25 s nr, and accept tog form
"tog1" for the lift plus ROGUESQ_S7115_NEARK=togK:<k> = k on odd seconds, 1.0 on even, with the lift ON always (ROGUESQ_S7115_NEARLIFT=1). Log k in the nl line.
Regen order: make_elf.py -> N64Recomp -> fixup_game_funcs.py -> cmake (the fixup list already carries apply_s7115_nearlift.py).
Run: scratch/s7115/arm.zsh 6 4 h "ROGUESQ_S7115_NEARLIFT=1 ROGUESQ_S7115_NEARK=togK:1.6 <s7115 passive instruments from cmd_g.txt>", then
s7107_losscan, s7116_phase (on = k1.6 half), s7117_tickjoin. Positive control: nl need > 0 on more ticks in the k1.6 half.
Outcomes: H-margin: k1.6 half losses fall clearly (>2x) with control passing; H-proj/H-other: no change -> make a sheet of the residual swaps from h.raw
(tools/s7107_sheet.py) to see whether they show a wall cut at all. Also check the visible hop cost (lift p99) at k1.6.
