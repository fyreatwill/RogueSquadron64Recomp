# G1d: which texture does the title garbage rect sample? (H-up167 vs H-cache)
HYPOTHESIS-ID: g1d-widescreen
s6233: reinterpretTileRecord never fired in a w900 title run (0 [REINTERP], no positive control) -> H-fbreinterp disfavoured. Remaining: H-up167 (rect = noisy 64x32 upload hash h98bb35b7e7c80445), H-cache (hash collision).
Next: one build logging per-draw texture hash + upload id for texrects at screen x<=0x240,y>=0x2A0 (w900 title), compare to up_167. Add a positive control (force-mark all draws). Run: zsh scratch/agent/s6233_run.sh 900 log (note wrapper can exceed 10 min; run in background).
