# NEXT work unit — qualify the title-1024 state-pointer join

HYPOTHESIS-ID: m5-state-pointer-clobber-boundary

Run one phase-qualified, regeneration-safe comparison of the state pointer
after `rs_free` entry and before consumer `0x80001CB8`, with witnesses enabled
for title 1024 origins `0x00790400`/`0x00790800` as well as hangar 512 origins
`0x006AB400`/`0x006AB800`. Ask the independent retail oracle first with the
whole-RDRAM positive control and the four target PCs. Then build once and run
silent and Factor 5 image arms; run sequentially if concurrent startup repeats
the discarded pre-phase scheduler crash.

Competing hypotheses and discriminating outcomes:

- `H-StatePointerParity`: both checkpoints retain `s1=0x80194B20` and its
  pointed word; this closes the clobber hypothesis at this scope.
- `H-PortStatePointerClobber`: the first post-receive checkpoint changes `s1`
  or the pointed word only on port; that checkpoint selects the boundary.
- `H-WrapperBoundary`: generated wrapper return differs from the first guest
  checkpoint while both guest checkpoints otherwise agree; this selects the
  host receive boundary.
- `H-StatePointerUnevaluable`: positive controls fire but the ordered join is
  missing; no hypothesis is selected and the instrument must be redesigned.
- `H-PhaseMismatch`: 512 checkpoints and 1024 consumer rows remain disjoint;
  this confirms the prior measurement is not a title-boundary test and requires
  a phase/ordinal join redesign.

Expected measurement table: `(edge, s1, pointed_word, output)` joined to the
successful receive, with phase and arm labels. Keep waits, slots, dispatch,
clear behavior, and PCM writeback unchanged. Do not infer that message zero
is corrupt. Use SIGKILL for teardown and capture all logs under a non-dot final
path.

    cmake --build build --config Debug --target RogueSquadron64Recomp
    env zsh scratch/agent/run_s3447_m5_state_pointer_title_join.sh
