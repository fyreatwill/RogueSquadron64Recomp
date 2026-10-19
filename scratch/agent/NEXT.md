Work unit: classify objective item behind counter 0x80138064 (set via datItemSetObjectiveBooleanCount from updateDestructionDebrisNpc, threshold 3 in lv0_checkComplexObjectives). Offline: read docs/M6-OBJECTIVE-STATE-MACHINE.md + scratch/agent/objc_disasm.txt; decide whether reaching 3 means mission success or failure (e.g. what the result mode/speech 0x8010C9E0 bit0 selects).
Hypotheses: (W) win condition -> results screen is correct, M6 endurance of first mission is satisfied by completion; (L) loss/friendly-destroyed count -> autopilot loses mission, GAME OVER legit; (X) wrong counter semantics from runtime defect.
Discriminator: the success/fail branch selected after requestSpeechResponseMode2 + results screen text (fb dump s5490).
HYPOTHESIS-ID: m6-mission-endurance
