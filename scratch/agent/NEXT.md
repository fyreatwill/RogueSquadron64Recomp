# NEXT work unit (s2608) — restore the guest C88 store as the default

HYPOTHESIS-ID: m5-c88-default-store

## Single work unit

s2607 selected `H-C88ForceZeroBlocksGate` on the restored hangar route:
`ROGUESQ_M5_C88_VALUE=1` stores the guest `0x01` at `0x8008EC88`, the gate
becomes nonzero, `startSongSequence` / `L_80094640` run, and title PCM is
briefly `nz=768`. Retail s2583 wrote `0x01000000` at `0xA0F50` from this PC.
Land M5 plan Step 4's one-writer change: invert the hatch so the default
store is the guest value.

Do not full-regen (cache 0x0D). Edit the live generated store and the
fixup replacement together. Do not touch ED48 (`sb $zero` is a disable).

ORIGIN for the change: writer is `reapplyDisplayMode` at `0x8008EC88`;
the guest requested value is `0x01`; retail post-store at this PC is
`0x01000000`; the force-zero is a port hatch, not a legitimate game store.

## Competing hypotheses and discriminator

- `H-DefaultMatchesEnvArm`: after the invert, unset (new default) reproduces
  the s2607 C88=1 table: title/hangar reached, C88 stored 1, gate 1, song
  / `L_80094640` live, title PCM `nz=768` then silent, hangar PCM `nz=0`.
  The `=0` rollback arm reproduces s2607 control (stored 0, gate 0, no song).
- `H-DefaultRouteAbort`: compiling store-guest as default dies before
  title/hangar, so the env arm is not a compiled-default equivalent.
- `H-HangarPcmFollows`: default store-guest makes hangar PCM nonzero in
  the same run (title PCM remaining the positive control).

The discriminator is one rebuilt image, two concurrent AUTOPILOT hangar
arms: default (unset) vs `ROGUESQ_M5_C88_VALUE=0`. Require title
`1024 @ 0x00790400` and hangar `512 @ 0x006AB400` before reading writers.

## Exact checks

1. `python3 tools/check_jr_t9_host_return.py` still passes.
2. In `../N64Recomp/fixup_game_funcs.py` invert the `0x8008EC88` replacement
   so unset stores `ctx->r2` and env `0` stores `0`. Apply the same invert
   to the live line in `../N64Recomp/RecompiledFuncs/funcs_23.c`.
3. Rebuild Debug `RogueSquadron64Recomp` only (no N64Recomp regen).
4. From `build/`, ROM present, both arms at once, 90s SIGKILL, same shared
   flags as s2607. Logs:
   - default unset → `scratch/agent/s2608_m5_c88_default.log`
   - rollback `ROGUESQ_M5_C88_VALUE=0` → `scratch/agent/s2608_m5_c88_rollback.log`
5. Per arm and per title/hangar: C88 requested/stored, gate byte, song /
   `0x80094664`, PCM `nz`, crash/abort. Default must match s2607 C88=1;
   rollback must match s2607 control. Do not change ED48 or any other gate
   writer this iteration.
