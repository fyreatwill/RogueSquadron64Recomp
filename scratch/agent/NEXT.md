# Next: who writes 0x80130C54 / 0x80130C58 (inputs of the 0x9DEAC lerp) and what drives the 0x80045618 compare
HYPOTHESIS-ID: m6-mission-input
Result s5078: 0x9DEAC = per-frame lerp of floats at 0x80130C54/0x80130C58 (arm 0x80045658) or copy of 0x80130C58 (arm 0x8004562C); arm flips with W/D/momentum; 0x800448B0, 0x8004567C never fire.
Hypotheses: Hin (0x130C54/58 are written by stick-reading code, e.g. through the 0x80130B88 stick struct) vs Hmom (written by ship-velocity/throttle integrator, stick only indirect).
Unit: extend apply_s5078 census range to 0x80130C40..0x80130C70 (physical 0x130C40..0x130C70) AND log lwc1 sources of the c1cs compare operands at 0x80045618; rerun s5078_watch.sh once (copy to s5079). Positive control = the stick struct 0x130B88 bytes still change in W and census lines appear. Discriminator: writers fire only in W/D windows (Hin) vs every frame (Hmom).
Note: after touching RecompiledFuncs, `touch src/main/register_overlays.cpp` before cmake (stale .o link failure).
