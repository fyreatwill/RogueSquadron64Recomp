# Next work unit (s4288): hangar-length restore A/B and WRAP_FLUSH default

HYPOTHESIS-ID: m5-audio-destub-sequence

s4287: restore-from-shadow replicated 3/3 (ODD 60 -> 0) and is default-on (needs WRAP_FLUSH=1 + S4271/S4272 shadow envs).
Hypotheses: Q1) restore also removes the hangar garbage cimg / fb-set growth (3 -> 56) and 0x130393 wipe; Q2) hangar garbage has a different writer, restore changes nothing there; Q3) WRAP_FLUSH+shadow cost hurts at hangar.
Discriminator: copy scratch/agent/s4287_default.sh, lengthen sleep to >=130 s (hangar VI 512 at ~26 s on the autopilot route used by s1949; confirm the autopilot reaches it), arms RESTORE=0 vs defaults, both WRAP_FLUSH=1; per arm count cimg events after the 512 phase and tracked-fb count (grep checkRDRAM / [fbset] lines in s4268/s4270 instruments). Positive control: arm0 odd=60 at VI 640.
Then: make WRAP_FLUSH + shadow default in the VI 640 phase if no regressions; commit with ORIGIN line.
