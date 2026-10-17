# Next: (BLOCKED s5071 until keytest shows a padlog press edge) run the RDRAM snapshot discriminator
HYPOTHESIS-ID: m6-mission-input
First: `zsh scratch/agent/keytest.sh` must print a padlog transition (key injection alive). If not, BLOCKED (ask owner to wake/unlock display).
Then: `zsh scratch/agent/s5069_mission_snap.sh`; offline: words with ctl1==ctl2==ctl3 but != keyW/keyD/keyZ = state witnesses. Positive control: frame-counter-like words differ ctl1 vs ctl2. H1 = witnesses exist; H2 = none.
