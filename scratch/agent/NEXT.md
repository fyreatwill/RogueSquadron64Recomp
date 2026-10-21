# NEXT: G1 — why counter 1 stops at 8 (needs 21) and counter 10 never moves

Work unit: ONE build with a logger at the counter store sites (applyDatObjectiveTriggerEffect 0x80065980,
datItemSetObjectiveBooleanCount 0x80065914, updateNpcEffectIntensity 0x800F3D64, executeActorType1Effect 0x800F435C,
increaseObjectiveCount 0x800C75EC): print idx, delta, new value, ra, wall time (put it in a tools/apply_s58xx_*.py
and the fixup vendored script). Also dump the lv0 DAT items whose target idx is 1 or 10 (count, trigger type).
Run g1_inv1.sh with the lever on (600 s). Positive control: counter 1 must log 1..8.
Hypotheses: H-supply (only 8 sources exist before a later trigger); H-trigger (autopilot never enters a trigger
volume/waypoint); H-port-spawn (port fails to spawn/count items). Discriminator: DAT item total targeting idx 1 —
==8 selects H-supply, >=21 with unspawned ones selects H-trigger/H-port-spawn. Also verify 800C7D98(4) is requestMissionTransitionMode.

HYPOTHESIS-ID: g1-mission-progression
