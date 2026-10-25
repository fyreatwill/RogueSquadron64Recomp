# Are the wide texels written this frame or stale?
HYPOTHESIS-ID: g1d-widescreen

s6213: at the phase-4 TI hit, wide 0xAE5F20 and 0xAE6B20 hold identical non-fill words
(`00010845 008300C5 10411045 ...`); ctl 0xA6AA10 is a flat `63556355` fill. Wide pointers are
real texels. Open: are they produced this frame (phase-3 writeback / guest write) or stale?

One paired run (recipe `scratch/agent/s6213_run.sh`, ctl then wide, 12 MB, from build/, SIGKILL,
screen unlocked). Add one-shot `[g1d-tb2]` of the same 8 words at 0xAE5F20/0xAE6B20 (and 0xA6AA10 ctl)
at the first phase-3 writeback end (`[g1d-wb]`) and again at the 2nd phase-4 submission.
- H-fresh: bytes differ at wb end vs phase-4 hit or are first written in phase 4 -> real per-frame texture.
- H-stale: bytes identical at both and equal to pre-phase-3 contents -> leftover data.
Positive control: ctl 0xA6AA10 must show `63556355` at both samples. Do not patch.
