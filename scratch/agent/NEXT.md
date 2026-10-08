# Next work unit: M5 Step 9p — retail vs port voice-record field compare

HYPOTHESIS-ID: m5-audio-destub-sequence

s4217: retail data_ptr block has ASCII names early + real records from task n~256 (same as port shape); content census does not diverge.

Hypotheses:
- H-records-equal: voice records (base+0x10+voice*0x50: +0x2C flags, +0x44 output) match retail at same phase => divergence is in ucode consumption/PCM output.
- H-records-differ: specific fields (flags/output ptr) differ => producer-side bug at that field.
Discriminator: retail `[audio-objects-frame]` rows (oracle already prints, see run_s3481 script) vs port ROGUESQ_AUDIO_UCODE dump of same 0x50 words, matched on phase (VI 1024 origin) and late task ordinal; compare active-voice count and first-voice words.
