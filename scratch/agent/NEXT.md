# Next work unit

HYPOTHESIS-ID: m5-task-family-retail-compare

AUTHORIZED (no human approval needed; see UNBLOCK.md). data_size is the frame-batch counter at 0x80149760 (musyxBuildVoiceCommandList resets at 0x8009106C / increments at 0x800911DC; musyxSynthFrame stores it at 0x80091784 -> OSTask+0x34). Do one build carrying a phase-gated trace of those two writers plus musyxSynthFrame entry timestamps, ROGUESQ_S4562_PAUSE=0 vs 4 in the same run set, plus the oracle exec watch at 0x80091784 (OSTask+0x34, NOT +0x24) with a whole-RDRAM positive control. Equal build-to-submit cadence with different counts => guest state differs; counts track cadence => cadence only, close the thread, mark M5 closed, then take the rename sweep / VI-640 route wall. Unchecked alternative: s4561/s4562 synth-pause patches changing batching.
