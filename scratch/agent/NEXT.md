# NEXT work unit — restore a valid route for the pointer-source capture

HYPOTHESIS-ID: m5-callback-indirect-pointer-source

Session 3341 added a regeneration-safe probe at the concrete port store
`0x80091900` and observed `0x80007910`, but two retries crashed in the
scheduler before target phases. Retail's requested `0x001099D4` watch passed
the positive control and remained at zero writes; the actual generated load
address is physical `0x001499D4`.

Competing hypotheses remain:

- `H-PointerWriter`: a guest writer sets the indirect callback pointer.
- `H-StalePointer`: the port's pointer is pre-existing/stale and the indirect
  call is only a consumer.
- `H-HostDispatch`: a host/runtime path supplies the pointer.

The discriminating measurement remains a same-run writer census with retail
and port arms plus whole-RDRAM positive controls, but the port route must first
reach title 1024 and hangar 512. A target-phase retail writer at the actual
physical slot identifies `H-PointerWriter`; no retail writer but a target-phase
port writer selects `H-StalePointer`; no writer in either arm with valid
indirect transfers selects `H-HostDispatch`. A null is invalid unless the
whole-RDRAM control fires.

The fixup and current generated artifact contain the port writer census. First
diagnose/restore the early scheduler crash without changing behavior; then
rebuild once and run:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    env ROGUESQ_LOG_M5_CALLBACK_WRITER=1 zsh scratch/agent/run_s3333_m5_callback_reachability.sh

The positive-control rows must include host-boundary and task-handoff controls,
and the run must reach title 1024 and hangar 512. No pointer-source conclusion
or behavioral change is authorized until the port arm is valid.
