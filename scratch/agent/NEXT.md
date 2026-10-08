# Next work unit (s4294): hangar A/B of ROGUESQ_WRAP_RESTORE with SEEDED saves

HYPOTHESIS-ID: m5-audio-destub-sequence

s4293: slowdown = empty saves dir in build_arm_* (seeded 1024@13.9s #765, 512@47.4s; empty 1024@46.8s). Base script: scratch/agent/s4293_save_ab.sh (copy build/saves into each arm).
Hypotheses: H1) restore keeps the hangar fb set small (maxFbs <=4 vs 10-56) and the 0x130393 wipe absent; H2) no hangar effect (garbage fb sets come from another writer); H3) restore destabilises hangar (crash earlier).
Discriminator: arms WRAP_RESTORE=1 vs =0 (both WRAP_FLUSH=1, S4271/2, cap 0x2000), same seeded save, phase-gated on VI 512 (+10 s): compare odd cimg count, max tracked fb set, crash. Positive control: =0 arm must show odd>0 as at VI 640.
Outcomes: H1 -> candidate default-on + crash soak; H2 -> name the hangar-entry writer (s4270); H3 -> revert default.
