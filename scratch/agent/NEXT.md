# NEXT work unit (s1112)

HYPOTHESIS-ID: submit-phase-route-audit

Perform one bounded, build-free static audit of the VI launch route. Find the
code that emits the 640 and 1024 VI transitions, enumerate its state/input
predicates, and compare those predicates with the key and phase-gate semantics
implemented in `tools/probe.sh`. Do not run another capture this iteration.

Competing hypotheses:

* H-route-predicate: the 1024 transition requires a concrete input/state
  predicate that the current probe schedule does not satisfy.
* H-state-lifecycle: the 640-to-1024 transition is state/overlay-driven and
  not directly controllable by the probe's key schedule.
* H-phase-observation: the runtime reaches a 1024-equivalent route, but the
  host phase logger or width transition is not observing it on this path.

Discriminator: a source-level mapping from each 640/1024 VI write to its
controlling state/input predicate and to the logger's observation point.
Finding a satisfiable missing input predicate selects H-route-predicate;
finding only lifecycle/overlay predicates selects H-state-lifecycle; finding
an uninstrumented 1024 write or logger mismatch selects H-phase-observation.

Exact commands:

```sh
rg -n -i 'vi_width|width=1024|width.*640|set.*vi|update_screen|VI_' src lib tools | head -240
rg -n -i 'PROBE_KEYS|KEYS_FROM_PHASE|PROBE_PHASE_WIDTH|keycode_for|phase' tools/probe.sh src/main
```

Read bounded source windows around the identified transition sites and record
the predicate-to-probe mapping in the next ledger entry. No build, runtime
capture, or mitigation is authorized for this unit.
