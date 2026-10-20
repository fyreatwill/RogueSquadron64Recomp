# NEXT (s5671): residual noise vs retail (H-c) — oracle AI PCM hf_ratio of title music
Facts (s5670): speech enqueue windows are 1.8-15x louder than control at AI output; rails 0. Remaining G2 complaint: fuzzy layer.
Hypotheses: H-c1 port hf_ratio on title music > retail (quantization/resample noise); H-c2 equal to retail (noise is perceptual/host sink, e.g. SDL rate/format); H-c3 oracle cannot give AI PCM (then compare spectrum of port AI dump to known-good decode of same music).
Discriminator: tools/oracle AI PCM capture of title music (positive control: nonzero PCM) vs port [pcm-noise] hf_ratio in title phase, same metric.
HYPOTHESIS-ID: g2-speech-audible
