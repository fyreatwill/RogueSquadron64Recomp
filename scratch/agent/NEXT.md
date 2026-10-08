# Next work unit: is the 19-buffer constant-fill at phase entry also in retail? (s4241)

HYPOTHESIS-ID: m5-audio-destub-sequence

s4240: fixed reader still shows hangar n=1..19 constant -33 DC, n=20 zeros, wide-band by n=128; title n=1..3 constant but ramping.
Hypotheses: (a) retail title entry also emits constant/ramp buffers for the first N AI buffers (benign prefill); (b) retail goes wide-band immediately (port prefill is a real defect: voices start late).
Discriminator: oracle dump_ai_output at title entry, per-buffer distinct counts n=1..40 (add every-buffer stats). Compare with port title rows in scratch/agent/soak_results/s4236_hangar_stats/run1.log.
Also: grep TO_PTR audio readers for the missing ^3 (s4239 leftover).
