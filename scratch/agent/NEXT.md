# Next work unit

HYPOTHESIS-ID: m5-task-family-retail-compare

s4870 result: chunk-loop bound = AI-ring index delta per synth entry (retail +2, port +1; cap 3 never binds). Writer of byte 0x801496F0 = runAiAudioStreamPlaybackLoop (funcs_23.c 0x8008EE6C), +1 per value-1 message from queue 0x80149670 (arg -0x6990, osRecvMesg 0x800331D0).
Hypotheses: (H-P) port posts one AI-done message per synth wake, retail posts two (AI interrupt per 0x300-byte buffer, synth wakes on a coarser tick); (H-W) same message rate but the port's synth is woken twice as often per message (extra wake source / double registration, cf. musyxSynthFrame registered twice, s4762-s4772); (H-Q) port drops/coalesces a message.
Discriminator: count in ONE run on both sides: value-1 messages received at 0x8008EE44 (retail watch-pc 0x8008EE44 + synth entry 0x8009123C, same phase gate) vs synth entries. Retail ratio 2:1 -> if port is 1:1 with fewer messages -> H-P/H-Q (find poster via exec-prev/prev_pc in retail, and the port's AI shim); if port messages == 2x entries -> H-W.
Reuse: tools/apply_s4872_bound.py pattern, scratch/agent/s4872_oracle_bound.sh (swap --watch-pc 0x8008EE44,0x8009123C).
