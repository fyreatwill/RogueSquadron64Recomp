# Next work unit
HYPOTHESIS-ID: voice-count-before-base-race
s4979: retail-entry boundary closed (design-dead). Port reaches 0x800903F0 only via mixer index past the 18-voice array (count stored before rs_malloc, base after; s4577/s4578).
Work unit: grep current-default soak logs (SOAK-RESULTS since s4959, mission/idle runs) for `kind=bad site=800903F0`, `count=32`, `[s4579` markers, and the `pi.cpp:112` odd-DMA abort. If zero across all default runs with the instruments armed (and a positive control line from the same logs), the race is dissolved by a later fix (ring-lap s4549?) - record which, close the thread, and pivot to M5 plan step. If hits remain, the allocator count-before-base window is real: fix at the source in a fixup script (publish count after base, or hold the mixer lock), with ORIGIN line.
Hypotheses: A race already dissolved by default fixes; B still live but rare; C instruments not armed in default soaks (null uninterpretable).
Discriminator: presence of armed-instrument control lines vs bad-site hits in the same logs.
