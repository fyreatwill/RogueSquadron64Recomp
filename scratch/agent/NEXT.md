# Next work unit (s4290): phase-relative key route to hangar VI 512, restore A/B

HYPOTHESIS-ID: m5-audio-destub-sequence

s4289: two concurrent arms delayed title to 52.7 s so from-boot Starts (6..56 s) missed; arm0 died at VI 640 (odd=60, maxFbs 14), arm1 odd=0 maxFbs=1 reached 1024 only.
Hypotheses: Q1) restore removes hangar garbage cimg/fb-set growth 3->56 and 0x130393 wipe; Q2) hangar garbage has another writer; Q3) WRAP_FLUSH+shadow cost hurts at hangar.
Discriminator: edit scratch/agent/s4289_hangar_ab.sh: PROBE_PHASE_WIDTH=1024, PROBE_KEYS_FROM_PHASE=1, PROBE_KEYS='2:start 6:start 10:start 14:start', then wait for 512 (needs width gating twice: use probe.sh in two stages or run arm1 alone first). Run arm1 alone if arm0 dies at 640 again. Count maxFbs and odd after 512 phase line; positive control: arm0 odd>0.
Then: default WRAP_FLUSH+shadow in VI 640 phase if no regressions (ORIGIN: ucode ring lap-2 overwrite, mitigation restores bump-time bytes).
