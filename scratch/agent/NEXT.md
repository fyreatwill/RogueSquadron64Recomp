# Next work unit: read s5482_phase6 (scratch/agent/m6/s5482_phase6, SOAK-RESULTS.md)
Question: after the mission-end gate, do state (0x8010CA20 -> 4 -> 6) and flags (0x8010CA1C |= 0x40) get written, and does runInMissionFrame return? What renders afterwards?
Hypotheses: (A) state reaches 6 and flags get 0x40 -> loop exits; the post-loop caller (find via bt) keeps presenting = results/unload screen; read it. (B) state reaches 6 but flags never gets 0x40 (timer not decrementing: dt f20 == 0 or tick not called) -> mission frozen in phase six; fix root cause of dt. (C) state stuck at 4 (requestSpeechResponseMode2 not reaching bit0 handler) -- contradicted by s5481 (bit0 write seen), so only if watch shows otherwise.
Discriminator: the lldb_att1.log sequence of Watchpoint hits on state/flags + per-second timer reads (0x10C9EC).
HYPOTHESIS-ID: m6-mission-end-trigger
