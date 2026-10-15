# Next work unit
HYPOTHESIS-ID: keyed-mission-route-m5-validation
Context: s4957 — hangar sweep (15 keys) never reaches a mission; 5th A leaves to the 0x6A2900 model viewer (known). Input delivery is fine.
Work unit: find what state launches a mission from the hangar. Hypotheses: H-launch-flag (campaign mission-select state var not set; set it directly via env poke) vs H-viewer-then-exit (mission starts from viewer exit/Start) vs H-needs-different-hangar-screen. Discriminator in ONE run: after reaching 0x6A2900 send Start/B/A and log origin; plus grep PROJECT-OVERVIEW/F5 docs for the function that enters mission (mission-entry PC) and check callers. Reuse scratch/agent/s4957_hangar_sweep.sh (extend the key list).
Then record a mission-phase row in docs/M5-AUDIO-PLAN.md.
