# NEXT (s5670): is dialogue audible? Compare speech-slot PCM and residual noise vs retail
Facts (s5669): AI PCM has 0 rail samples post-fix (330 rows); speech clips enqueue (6) and voices allocate (6). Instrument: [pcm-noise] in main.cpp.
Hypotheses: H-a speech PCM reaches AI ring audible (non-silent bursts coinciding with enqueueSpeechClip); H-b speech voice allocated but output silent (volume/pan/mix zero); H-c residual hiss from lower-level quantization (hf_ratio higher than retail).
Discriminator: one run logging, per enqueueSpeechClip, mean_abs of AI callbacks in the following ~3 s vs the 3 s before (positive control: music mean_abs>0 already); plus retail oracle hf_ratio of title music via tools/oracle for H-c.
HYPOTHESIS-ID: g2-voice-never-requested
