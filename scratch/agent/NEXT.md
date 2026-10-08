# Next work unit (s4289): hangar-reaching A/B for restore + WRAP_FLUSH default

HYPOTHESIS-ID: m5-audio-destub-sequence

s4288: AUTOPILOT route does not reach hangar VI 512 in 140 s (both arms title-only). Restore arm: odd 0, maxFbs<=4 at title; no-restore arm maxFbs 9 and died at VI 640 (single run).
Hypotheses: Q1) restore also removes hangar garbage cimg / fb-set growth 3->56 and the 0x130393 wipe; Q2) hangar garbage has another writer, restore changes nothing; Q3) WRAP_FLUSH+shadow cost hurts at hangar.
Discriminator: build a two-arm script from scratch/agent/soak_queue/done/s1949_menu_input_yield_20260818-021858.sh (probe.sh, PROBE_KEYS='6:start 11:start ... 56:start', PROBE_PHASE_WIDTH=512), per-arm build_arm dirs, arm0 ROGUESQ_WRAP_RESTORE=0, arm1 defaults, both WRAP_FLUSH=1 S4271/S4272/S4268=1. Count maxFbs and odd cimgs after the 512 phase line. Positive control: arm0 odd>0 and arm0 fb set grows.
Then: make WRAP_FLUSH+shadow default in VI 640 phase if no regressions (ORIGIN line: writer = ucode ring lap-2 overwrite, legitimate ucode data, mitigation restores bump-time bytes).
