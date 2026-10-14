# Next work unit

HYPOTHESIS-ID: m5-qualified-route-startup-contract

The M5 Step 1 A/B is parked until the documented qualified route reaches its
VI-640 positive control. s4824 changed the harness to launch the tuple and
showed a new pre-control failure: default stops at VI 320 after 10 SP
completions; request-only crashes in `spTaskSchedulerThread+8972` with
`si_addr=0x400128d47` after one completion.

Single bounded work unit: audit and symbolicate this startup boundary, without
another Step 1 A/B or a mitigation. Competing hypotheses:

* H-common-route: LLE/real-audio startup fails in both arms before VI 640;
  select if the default stop and request-only crash share the same guest task,
  queue, or state transition.
* H-request-state: request-only handling corrupts scheduler state; select only
  if the request-only crash maps to a state/queue write absent from the default
  arm at the same phase.
* H-stale-route: the tuple is not actually the qualified route in this binary;
  select if source/config inspection finds a missing or overridden flag, stale
  generated function, or route gate before the first VI-640 transition.

Discriminating measurement: symbolicate `spTaskSchedulerThread+8972`, map its
guest PC and nearby generated function to source, then compare the bounded
VI-320 rows and first-SP task/queue state in both saved logs. Outcomes must
identify a shared common boundary, a request-only-only state mutation, or a
configuration/build mismatch; otherwise remain blocked on the specific missing
route evidence. Commands:

```sh
atos -o build/RogueSquadron64Recomp -l 0x100000000 0x1056dc634
rg -n -C 8 "spTaskSchedulerThread|0x8000834c|request.only|SP_YIELDED|LLE_FORCE|AUDIO_UCODE" src lib RecompiledFuncs tools
grep -a -n -E "\[phase\]|\[event-wiring\] complete kind=SP|\[CRASH\]|spTaskSchedulerThread|\[sp-yielded-ab\]" scratch/agent/m5_yield_ab/default.log scratch/agent/m5_yield_ab/request-only.log
```

Do not rerun `tools/run_m5_yield_ab.sh` until this audit identifies a route
qualification fix or confirms the tuple is correctly active and the failure is
understood.
