# Next work unit (s4296): find which b-recipe element exposes odd (S4268 vs 1024-width phase-relative keys), then reach 512 with it

HYPOTHESIS-ID: m5-audio-destub-sequence

s4295: odd control works in recipe b (RESTORE=0 odd=60, RESTORE=1 odd=0) but b never reaches 512; recipe a reaches 512 but odd=0 in both arms (SPIN_YIELD/Y8000 and seeded saves exonerated).
Hypotheses: H1) S4268 exposes odd; H2) PHASE_WIDTH=1024 + KEYS_FROM_PHASE key timing exposes odd (the 640 stage dwell differs); H3) odd is only counted before a threshold the a-route passes too fast.
Discriminator: RESTORE=0 arms only, three concurrent: a+S4268; b without S4268; b with keys extended (add 18:start 22:start 26:start) and PHASE_WIDTH=512 gating. odd>0 and 512 reached = the control for the hangar A/B.
