# NEXT (s5674): isolate speech PCM (not just loudness)
Facts (s5673): speech enqueue windows 1.9-4.6x louder at AI output on the new cadence; callers fire. Loudness is confounded with music/SFX.
Hypotheses: H-e1 speech PCM is intelligible (decode of voice-slot pre-mix output looks like speech: low zero-crossing rate, bandlimited); H-e2 it is loud but garbage (rail/noise); H-e3 intelligible but masked/ducked in final mix.
Discriminator: dump the speech voice's decoded PCM (slot 0x80153420 output / ring at +0x198) for ~2 s after an enqueue, write WAV, compute spectrum offline; compare to SFX voice dump as control. If owner reports dialogue audible, close G2 and move to G1.
HYPOTHESIS-ID: g2-speech-audible
