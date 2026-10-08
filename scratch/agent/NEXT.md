# Next work unit: re-measure hangar + phase-aligned title loudness with the FIXED AI reader (s4240)

HYPOTHESIS-ID: m5-audio-destub-sequence

s4239: ai.cpp read rdram in host order (needs ^3); s4235-s4238 AI stats (DC hangar, 13x hot, clipping) were that artifact. Fixed; 876/894 title AI buffers FNV-match ucode 0x6F0/0x300 output.
Hypotheses: (a) hangar entry still shows a constant-fill transient with the fixed reader (real ring-contents-before-first-mix issue); (b) it vanishes (pure artifact, hangar audio fine); (c) port title ~3x louder than retail persists when aligned by buffer index after title entry.
Discriminator: run s4236 hangar recipe (scratch/agent/s4236_hangar_stats.sh, ROGUESQ_S4239=1 set) and read the first 40 hangar `[ai-output-stats]` rows (distinct, min/max). Constant per-channel rows = (a); wide-band from n=1 = (b). For (c): oracle `dump_ai_output` RMS vs port `[s4239-ai]` rms by n in 1-50/50-200/200-500 (retail needs the same ordering; oracle samples every 128th after 20 - add all-buffer rms there).
Positive control: title `[s4239-ai]` FNV-vs-`[s4239-out]` join must stay >95%.
Also: check other ai.cpp/oracle readers of rdram bytes (grep TO_PTR on audio paths) for the same missing ^3.
