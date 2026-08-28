# NEXT work unit (s2873) — M5-game-settings-state-arbiter

HYPOTHESIS-ID: M5-game-settings-state-arbiter

## Work unit

Use the distinct `gGameSettings`/`mainGameLoop` state-arbiter class to test the
persistent port stop at VI 640. Do not repeat the exhausted route-state table,
launch/configuration comparisons, or downstream audio interpretation.

## Competing hypotheses and discriminator

- H-settings-state: a `gGameSettings` byte differs or fails to transition on
  the port before the 640-to-512 boundary.
- H-main-loop-order: `mainGameLoop` reaches the state checks in a different
  predecessor/order than retail.
- H-input-gate: the state table is equivalent but phase-relative input is not
  delivered at the expected caller.

The discriminator is one retail-first watch table for physical
`0x130B40:0x130B70`, execution at `mainGameLoop=0x8003DFA0`, and its known
screen-handler callsites, phase-gated at title/hangar. A state-byte transition
selects H-settings-state; a changed main-loop predecessor/order selects
H-main-loop-order; equivalent state plus missing input selects H-input-gate.
If the retail table is positive but the port route remains invalid, do not
interpret downstream nulls.

## Exact command

    rg -n 'mainGameLoop|gGameSettings|0x80130B40|0x8003DFA0|VI 640|VI 512' docs src syms
    tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 50 --hit-cap 10000 --watch-write 0x0:0x800000 --watch-write 0x130B40:0x130B70 --watch-pc 0x8003DFA0 --pc-phase-log-width 0x006AB400:512 --pc-phase-log-width 0x00790400:1024 --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start > scratch/agent/s2873_m5_game_settings_state_arbiter/oracle.log 2>&1

Only after the oracle whole-RDRAM control and target phases qualify, batch the
selected port instrumentation into one Debug build and run both audio arms
concurrently with `PROBE_PHASE_WIDTH=512 PROBE_KEYS_FROM_PHASE=1`. Record the
state table and phase-gated outcome under
`scratch/agent/s2873_m5_game_settings_state_arbiter/`.
