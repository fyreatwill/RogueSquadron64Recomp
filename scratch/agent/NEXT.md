# Next work unit

HYPOTHESIS-ID: m5-task-family-retail-compare

s4868: retail producer 0x8008EE6C = 1.91/synth entry, port 0.51 (H-A refuted). Build loop (0x80091034, bound s2 = a1 loaded 0x8009132C from halfword array -0x68F0+2*(buf^1)) runs ~2 iterations retail, ~1 port. a1 is written by the voice-array walk 0x80090E04 (sh at 0x80090F24/0x80090FE8).
Hypotheses: (H-V) port voice list has 1 active entry where retail has 2 (audio-state divergence upstream, e.g. a sound effect/stream voice never allocated); (H-W) same voices but port 0x8008FFAC (per-voice command add) drops/merges one; (H-X) a1 identical but loop exits early.
Discriminator: retail oracle `--watch-pc 0x80091084,0x80090E04,0x80090F00` (v0 at 0x80091084 = a1; whole-RDRAM control first) histogram of a1, vs port log of ctx->r18&0xFFFF at 0x80091084 and the s0 count / jal 0x8008FFAC hits per 0x80090E04 call. Same a1 (2 vs 2) -> H-X; a1 1 vs 2 with equal 0x8008FFAC hits per voice -> H-V; fewer 0x8008FFAC hits -> H-W.
Use apply_s4870_producer.py as the template (helper only in one file; a second copy gives a duplicate-symbol link error). Do not retry ra logging (r31 = 0 in the port).
