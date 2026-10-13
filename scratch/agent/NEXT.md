# Retail ordering around the musyxNoopStub teardown: what does retail do between the free burst and the gate clear?

HYPOTHESIS-ID: factor5-overlay-0x2c-splice

s4782: the free burst is musyxNoopStub -> waitForMusyXAudioTaskDone (8/8 in retail, 85 s driven), NOT shutdownAudioEngine. Port crash at musyxSynthFrame_s4562_impl+5808 follows a freed-then-reused arena. Hypotheses: A) retail's synth is paused/returns early in that window (gate/flag in musyxSynthFrame reads 0x800A0F50 or a countdown) and the port's synth ignores it; B) retail re-allocs the same blocks before the next synth tick (no gap); C) retail synth does run on freed memory harmlessly because the 73728 alloc (loader) happens elsewhere/later.
Discriminator: oracle write watches (physical) on gate 0x800A0F50 and exec watch on rs_malloc, ordered against musyxSynthFrame hits (0x8009123C) inside one musyxNoopStub window (0x8008ED00..0x8008ED44); compare in port the count of synth ticks between spin-exit and gate clear (ROGUESQ_S4562_PAUSE=1/2 already crashes, so it is NOT the answer). Control: whole-RDRAM watch must fire.
Do NOT add a guard until the writer/ordering is named (ORIGIN rule).
