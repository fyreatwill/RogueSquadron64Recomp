# Next work unit: M5 Step 9f — does the audio ucode ever DMA-write into a +0x7C buffer?

HYPOTHESIS-ID: m5-audio-destub-sequence

s4207: after every audio task (exit=1), +0x7C buffers are zero in phase 4/5 (hangar 0/138065) while +0x2C sources are nonzero; phase 3 control shows +0x7C can be nonzero. Patch the live tree only (tools/apply_s42*.py, funcs_24.c; hook in lib rsp.cpp already exported); never regen.

Hypotheses:
- H-never-writes: the ucode image never DMAs DMEM->RDRAM into any +0x7C address in phase 5 (internal branch skips mixing/save).
- H-writes-zeros: it DMAs there but the data is zero (ADPCM decode/state/volume math yields zero).
- H-wrong-ptr: +0x7C is not the PCM output; the real output goes elsewhere (check where the AI-bound buffer is written).

Discriminator (one build, one run, s4207_postaud.sh): in rsp.cpp use AudioDmaProbe ranges (RDRAM write ranges per task) and intersect with the task's ring of +0x7C addresses; also record the ranges that overlap the AI-bound PCM buffer (rs64 pcm consumer source). Positive control: ranges overlapping +0x2C-style reads and any write range nonzero in phase 3.
Outcomes: no write overlaps +0x7C but writes hit another range that later reaches AI => H-wrong-ptr; no writes at all in phase 5 => H-never-writes; overlapped writes with zero bytes => H-writes-zeros.
