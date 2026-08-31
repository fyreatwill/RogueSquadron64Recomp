# NEXT work unit — locate the first port state-pointer clobber

HYPOTHESIS-ID: m5-state-pointer-clobber-boundary

Run one phase-qualified, regeneration-safe comparison of the state pointer
after `rs_free` entry and before consumer `0x80001CB8`. Ask the independent
retail oracle first using whole-RDRAM, title-origin, hangar, consumer, and
output controls. Then build once and run the silent and Factor 5 image arms
with witnesses immediately after `osRecvMesg_recomp` returns and immediately
before the existing consumer witness.

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

Expected measurement table: `(edge, s1, pointed_word, output)` joined to the
successful receive, with phase and arm labels. Keep waits, slots, dispatch,
clear behavior, and PCM writeback unchanged. Do not infer that message zero
is corrupt. Use SIGKILL for teardown and capture all logs under a non-dot final
path.

    cmake --build build --config Debug --target RogueSquadron64Recomp
    env zsh scratch/agent/run_s3446_m5_state_pointer_clobber_pair.sh
