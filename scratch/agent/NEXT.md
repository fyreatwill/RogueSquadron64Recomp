# NEXT work unit (s2875) — m5-state-arbiter-ground-truth

HYPOTHESIS-ID: m5-state-arbiter-ground-truth

## Work unit

Ask the retail oracle for ground truth on the distinct `gGameSettings` /
`mainGameLoop` state-arbiter class before adding any port instrumentation.
Use one whole-RDRAM positive-control watch plus phase-qualified watches for
the known state object `0x80130B40` and `mainGameLoop=0x8003DFA0`; drive the
validated title/hangar route and capture writer PCs, values, and phase rows.
Do not modify runtime behavior or interpret downstream audio nulls unless the
positive control and both target phases are reached.

## Competing hypotheses and discriminator

- H-arbiter-writes: retail writes the state object or enters `mainGameLoop` at
  a phase-qualified edge absent from the port, selecting a route-state lead.
- H-arbiter-equivalent: retail and port show the same writer/entry sequence,
  ruling out this state-arbiter class at the measured scope.
- H-route-invalid: the positive control fails or the port does not reach title
  and hangar, making the target rows unevaluable and requiring route repair.

The discriminator is the single retail-vs-port phase table: positive-control
count, title/hangar phase reachability, writer-PC/value histogram for
`0x80130B40`, and `mainGameLoop` entry rows. Each possible outcome selects one
hypothesis above; no downstream audio counter is interpreted on H-route-invalid.

## Exact command

    grep -n "gGameSettings\|mainGameLoop\|8003DFA0\|80130B40" tools/oracle docs PORTING-STATE.md | tail -80
    sed -n '1,220p' tools/oracle/README.md
    # Then use one new oracle recipe with the validated whole-RDRAM control,
    # title/hangar phase gates, and both state-arbiter watches.

Record the complete phase table under
`scratch/agent/s2875_m5_state_arbiter/`; use SIGKILL, run from `build/`, and
run `git diff --check` before committing.
