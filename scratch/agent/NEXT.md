# NEXT work unit — locate the first port state-pointer clobber

HYPOTHESIS-ID: m5-state-pointer-clobber-boundary

Session 3445 selected `H-PortStatePointerClobber`: both port arms entered
`rs_free` with `s1=0x80194B20` and pointed word `0x80194B40`, then the
post-receive consumer saw `0x801Bxxxx` and output `0x2`.

Competing hypotheses and discriminator:

- `H-StatePointerParity`: all checkpoints retain `0x80194B20`; the clobber
  hypothesis is closed.
- `H-PortStatePointerClobber`: the first port-only checkpoint changes `s1` or
  its pointed word before the consumer.
- `H-WrapperBoundary`: the first change occurs only across the host receive
  wrapper.
- `H-StatePointerUnevaluable`: controls fire but no ordered checkpoint join is
  obtained.

The measurement is one phase-qualified table `(edge, s1, pointed word,
output)` joined to the successful receive. Ask retail first with the existing
whole-RDRAM, title-origin, hangar, and consumer controls. Then add
regeneration-safe port witnesses immediately after `osRecvMesg_recomp` returns
and immediately before the existing consumer witness. Build once and run both
silent and image arms concurrently. Keep waits, slots, dispatch, clear
behavior, and PCM writeback unchanged.

    cmake --build build --config Debug --target RogueSquadron64Recomp
    env zsh scratch/agent/run_s3446_m5_state_pointer_clobber_pair.sh
