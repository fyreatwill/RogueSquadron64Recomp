# NEXT work unit (s1076)

HYPOTHESIS-ID: oracle-512-phase-discriminator

Perform one bounded design audit for a new retail-oracle route to the VI-512
hangar-origin phase. Read only `tools/oracle/README.md`, existing oracle
recipe/config files, and the relevant current-truth entries. Enumerate the
existing positive controls and closed schedule/input explanations, then name
one new phase-gated discriminator whose outcomes would split the remaining
state-shaped hypotheses. Do not build or run.

Competing hypotheses and discriminator:

* `H-oracle-state`: a newly isolated state/config predicate is the missing
  gate and can be tested without changing input timing or cadence.
* `H-oracle-input`: an unclosed controller-edge or input-shape predicate is
  the missing gate and requires a schedule arm.
* `H-oracle-route-open`: the existing oracle surface cannot discriminate the
  remaining hypotheses; identify the single missing observation or harness
  capability needed before a run.

Discriminating measurement: one table mapping each candidate schedule/config/
input arm to its phase transition, independent positive control, and the
first observation that differs at VI 512. A complete new arm selects the
corresponding state or input hypothesis; no arm capable of separating them
selects `H-oracle-route-open` and blocks runtime instrumentation.

Exact commands:

```sh
sed -n '1,240p' tools/oracle/README.md
rg -n -S 'oracle|mupen|schedule|Start|controller|VI|512|320' tools/oracle docs/CURRENT-TRUTH.md \
  --glob '*.{md,ps1,sh,py,json,toml}' 2>/dev/null
```

No build or runtime run is needed for this design audit.
