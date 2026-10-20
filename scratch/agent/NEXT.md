# NEXT: G1 - name the index source of the level-init callback table
Context: s5696 showed gCurrentLevel=1 in every mission phase (lv2_* handlers = level index 1); win poke replays it.
Hypotheses: H1 table indexer reads gCurrentLevel (0x80130B70) directly; H2 it reads B40 (0x80130B40) copied by initMission; H3 it reads a save/progress word via applySaveSlotToMissionState.
Discriminator (offline): in RecompiledFuncs, find who computes the address of ROM table 0x10B050 (lv2 init at 0x80101D10 region / lvF 0x80107EB0) and which global feeds its index; then one soak logging that global + a poke arm of 0xE (control: default arm reads 1 and still loads lv2 handlers via [hreg]).
HYPOTHESIS-ID: g1-level-select
