# Next work unit

HYPOTHESIS-ID: oracle-poke-mission-entry

Premise (s4722 unblock, route 3): the block assumed mission entry needs an owner-supplied input recipe or savestate. Not proven. The oracle reliably reaches the retail hangar (38 s, VI 512 @0x6ab400) and loads/saves savestates, and Start/A there only reach the model viewer. Untried: force the transition by writing game state instead of pressing buttons.
Unit (no owner input needed):
1. Statically read runHangarSelectionFrame (find via syms/rogue_squadron.syms.toml and N64Recomp/RecompiledFuncs) and the menu-overlay mode dispatcher (menuOverlayInit jump table) to find the global that selects the next mode, and the path that reaches initMission (0x800FA250) / loadLevelAssets (0x800453C8).
2. Add an oracle option `--poke ADDR:VAL` (bounded RDRAM word write once the 512 hangar phase is reached) in tools/oracle/rs64_oracle.c; positive control = read-back of the word plus the VI width/origin change.
3. Run once: if initMission/runInMissionFrame PCs fire (--watch-pc), the block is refuted; take the PC trace and revisit CURRENT-TRUTH Next steps #2.
If step 1 finds no single selector global (state set only by multi-field menu logic), record that and re-escalate with that specific negative.
