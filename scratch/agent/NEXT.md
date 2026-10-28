# NEXT: is the 64x64 terrain table the binding limit past dd4?
HYPOTHESIS-ID: g1c-dd-phase2
Fact (s6575): ROGUESQ_DRAW_DISTANCE=12 clamps to 8 (apply_s6036_dd.py:7); [ddclamp] post x[0,64) shows x saturating at tw=64.
Work unit (offline first): for the dd1/dd2/dd4/dd8 lvl1 runs under scratch/agent/m6, grep "[ddclamp]" and tabulate post-clamp footprint area (x1-x0)*(z1-z0) vs dd. If area stops growing at dd>=4 => table dims (tw/th=64) are the limit: plan enlarging them (s6035 stride notes). If it keeps growing => run dd8 vs dd4 fixed-camera sheet in-run (phase-gated) and 300 s holds on lvl 1,5,10.
Outcomes: saturation => next unit is terrain dims patch; no saturation => bundle recipe behind the single knob.
