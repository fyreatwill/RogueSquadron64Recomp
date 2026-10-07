# Next work unit: M5 Step 9/10 gate — does nonzero PCM exist at AI source / callback / SDL on title+hangar?

HYPOTHESIS-ID: m5-audio-destub-sequence

s4200 closed Step 6/A13 as dormant on title+hangar (drain never entered; gate now actually wired into full fixup — a regen must keep `apply_s1993_drain_inloop_gate()` at the end of fixup_game_funcs.py). Steps 7/8 are effectively closed (A14/A9/A10 never fire). Remaining: Steps 9 (CPU-side MORT) and 10 (AI/SDL).
Hypotheses: H-pcm-zero-at-source (guest never produces nonzero PCM -> Step 9: MORT/voice-matrix gap); H-pcm-lost-host (nonzero at AI source, zero/different at callback or SDL -> Step 10); H-pcm-clean (nonzero and identical at all three -> audio path de-stubbed on title+hangar; update plan, move to M3 idiom audits).
Discriminator: one run (title+hangar, copy scratch/agent/s4200_drain_tick_ab.sh single arm) logging, per AI buffer: address, sample count, hash, nonzero span at AI source, callback consumer, SDL queue. First check docs/M5-AUDIO-PLAN.md Step 10 and grep existing `[m5-audio-drain-raw]` logs — they may already carry the three joins. Positive control: a synthetic nonzero buffer injected at the source must show at all three points.
