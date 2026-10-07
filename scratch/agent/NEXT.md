# Next work unit: M5 Step 4j caller-side use after `0x8008D624`

HYPOTHESIS-ID: m5-audio-step4j-caller-use

Session 4084 qualified the `0x8008D624` call boundary. Retail and port
carried matching hangar inputs (`a0=0x8013D880`, `a1=0x8013D952`, pre-call
`v0=0x00800000`), and retail's `0x8008D62C` plus the port callee return both
reported `v0=0x00002000`.

Competing hypotheses:

- Hcaller-use: the matching return is transformed differently in the port
  between `0x8008D62C` and the `$s3` update at `0x8008D63C`.
- Hcaller-input: the caller's live `$s3`/other state differs immediately after
  the return, before the shift/bias/clamp sequence.
- Hnext-callsite: the whole `0x8008D624` path matches, and the earlier
  `0x8008D5FC` call remains the source of the separate `0x8008D610` split.
- Hcoverage: either arm misses whole-RDRAM, title, or hangar controls.

Discriminating measurement: batch one regeneration-safe witness for the
post-call values at `0x8008D62C`, `0x8008D630`, `0x8008D634`, `0x8008D638`,
and `0x8008D63C`, including `$s3`, `$v0`, and phase/route identity. Retail
must watch the same PCs with `--watch-pc`; the port must log the same fields.
Hcaller-use selects a first retail/port mismatch in this sequence; matching
rows select Hnext-callsite. Hcoverage rejects the run.

Preparation before building:

1. Extend `/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`
   and `src/main/upstream_compat.cpp` with one phase-scoped post-call witness;
   apply the regenerated-equivalent patch to `RecompiledFuncs/funcs_23.c`.
2. Build once:
   `cmake --build build --config Debug --target RogueSquadron64Recomp`
3. Run the fixed control-first recipe shape in
   `scratch/agent/run_s4083_m5_predecessor_arithmetic_fixed.sh`, with retail
   `--watch-pc 0x8008D62C,0x8008D630,0x8008D634,0x8008D638,0x8008D63C`
   and the isolated direct-AUTOPILOT port arm. Capture under a new
   `scratch/agent/s4085_*` directory. Kill with SIGKILL and reject any arm
   missing the whole-RDRAM/title/hangar controls.
