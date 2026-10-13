# Rerun the VI640->hangar->mission key route on the default (PAUSE=4) binary; look for res=0x2C rows

HYPOTHESIS-ID: factor5-overlay-0x2c-splice

s4786: PAUSE=4 is default-on and soaked (544 s, 0 crashes). The +5808 crash that blocked the route (s4775/s4776) should no longer stop it.
Work unit: run scratch/agent/s4776_gated_menu_walk.sh (or the s4753 winctl Start/A recipe) with ROGUESQ_S4562_PAUSE unset; record whether mission origin 0x00690400 is reached and count `res=0x2C` rows / arrivals2c in dlwalk output.
Competing: (A) route reaches mission and 0x2C rows appear => splice evaluable, compare with ROGUESQ_OVL2C_DROP; (B) reaches mission, no 0x2C rows => splice ineffective, back to H2C-real-image; (C) still stalls at hangar 0x006AB400 => derive the hangar->mission trigger (s4774) instead of key mashing; (D) new crash => read pc-symbol, a different family.
Control: a hangar VI 512 phase reached in the same run is the positive control for the route; dlwalk rows firing is the control for the counter.
ORIGIN: retail ordering (s4783/s4785).
