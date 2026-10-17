# Next: what selects the 0x9DEAC arm (compare at 0x80045618) and what 0x80019444 accumulates into 0x80130C40
HYPOTHESIS-ID: m6-mission-input
Result s5079: 0x130C54/58 static during flight (no writers in any window); only 0x80019444/84/90 write 0x130C40/44/48 once per swap. Arm selection (lerp 0x80045658 vs copy 0x8004562C) flips with W/D/momentum.
Hypotheses: Hpar (compare operand is 0x130C40 accumulator vs a threshold), Hstick (compare reads the 0x80130B88 stick struct directly), Hvel (reads a ship velocity float).
Unit: static read of generated funcs around 0x80045600-0x80045660 (lwc1 operands before the c.lt/c.le branch) and 0x80019430-0x80019494; if ambiguous, add one lwc1-read census in a single build. Discriminator: which address the compare operands load from.
Note: after touching RecompiledFuncs, `touch src/main/register_overlays.cpp` before cmake.
