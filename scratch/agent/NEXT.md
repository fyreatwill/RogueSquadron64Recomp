# Next: run the RDRAM snapshot discriminator (unblocked s5072)
HYPOTHESIS-ID: m6-mission-input
Run `zsh scratch/agent/s5069_mission_snap.sh` (now uses ROGUESQ_PAD_OVERRIDE_FILE, no winctl). Check keys.log/padlog shows edges at key windows before trusting snapshots.
Offline: words with ctl1==ctl2==ctl3 but != keyW/keyD/keyZ = state witnesses. Positive control: frame-counter-like words differ ctl1 vs ctl2. H1 = witnesses exist; H2 = none.
