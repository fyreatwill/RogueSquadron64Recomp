# Next work unit: M5 Step 9c — is the zero PCM made in the guest-built audio command list, or inside the ucode?

HYPOTHESIS-ID: m5-audio-destub-sequence

s4204: every key-on has nonzero source bytes (p28/p2c/p40, 55-64/64 nonzero; ctl_nz=n; src_zero=0) in title+hangar. H-voice-no-decode refuted at the guest-bytes edge.
Do NOT regen N64Recomp (full flow broken, see CURRENT-TRUTH s4204 REGEN WARNING). Patch the live tree with tools/apply_s*.py scripts only.

Hypotheses:
- H-list-silent: the guest (musyxMixActiveVoices / synth frame) builds an audio command list whose mix/volume/resample ops carry zero volume or never reference the voice buffers (guest-side drop; includes musyxMixActiveVoices not iterating the keyed voices).
- H-ucode-drop: the command list is well-formed (nonzero volumes, DMA of the p28/p2c/p40 sources) but the ucode image/HLE path zeroes or never DMAs (ties to F5 ucode / s4163 pi_rom_to_rdram).
- H-p-not-samples: p28/p2c/p40 are not sample data (e.g. envelope/codebook tables), so "nonzero source" proves nothing about samples — first identify them (cheap: read musyxRenderVoiceSamples / filterVoiceSampleBlock use of s1+0x24/28/2C/40).

Discriminator (one build via a new tools/apply_s4205_*.py on the live tree, one run, s4204 recipe = scratch/agent/s4204_voice_src.sh):
1. Offline first (no run): read generated musyxRenderVoiceSamples / musyxMixActiveVoices to map which s1 fields feed the list and whether p28/p2c/p40 are sample/codebook (settles H-p-not-samples).
2. Then in musyxMixActiveVoices log per phase: voices visited, per-voice volume/step fields written into the list, and a dump of the first 3 audio-task command lists (words) at task submit. Positive control: a pre-existing nonzero list word region (task header) must hash nonzero.
Outcomes: list volumes 0 / voices skipped => H-list-silent (chase the zeroing writer, ORIGIN rule 11); list has nonzero volumes + sample DMA => H-ucode-drop (compare against GLideN64 F5 ucode semantics, docs/F5-UCODE-REFERENCE.md).
