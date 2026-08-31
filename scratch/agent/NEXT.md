# NEXT work unit — align the retail and port output/state field schema

HYPOTHESIS-ID: m5-output-state-contract-boundary

Use the now-live retail target PCs and add one phase-scoped port witness table
with the same fields as the oracle: `s0`, `s1`, pointed/source word,
branch-selector, source byte, and branch-state. Keep existing consumer/output
fields in the same build, then run silent and Factor 5 image arms sequentially
with explicit SIGKILL teardown. The oracle baseline is
`scratch/agent/s3450_oracle_fixed.log`.

Competing hypotheses and discriminating outcomes:

- `H-FieldParity`: all mapped fields match at ordered title rows; close the
  measured output/state boundary.
- `H-FieldDivergence`: the first mapped field differs while both target PCs are
  live; that field selects the missing contract edge.
- `H-JoinMismatch`: both sides are live but phase/ordinal/callsite cannot form
  an ordered join; redesign the join key without runtime behavior changes.
- `H-PhaseControlFailure`: a positive control or title target is absent; the
  comparison is invalid and no contract conclusion is allowed.

Expected measurement table: `(pc, s0, s1, source_word, branch_selector,
source_byte, branch_state, output_v0, output_v1, state_word, callsite)` joined
to the successful receive, with phase and arm labels. Keep waits, slots,
dispatch, clear behavior, and PCM writeback unchanged. Do not infer that
message zero is corrupt. Use SIGKILL for teardown and capture all logs under a
non-dot final path.

    env tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 55 --watch-write 0x0:0x800000 --watch-pc 0x80001C98,0x80001CB8,0x80001CC8,0x80001F84 --pc-phase-log-width 0x00790400:1024 --pc-field-dump 0x80001C98,0x80001CB8,0x80001CC8,0x80001F84 --hit-cap 10000
    cmake --build build --config Debug --target RogueSquadron64Recomp
    env zsh scratch/agent/run_s3449_m5_state_tuple_context.sh
