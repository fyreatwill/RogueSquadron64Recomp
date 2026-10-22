# NEXT: G1 - s5854: are player bolts spawned at all, and what owner do they carry?
s5853: owner census over 81921 chain-loop calls with A held: playermatch=0 (plid 0x38 at 0x80137DBA never equals proj+0xF8); P tests 0. Contradicts s5833 (P 28679 tests).
Hypotheses: H4 fire handler not spawning bolts (ammo/cooldown/gate); H5 who-classifier wrong field/id (player id differs, e.g. 0x80137DBA stale); H6 s5833 P rows were mislabelled N-side.
Discriminating measurement (one build, one run): hook the projectile-spawn function (find via the object that writes +0xF8 in the chain; grep recomp funcs for stores to +0xF8 near the fire-button handler / 'audioCueDispatcherNpcHandler' callers) and log owner id + button state at spawn; also log the player object's own id word. Control: N spawns must appear. Outcomes: no spawn while A held -> H4 (read the gate); spawns with owner != 0x38 -> H5 (fix classifier, rerun s5853 probe: newmin rows will then fire); 
Run: env ROGUESQ_LOG_HITS=1 ROGUESQ_NPC_INVULN=1 zsh scratch/agent/g1_fireall.sh s5854 300
HYPOTHESIS-ID: g1-mission-progression
