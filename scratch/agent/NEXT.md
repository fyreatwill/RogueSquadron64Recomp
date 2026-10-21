# NEXT: G1 — who calls setHudEnableBit4 (0x800C7738) with val 4 ~190 s into the mission?

s5785: life loss 3->2 = mtm(a0=2) after setHudEnableBit4 store (mtmst pc=0x800C775C val=4); not debris (killset=0, control ok), not reload, not the 0x64/0x65 LOSE booleans (0 at entry).
- H-script-fail: mission script fail condition (friendly lost / timer / bounds) -> discriminator: log guest caller PC (ctx r31 is 0; use the script interpreter frame / host backtrace) and dump objective booleans 0..0x70, objective counts, objective timer at the val=4 store.
- H-timer: mission time limit ~190 s -> check getObjectiveTimer (0x800C76E0) value at the store; control: the same dump at mission init must show the timer start.
- H-ours: our input/autopilot did something (e.g. fire/btn 0x8000 at t=379/385 hitting a friendly) -> compare autopilot lines 766805..766880 (btn=0x8000 at t=379) vs the s5783_noalt run (0 deaths).
Single build: extend tools/apply_s5754_mask_stores.py with backtrace + bool/timer dump gated ROGUESQ_LOG_MTM on pc==0x800C775C; queue 2 soaks (althold, noalt) of the s5777 recipe with the [terr] budget unchanged. HYPOTHESIS-ID: g1-mission-progression
