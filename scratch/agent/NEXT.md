# Next work unit: M5 Step 9 — are any MusyX voices ever started (title/hangar), and does a started voice decode?

HYPOTHESIS-ID: m5-audio-destub-sequence

s4202: PCM content is nil: title = 19 buffers of decaying constant L/R DC, hangar = all zeros (min=max=0).
Hypotheses: H-no-voices (no voice/song start ever reaches the synth: sound API calls stubbed/never issued); H-voice-no-decode (voices allocated but sample ADPCM/DMA yields zeros); H-mix-drop (voices decode but the ucode mix/envelope zeroes them).
Discriminator (one build, one run, s4200_drain_tick_ab.sh default arm): log per audio-frame count of active voice slots (voice array at the MusyX struct, see waitForAnyAudioSlot/ slot status guards) plus count of voice-start (note on) calls, and first 8 decoded-sample words of the first active voice. 0 voices => H-no-voices; voices>0 with zero decoded words => H-voice-no-decode; nonzero decoded but zero out => H-mix-drop. Positive control: the title DC buffers must coincide with a nonzero voice/filter state.
