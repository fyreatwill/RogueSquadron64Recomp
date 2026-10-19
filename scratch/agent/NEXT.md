Work unit: fold s5519_save_{base,f2,f7} from SOAK-RESULTS.md and scratch/agent/m6/<tag>/run.log.
Hypotheses: H1 route reaches applySaveSlotToMissionState and the forced save byte changes [mfst] names (save data selects mission); H2 route never calls it (no [saveslot] in base) so hook unexercised -> need hangar-route recipe (m6_wp_flag.sh style, origin 0x006AB400 gate); H3 called but content identical (selector lives elsewhere).
Discriminator: grep '\[saveslot\]\|\[mfst\]\|\[initMission\]' run.log per arm; base [saveslot] is the positive control.
HYPOTHESIS-ID: second-distinct-mission-coverage
