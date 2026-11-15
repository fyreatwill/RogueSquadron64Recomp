# NEXT (s7406)
HYPOTHESIS-ID: fp-corner-semantics

s7405 closed class BO (ROGUESQ_FTZ now default on). First fold soak s7405_ftz_levels if SOAK-RESULTS has it (pass: alive,
0 crash, fz1>=1, fz0=0, plant_rows>=10 per level).
Class BP: FP corner cases left after FTZ, on the game thread (tid 3).
1. Attribute the producers. With ROGUESQ_S7405_FPSR=1 the sample point is a guest block, too coarse. Add a sampling
   arm (ROGUESQ_S7406_FPATTR=1) that reads FPSR at every RECOMP function return (hook in a fixup-script-injected macro, or
   sample in the mem/lookup shim with the current guest PC from the s4584/r4300_pc wrapper) and logs the first 64 guest
   functions where UFC (FZ=0 arm), IDC (FZ=1 arm) or DZC set. Use one build and two arms (FTZ=0 / default), L5 route as in
   scratch/s7405_arms.sh.
2. Hypotheses: H-guest-math (UFC/IDC come from game float code: then IDC = lwc1 of a denormal from memory, i.e. data that retail
   would trap on, so check whether retail ever stores it), H-host-shim (IDC from host C++ on the game thread, e.g. audio or
   matrix shims: harmless), H-dz-benign (the 173 boot DZC quotients are discarded or compared the same as retail's inf).
3. Positive control: the s7405 plant (plant_ufc=1 per thread) plus a planted denormal lwc1 inside one known guest function.
