# NEXT work unit — locate the first output/state divergence

HYPOTHESIS-ID: m5-output-state-contract-boundary

Use the qualified title pointer boundary and compare retail
`0x80001CB8`/`0x80001CC8` rows with the existing port output/state rows. Ask
the independent retail oracle first with the whole-RDRAM positive control and
the four target PCs, adding only output/state fields needed for the ordered
join. Build once and run silent and Factor 5 image arms sequentially with
explicit SIGKILL teardown.

Competing hypotheses and discriminating outcomes:

- `H-OutputStateParity`: retail and port retain the same pointer and
  output/state tuple; this closes the downstream contract at the measured site.
- `H-OutputStateDivergence`: pointers match but output or state-word fields
  differ; the first differing field selects the missing contract edge.
- `H-ContextMismatch`: retail rows cannot be joined to the port ordinal or
  callsite; the target remains unevaluable and the join key must be redesigned.
- `H-PhaseControlFailure`: the positive control or title target rows are
  absent; the run is invalid and no contract conclusion is allowed.

Expected measurement table: `(pc, s0/state_pointer, s1, pointed_word,
output_v0, output_v1, state_word, callsite)` joined to the successful receive,
with phase and arm labels. Keep waits, slots, dispatch, clear behavior, and
PCM writeback unchanged. Do not infer that message zero is corrupt. Use
SIGKILL for teardown and capture all logs under a non-dot final path.

    env tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 55 --watch-write 0x0:0x800000 --watch-pc 0x80001C98,0x80001CB8,0x80001CC8,0x80001F84 --pc-phase-log-width 0x00790400:1024 --pc-field-dump 0x80001C98,0x80001CB8,0x80001CC8,0x80001F84 --hit-cap 10000
    cmake --build build --config Debug --target RogueSquadron64Recomp
    env zsh scratch/agent/run_s3449_m5_state_tuple_context.sh
