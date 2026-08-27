# NEXT work unit (s2609) — hangar 0x80094648 store value vs PCM

HYPOTHESIS-ID: m5-hangar-pcm-writer

## Single work unit

s2608 made the guest C88 store the default. Title PCM n=0..18 is `nz=768`
(positive control). Hangar PCM stays `nz=0` even though the gate is `0x01`
and `startSongSequence` reaches `L_80094640` (56× `0x80094664` in hangar).
Retail s2583 wrote hangar `0x141AD0` from PC `0x80094648`. That instruction
is `sb $a2, 0x1AD8($at)` immediately before the logged branch, so it ran;
the stored `$a2` and dest are unlogged because s2586 only tags branch PCs.

Do not full-regen. Add one store-site row at `0x80094648` (dest, `$a2`
requested/stored) to the existing writer table in the live
`startSongSequence` body and the matching fixup. Do not change C88, ED48,
or any other gate writer.

ORIGIN if any store/guard changes: writer is `startSongSequence` at
`0x80094648`; legitimacy is the retail hangar write at this PC.

## Competing hypotheses and discriminator

- `H-HangarStoreZero`: hangar `0x80094648` stores 0 while title stored
  nonzero. Hangar song loop is live but the channel byte is empty.
- `H-HangarStoreNonzeroNoPcm`: hangar stores nonzero (retail-shaped dest
  near `0x80141AD0`/`0x80141AD8`) while sampled PCM buffers stay `nz=0`.
  The mix/output join is the gap, not the song store.
- `H-HangarStoreUnlogged`: the new store row still does not fire despite
  `0x80094664` branches in the same function. The matcher missed the
  s2190-wrapped `MEM_B` form.

The discriminator is one rebuilt image, one AUTOPILOT hangar run under the
new C88 default (unset). Require title `1024 @ 0x00790400` with PCM
`nz=768` and hangar `512 @ 0x006AB400` before reading 94648 dest/value.
Optional same-build rollback `ROGUESQ_M5_C88_VALUE=0` must show 0 song and
0 94648 stores (negative control).

## Exact checks

1. `python3 tools/check_jr_t9_host_return.py` and
   `python3 tools/check_c88_default_store.py` still pass.
2. In `../N64Recomp/RecompiledFuncs/funcs_25.c` at `0x80094648`, log dest
   (`ADD32(ctx->r1, 0x1AD8)`), `$a2` (`ctx->r6`), and post-store byte,
   phase-gated, first 8 plus every 16th. Mirror that in
   `../N64Recomp/fixup_game_funcs.py` so regen keeps it. Do not use
   `ROGUESQ_LOG_ALL` or `ROGUESQ_LOG_SUBMIT_GATE_STORES` (that probe is
   phys-range filtered to `0x11A89F`).
3. Rebuild Debug `RogueSquadron64Recomp` only (no N64Recomp regen).
4. From `build/`, ROM present, 90s SIGKILL, shared flags as s2608
   (LLE_FORCE/SPIN_YIELD/LLE_UNGATED/LLE_SOLO, writer/gate/PCM/audio-return/
   B40-writer, hangar AUTOPILOT, STOP_WIDTH=512). Logs:
   - default unset → `scratch/agent/s2609_m5_hangar_94648.log`
   - optional rollback `ROGUESQ_M5_C88_VALUE=0` →
     `scratch/agent/s2609_m5_hangar_94648_rollback.log`
5. Per title/hangar: 94648 dest/value/count, C88 stored, gate, song /
   `0x80094664`, PCM `nz`, crash/abort. Title PCM `nz=768` is the control
   that the new 94648 logger is not required to explain silence.
