# NEXT work unit (s1146)

HYPOTHESIS-ID: m3-generated-boundary-anomaly

Analyze the existing s1145 trace as one bounded reachability experiment. Do
not change code or add a runtime guard. The second explicit-control attempt
again reached only VI width 640; slot dispatch was live, but all E9 controls and
the VI-1024 marker were absent.

Competing hypotheses and discriminator before the work unit:

- H1/stable phase loop: the process remains active in a repeatable VI-640 /
  dispatch state, so the boundary test is blocked by pre-phase reachability.
- H2/early execution halt: the apparent 180-second stall masks a stopped or
  non-progressing execution path, so the phase trace should show a terminal
  dispatch/phase pattern.
- H3/boundary relevance: the process does reach the target phase on a rerun;
  this is refuted if the bounded trace contains no VI-1024 or task-control E9
  marker.

Discriminating measurement: the ordered tail of phase records, the first and
last slot-dispatch records, and the process outcome in the existing log. A
continuing dispatch stream with repeated VI-640 records selects H1; a finite
tail with no later progress selects H2; either result without VI-1024/E9
controls refutes H3 for this run.

```sh
grep -n '\[phase\]' scratch/agent/next_s1145/run.log | tail -30
grep -n '\[slot-dispatch\]' scratch/agent/next_s1145/run.log | head -5
grep -n '\[slot-dispatch\]' scratch/agent/next_s1145/run.log | tail -5
grep -n '\[e9-prov\]\|\[e9-unified\]\|\[CRASH\]\|SIGBUS' scratch/agent/next_s1145/run.log | tail -30
```

Expected outcomes:

- STABLE LOOP/H1: phase records stop at 640 while slot dispatch continues;
  next unit can redesign the phase gate around the observed state.
- EARLY HALT/H2: dispatch/phase output has a terminal point with no later
  activity; next unit should isolate that halt.
- UNEVALUABLE/H3: any absence of VI-1024 or task-control E9 keeps the boundary
  crash hypothesis untested; do not interpret a null crash marker.
