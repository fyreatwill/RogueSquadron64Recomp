# Next work unit: M5 Step 9t — why do the inputs of setVoiceModulationParams (0x8008D710 call) carry volume=0/pan=0 in the port?

HYPOTHESIS-ID: m5-audio-destub-sequence

s4221 chain (retail oracle + port hooks): record gain words <- musyxKeyOnVoice 0x80090CA4..CC8 <- voice-state +0x6E..0x74 <- musyxRenderVoiceSamples trunc(s1[0x44..0x4A]*f[0x5C]) <- computeVoiceVolumePanCoefficients (0x800940D4; vol arg sp+0, pan arg sp+0x14 are 0 in port phases 4/5) <- setVoiceModulationParams 0x800923E4 <- callers 0x8008D710 (100359/100372 retail calls), 0x8009818C, 0x80098264. s4079: port 0x8008D710 call has a1=0,a3=0 (retail nonzero, e.g. 0x004A79E0).

Hypotheses:
- H-channel-state-zero: the per-channel volume/pan state that 0x8008D6B0..0x8008D70C reads (s2,s3,s0 <- channel record) is zero because the song/sfx start path that sets channel volume (startSongSequence 0x80094350, applyNoteEventToGroup 0x800873D4) is not reached or gets zero args.
- H-scale-zero: channel state nonzero, but a master/fade multiplier in the 0x8008D6xx arithmetic is zero.
- H-other-caller: 0x8009818C/0x80098264 callers are the live ones in port and pass zero.

Discriminator (one build, one run, all arms): hooks at the three jal sites + the loads feeding 0x8008D6F4..D70C (print s2,s3,s0,s1,s6, v1, and the channel-record words they were loaded from), with a retail twin via oracle --watch-pc 0x8008D710 (prints a0..a3). Positive control: the retail twin in the same recipe must show nonzero a1. Split: channel words zero -> H-channel-state-zero (then find the writer of those words with an oracle write-watch as in s4221); channel words nonzero but a1 zero -> H-scale-zero; calls only from other sites -> H-other-caller.

Reuse: scratch/agent/s4221_gain.sh, scratch/agent/run_s4221_retail_pan.sh (watch-pc template), tools/apply_s4221_*.py (patterns).
