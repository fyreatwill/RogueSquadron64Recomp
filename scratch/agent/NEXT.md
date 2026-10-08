# Next work unit: read the queued s4255 wave, then name the wild-pointer writer (s4256)

HYPOTHESIS-ID: m5-audio-destub-sequence

s4255: A 0/4 vs B 1/4 crash (under-powered). Queued s4255_ab_wave.sh (4 A + 8 B); read its line in SOAK-RESULTS.md first.
If B rate >> A rate with N>=12: private DMEM is the cause -> audit what host-side state the audio thread shares (h3). If equal: the crash is not DMEM-related -> drop the flag, move to the next M5 step in docs/M5-AUDIO-PLAN.md.
Do not run more crash-rate waves by hand; add a single-instrument capture of the faulting pointer's source chain in crashed arms instead.
