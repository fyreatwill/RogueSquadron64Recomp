# Next work unit (s4301): does retail's teardown at guest pc 0x80095D54 (inside the merged waitForAnyAudioSlot body, called from menuOverlayInit) unregister the synth VI callback before the five rs_frees?

HYPOTHESIS-ID: m5-audio-destub-sequence

State (s4300): free of 0x8017D910 attributed (rs_free <- waitForAnyAudioSlot+2432 <- menuOverlayInit+14480, pc 0x80095D54), yield-independent. Hypotheses left:
- H-teardown-incomplete: guest code around 0x80095D54 removes the synth callback before freeing, and a port stub/gate skips it.
- H-retail-same: retail frees with the callback live and relies on state we lack.
Discriminator: read the recompiled code just before 0x80095D54 (RecompiledFuncs in ../N64Recomp) for the 5 frees and any call to the vi-callback unregister (slot 0x8009123C) or musyx shutdown; then confirm against retail with tools/oracle (write-watch on 0x8009123C, positive control first). If a skipped step is found, name the stub (iron rule 11) before any guard.
