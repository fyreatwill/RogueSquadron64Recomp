# NEXT (s5664): G2 voice — who is supposed to turn the slot ring (0x801535C0) into samples at 0x801B2C60?
Fact (s5663): clip payload streams into ring in-slot; slot+0x198/+0x1210 point at 0x801B2C60 (stale heap, ASCII).
Hypotheses: H5 decode ring->0x801B2C60 never runs (native/ucode path stubbed); H4 a2=0x801B2C60 to initMusyXVoiceSlot is wrong upstream (caller math); H6 pointer is legit but only a late-filled buffer (check after several ring cycles).
Discriminator: one build, one run: log caller/derivation of a2 at initMusyXVoiceSlot; watch writes to [0x801B2C60,+0x400) and reads of the slot ring by any task (ucode DMEM loads) after init; control = ring bytes change after each PI DMA. Outcomes: writes happen -> H6; no writers + ring read by ucode -> H5; a2 derived from bogus field -> H4.
Cheaper first: grep recompiled initMusyXVoiceSlot callers for a2 derivation (offline).
HYPOTHESIS-ID: g2-voice-never-requested
