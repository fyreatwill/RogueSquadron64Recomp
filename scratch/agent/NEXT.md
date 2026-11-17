# NEXT (s7517)
HYPOTHESIS-ID: vi-special-features-vs-hardware

First: fold s7516_fm_levels from SOAK-RESULTS if it ran (score 0 -> FM CLOSED 6 levels in CURRENT-TRUTH item 20; 1 -> read
scratch/s7516_fm_levels/out.txt BAD lines; 3 -> ctl arm L12 showed no Init ok / Start-Stop ok; 4 -> no [s7516-pak] rows).

Work unit: class FN, VI special features + osViBlack vs hardware. The game calls osViSetSpecialFeatures from 12 sites and osViBlack
from 2 (grep jal in an objdump of ../rogue_squadron64/build/roguesquadron.elf). Hardware: OS_VI_GAMMA_ON/OFF, DITHER_FILTER_ON/OFF,
DIVOT_ON/OFF, GAMMA_DITHER_ON/OFF toggle VI_CONTROL bits; osViBlack blanks the picture at the next VI. Read what ultramodern
(lib/N64ModernRuntime/ultramodern) and RT64 do with each (stored? applied to the presented image?), list the flags each game site
passes and when (front end, mission, transitions). Hypotheses: H-canon (host applies them like the VI) / H-dead (the game's values
equal what RT64 assumes anyway, e.g. gamma off) / H-live (a flag the game sets changes the retail picture and RT64 ignores it:
e.g. gamma ON expected but not applied -> darker image; osViBlack frames presented un-blanked -> flashes on transitions).
Measurement: static census + one runtime env ROGUESQ_LOG_VI_FEAT=1 (each call: flags, resulting VI_CONTROL bits, VI count) with a
planted ctl row, scorer with synthetic + mutant controls; L4 dd1 + L15 dd8 21:9 via tools/g1e_owner_quiet_arms.zsh (s7516 command in
PORTING-STATE), levels soak queued after. If H-live: compare against angrylion (which models VI gamma) on one frame before fixing.
OWNER SAVE RULE: never clear ROGUESQ_NO_SAVE_WRITE; never touch build/saves.
