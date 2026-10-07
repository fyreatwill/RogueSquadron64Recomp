# Next work unit: M5 Step 9b — at key-on normal tail, are the voice's ADPCM source bytes nonzero, and does the ucode DMA them?

HYPOTHESIS-ID: m5-audio-destub-sequence

s4203: voices ARE keyed on (entry>=22, normal_tail>=21, slot 01->02->00) in title and hangar. H-no-voices refuted.
Hypotheses: H-voice-no-decode (voice sample-source bytes in RDRAM are zero, or the DMA from them is never issued), H-mix-drop (source bytes nonzero and DMA'd, but ucode mix/envelope/volume zeroes the output).
Discriminator (one build, one run, s4203 recipe): at musyxKeyOnVoice normal tail (0x80090DE8) log the voice record's sample pointer and FNV of its first 64 bytes; in the same run log RSP-ucode DMEM input FNV for the first audio task per phase and the voice volume/envelope fields. Source zero => H-voice-no-decode (chase sample load; ties to s4163 pi_rom_to_rdram writer); source nonzero + volume field 0 => H-mix-drop. Positive control: a known-nonzero region (the 0x00C00092 source_word record) must hash nonzero.
