# NEXT: G1 - who writes B40 (0x80130B40) before initMission
Context: s5698 proved chain B40 -> initMission -> gCurrentLevel(B70) -> initializeObjectiveTracking jalr table[lvl*16] -> lvN init; ra=0 is a recomp artifact (generated jal never sets r31), so ra-based inference is invalid everywhere.
Hypotheses: H1 B40 comes from hangar/briefing selection state (player picks mission); H2 from save/progress word (applySaveSlotToMissionState); H3 default/zero-init + autopilot-forced value.
Discriminator: one soak with env-gated log (pc, new value, host backtrace first 3 hits) at the 5 B40 writers 0x8003E284/E4B8, 0x8006DC2C, 0x800A5E5C, 0x800C5B8C; control: initMission's own read logs B40. Then compare value vs hangar selection in the same run.
HYPOTHESIS-ID: g1-level-select
