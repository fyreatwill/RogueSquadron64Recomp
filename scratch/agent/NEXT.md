Single next work unit (s5643): fold s5642_aloc_{a,b} (grep '\[aloc\]\|\[speech\]' scratch/agent/m6/<tag>/run.log). Control: [speech] playSpeechClip lines + [spath] allocAndConfigureNewVoice present.
H-C1 entry cnt<=a0 (0x80154670 count too small vs clip id 0x1C4/0x5E) -> alloc bails at B0A8: find who writes 0x80154670 (MusyX voice pool never sized => audio-disabled artifact; M5 de-stub target).
H-C2 cnt ok, all u0..u3 nonzero / reach_B1F4 absent -> pool-full bail at B0D8.
H-C3 reach_B1F4 and B220 fire -> voice started; look downstream (ucode PCM, retail-oracle voice compare).
H-C4 label_B230 without reach_B1F4 and cnt ok -> first gate (B094, $v0 from prologue) bails; read prologue.
HYPOTHESIS-ID: g2-voice-never-requested
