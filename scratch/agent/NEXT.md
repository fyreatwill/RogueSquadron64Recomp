# NEXT: G1d reproduce the qualified 16:9 route and join RDP/VI at menu frames
HYPOTHESIS-ID: g1d-widescreen

s6164 parameterized g1_fly.sh's title, hangar, and mission origin gates. The fresh 4:3 control passed; fresh wide arms did not reproduce the qualified route (8 MB stopped before wide title; 12 MB stalled in phase 6). Existing s6163b evidence still shows correct wide VI transitions but garbage title/hangar dumps. Do not infer H-stride or H-menu-policy yet.

Work unit: one instrumented 12 MB 16:9 run plus 4:3 control using the qualified s6163b route recipe. Capture two consecutive title and hangar frames, and for each frame record RDP SETCOLORIMAGE width/address, scissor width, VI width/origin, and dump hash/validity. Keep all arms in the same build and phase-gate comparisons on the title and hangar VI transitions.

Competing hypotheses and discriminator:
- H-stride/VI: RDP colour-image/scissor and VI width/origin disagree at the first bad wide frame. This selects a present/readback stride or origin defect.
- H-menu-policy: RDP and VI agree, but the wide dump is already garbage while the 4:3 dump is valid. This selects a menu/hangar display-list assumption or invalid wide primitive.
- H-transition-only: the first wide dump is bad but the second consecutive dump recovers with the same RDP/VI relation. Recovery selects a transition-buffer defect; persistence refutes it.

Commands: use the existing qualified 12 MB route setup from `scratch/agent/m6/s6163b_g1d_169`, add the RDP colour-image/scissor trace to the same build, then run control and wide concurrently from `build/`; use `ROGUESQ_ASPECT=16:9 ROGUESQ_OSMEM_MB=12 TITLE_ORIGINS="0x00752200 0x752200" HANGAR_ORIGINS="0x006AB638 0x6AB638" MISSION_ORIGINS="0x00652438 0x652438"`. SIGKILL test groups after both title and hangar have two consecutive dumps. Record the exact route recipe before launching if the prior wrapper needs additional force-unlock variables.
