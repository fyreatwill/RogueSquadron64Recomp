# NEXT work unit — compare title state tuples with retail context

HYPOTHESIS-ID: m5-state-pointer-clobber-boundary

Compare the repaired title `rs_free` state tuples against a like-for-like retail
call context using one new port witness keyed by `s0`, `s1`, pointed word, and
output state. Ask the independent retail oracle first with the whole-RDRAM
positive control and the four target PCs. Build once and run silent and Factor 5
image arms sequentially with explicit SIGKILL teardown.

Competing hypotheses and discriminating outcomes:

- `H-StatePointerParity`: both title checkpoints retain the same `s1` and its
  pointed word; this closes the clobber hypothesis at this scope.
- `H-PortStatePointerClobber`: the first post-receive checkpoint changes `s1`
  or the pointed word only on port; that checkpoint selects the boundary.
- `H-WrapperBoundary`: generated wrapper return differs from the first guest
  checkpoint while both guest checkpoints otherwise agree; this selects the
  host receive boundary.
- `H-StatePointerUnevaluable`: positive controls fire but the ordered join is
  missing; no hypothesis is selected and the instrument must be redesigned.
- `H-PhaseMismatch`: title checkpoints remain absent while title consumer rows
  are live; this confirms the witness is not using the title phase and requires
  another gate repair.

Expected measurement table: `(edge, s1, pointed_word, output)` joined to the
successful receive, with phase and arm labels. Keep waits, slots, dispatch,
clear behavior, and PCM writeback unchanged. Do not infer that message zero
is corrupt. Use SIGKILL for teardown and capture all logs under a non-dot final
path.

    cmake --build build --config Debug --target RogueSquadron64Recomp
    env zsh scratch/agent/run_s3449_m5_state_tuple_context.sh
