# Next work unit: where does the port over-scale audio gain? (s4239)

HYPOTHESIS-ID: m5-audio-destub-sequence

s4238: port title AI RMS 18.3k/2.1% clipped vs retail 1.4k/0% (oracle). Port ~13x hot.
Hypotheses: (a) master/volume field read wrong feeding the mixer; (b) voice sum missing the RSP output shift; (c) reverb/feedback accumulating without decay.
Discriminator: in the port audio ucode path (ROGUESQ_AUDIO_UCODE=1) log, for the first 20 title buffers, per-stage peak (pre-master, post-master, post-reverb) and volume params. Pre-master already hot = (b)/voice decode; only post-master hot = (a); growth over buffers = (c). Positive control: scale a buffer x2 in the logger, peak must double.
