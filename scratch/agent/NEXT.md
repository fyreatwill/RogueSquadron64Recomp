# Next work unit

HYPOTHESIS-ID: m5-audio-destub

s4923: s4796-style driver gated on origin 0x006AB400, never seen; unprompted 512/0x00690400 phase at ~97 s; alive 240 s, 0 crashes, vi-fs stalled=1 at end.
Next: fix the driver gate to key on the 512-wide phase (any origin) as the press trigger, then press start/a and watch for a post-key phase change; N=1 run, sample counter every 10 s. Compare 512-phase origin across 3 runs first (are 0x00690400/0x006AB400 stable labels?).
Positive control: a VI phase change within 30 s of key presses.
