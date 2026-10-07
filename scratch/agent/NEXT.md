# Next work unit: M5 Step 4k next voice-modulator callsite at `0x8008D5FC`

HYPOTHESIS-ID: m5-audio-step4k-next-callsite

Session 4085 qualified the caller-side sequence after `0x8008D624`. Retail
and port match through `0x8008D63C`: post-call `v0` is `0x2000`, `0x40`, `0`,
`0` at the five instruction points, and `$s3` is updated consistently. Both
arms passed the whole-RDRAM/title/hangar controls.

Competing hypotheses:

- Hnext-return: the separate `0x8008D5FC` call returns differently and feeds
  the earlier `0x8008D610` divergence.
- Hnext-caller: that return matches, but its caller-side use diverges before
  `0x8008D610`.
- Hother-path: both call and caller match, moving the search elsewhere.
- Hcoverage: either arm misses whole-RDRAM, title, or hangar controls.

Discriminating measurement: add one regeneration-safe witness at the
`0x8008D5FC` call and its return, plus the existing `0x8008D610` arithmetic
row. Retail must watch the call/return PCs with `--watch-pc`; the port must
log matching arguments, return, and caller operands in title and hangar.
Hnext-return selects a first return mismatch; Hnext-caller selects a first
post-return operand mismatch; matching rows select Hother-path. Hcoverage
rejects the run.

Preparation before building:

1. Extend `/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`
   and `src/main/upstream_compat.cpp` with one phase-scoped witness for the
   `0x8008D5FC` call/return; apply the regenerated-equivalent patch to
   `RecompiledFuncs/funcs_23.c`.
2. Build once:
   `cmake --build build --config Debug --target RogueSquadron64Recomp`
3. Run a new `scratch/agent/run_s4086_*` control-first recipe with retail
   `--watch-pc` for the `0x8008D5FC` path and the isolated direct-AUTOPILOT
   port arm. Capture under `scratch/agent/s4086_*`; kill with SIGKILL and
   reject any arm missing the whole-RDRAM/title/hangar controls.
