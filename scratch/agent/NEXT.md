# Next work unit

HYPOTHESIS-ID: H-alloc-window-sched-switch

s4711 result: all 7 port allocateSongChannelArray calls go via initN64RspMixer (its only caller). Retail boot/attract: initAudioSubsystem (0x80091B3C) -> initN64RspMixer once; reapplyAudioConfig (0x80091C88) and reapplyDisplayMode (0x8008EB5C) 0 hits in 120 s (control fired).
Hypotheses: (A) port reaches reapplyDisplayMode->reapplyAudioConfig on each display-mode change and retail does too past attract (unobserved); (B) port-only: our setDisplayMode/reapplyDisplayMode gate handling (B40, 0x800A0F50, bytes 0x80141AD0/1) makes the game re-init audio where retail skips; (C) a repeat initAudioSubsystem call.
Unit: one port build with entry prints in reapplyAudioConfig / initAudioSubsystem / reapplyDisplayMode (host fprintf, with width/origin) and the guest caller ra of reapplyDisplayMode; run 2 arms like scratch/agent/s4711_callers.sh. Discriminator: entry counts of reapplyAudioConfig vs initAudioSubsystem between allocs (A/B vs C), and the guest caller of reapplyDisplayMode per alloc. Then read retail disassembly of reapplyDisplayMode (0x8008EB5C) for the condition that would skip the audio re-init.
Note: the s4711 entry hook shows ra=0 because the call site runs the hook before the jal sets r31; print ra from inside the callee's first line instead.
