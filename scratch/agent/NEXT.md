Single next work unit (s5599): queue an ASan-armed (build_asan) keyed hangar->mission hold (~5 min past mission origin 0x00690400), one run per recipe (the s5597 N=3 recipe overran the 600 s cap). Any asan.* file = new real finding: read it, name the writer, fix root cause. Control: run must log origin 0x690400 AND be alive at the end.
Do NOT queue more non-ASan first-mission holds (10/10 clean). POKE_WRAP A/B closed (s5598: no difference; default drop kept).
HYPOTHESIS-ID: m6-mission-endurance
