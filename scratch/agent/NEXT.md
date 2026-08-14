# NEXT work unit (s1077)

HYPOTHESIS-ID: oracle-512-phase-discriminator

Run the one-arm retail-oracle discriminator in
`docs/ORACLE-512-DISCRIMINATOR.md`. Use the documented eleven-Start schedule,
whole-RDRAM positive control, physical watches on `0x13A960:0x13A970` and
`0x130B40:0x130B58`, plus `--vi-trace --vi-poll --pif-trace`. Phase-gate all
interpretation on VI width/origin transitions; do not use a stopwatch and do
not arm the freelist watch.

Competing hypotheses and discriminator:

* `H-oracle-state`: a newly isolated state/config predicate is the missing
  gate and can be tested without changing input timing or cadence.
* `H-oracle-input`: an unclosed controller-edge or input-shape predicate is
  the missing gate and requires a schedule arm.
* `H-oracle-route-open`: the existing oracle surface cannot discriminate the
  remaining hypotheses; identify the single missing observation or harness
  capability needed before another run.

Discriminating measurement: classify the same-run combination of controller
edge writes, selector/state writes, PIF reads, and VI origin. Edge writes with
no selector writes select a state gate; selector writes without hangar-origin
512 select a downstream state gate; absent edge writes despite positive PIF
select an execution/alias boundary; selector writes plus `0x6abxxx` 512 solve
the route. If the watches cannot observe the needed transition, select
`H-oracle-route-open` and name the missing execution/read observation.

Exact commands:

```sh
sed -n '1,240p' tools/oracle/README.md
rg -n -S 'oracle|mupen|schedule|Start|controller|VI|512|320' tools/oracle docs/CURRENT-TRUTH.md \
  --glob '*.{md,ps1,sh,py,json,toml}' 2>/dev/null
```

Exact run shape: use the already-built oracle binary for 120 seconds with the
eleven Start events at 6,11,...,56 seconds, capture to a non-dot final path,
and SIGKILL only if a watchdog is required. One run; no build is needed before
executing the existing binary.
