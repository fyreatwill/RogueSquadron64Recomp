# Next work unit
HYPOTHESIS-ID: keyed-mission-image-vs-silent-ab
s4964: keyed mission route 3/3 valid (crash=0, PCM live). M5 steps 0-11 closed.
Unit: copy scratch/agent/soak_queue/done/s4959_mission_run1.sh to s4964_mission_image.sh and s4964_mission_silent.sh (silent sets ROGUESQ_AUDIO_UCODE=0), enqueue both, consume verdicts.
Hypotheses: H-stable-both (mission onset/crash identical -> audio is not the mission-time stability factor); H-image-regresses (image crashes/stalls, silent does not -> audio de-stub a mission hazard); H-silent-regresses (silent crashes -> degenerate path was the hazard). Discriminator: onset time, crash/abort, VI flip count per arm. Positive control: silent arm must show pcm_nz_rows=0, image arm >0.
