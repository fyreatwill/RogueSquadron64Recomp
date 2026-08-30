# NEXT work unit — capture scheduler message identity at the call site

HYPOTHESIS-ID: vi640-maudtask-type2-writer

Session 3255's wrapper-level receive-type probe was unevaluable: `$a1` was
zero at the wrapper and the queue snapshot preceded external-message
delivery. Do not repeat that probe or infer a message type from its zero rows.

## Competing hypotheses

- `H-SpMsgMutated`: the scheduler receives the host SP-complete object
  `0x80128C70`, whose byte 0 is unexpectedly 2 at the VI-640 wall.
- `H-OtherOsTask`: a different live producer supplies a type-2 message to
  `0x8011A420`; the call-site capture names its pointer and type.
- `H-Type2AbsentAtRecv`: the scheduler receives only type 1/0x81 or another
  non-2 value; the 89F=2 stall needs a different explanation.

## Discriminator

Instrument the generated scheduler call at `0x80019CCC..0x80019CD0` (through
the regeneration/fixup path, or an equivalent host hook that records the
generated caller) so the capture records the caller, output-slot address,
message pointer after return, type byte, and `89F/28D44`. The same run must
show the existing `[recvtrace]` positive control and reach the VI-640 phase.
Type 2 with `0x80128C70` selects `H-SpMsgMutated`; type 2 with another pointer
selects `H-OtherOsTask`; no type 2 after the controls select
`H-Type2AbsentAtRecv`. If the port never reaches the required call-site phase,
report coverage invalid rather than interpreting a null.

## Exact start

First inspect the fixup/regeneration path for the existing `funcs_4.c`
diagnostic hooks, then make one bounded instrument/build. Run from `build/`:

```
env ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1 \
    ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 \
    ROGUESQ_RECV_TRACE=1 ./RogueSquadron64Recomp
```

SIGKILL at approximately 40 seconds. Preserve the full log under a path whose
final component does not begin with `.`.
