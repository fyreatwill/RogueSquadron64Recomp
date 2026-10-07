# Next work unit: M5 Step 9d — does the zero PCM appear between the (populated) command list and the ucode output?

HYPOTHESIS-ID: m5-audio-destub-sequence

s4205: command-list records at the render jal are nonzero (138752/138752 in hangar); mixer visits voices. Patch the live tree only (tools/apply_s*.py); never regen.

Hypotheses:
- H-ucode-drop: list is fine; the F5 ucode HLE/LLE path never DMAs the sources or zeroes the output (docs/F5-UCODE-REFERENCE.md, s4163 pi_rom_to_rdram).
- H-list-zero-volume: records nonzero but the volume halfwords (field unidentified; read musyxRenderVoiceSamples stores to s0+0x40..0x60) are zero.
- H-p-not-samples: p28/p2c/p40 are tables, not samples.

Discriminator (one build, one run, s4205 recipe): in rs64_s4205_rec also hash the buffers at rec+0x08/+0x10/+0x40 immediately and again at the next audio task completion; log render's stores to s0+0x40..0x60 as named fields. Positive control: s1 nonzero hash.
Outcomes: volume fields zero => H-list-zero-volume (chase writer, ORIGIN rule 11); volumes and input buffers nonzero but output zero => H-ucode-drop.
