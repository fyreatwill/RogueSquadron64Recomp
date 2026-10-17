# Next: identify what 0x9DEAC is and why ctlB keeps moving
HYPOTHESIS-ID: m6-mission-input
Result s5076: stick reaches game (0x130B8B=7F), gate 0x130B56=0, floats at 0x9DEAC change only around key windows (static in ctlA/ctlC). H1 holds, single run.
Unit: second line of evidence. Statically find writers of 0x8009DEAC in RecompiledFuncs (grep the constant/offset), name the object (player ship position?), and repeat s5076 (`zsh scratch/agent/s5076_watch.sh`, ~320 s) with a longer ctlB (20 s) to see whether movement decays to static (momentum) or persists (free-running).
