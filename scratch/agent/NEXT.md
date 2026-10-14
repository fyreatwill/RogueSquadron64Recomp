# Next work unit

HYPOTHESIS-ID: m5-qualified-route-startup-contract

The M5 Step 1 A/B is parked until the documented qualified route reaches its
VI-640 positive control. s4825 showed that both arms share the first SP task
and scheduler dispatch; request-only crashes after that completion, before
any `osSpTaskYielded` A/B row, at `si_addr=0x400128d47`.

Single bounded work unit: add one batch of host-boundary witnesses and run the
same phase-gated pair, without another Step 1 A/B or a mitigation. Competing
hypotheses:

* H-pointer-conversion: `TO_PTR`/task-field conversion produces the malformed
  host address; select if the bad address first appears at conversion or task
  field logging in both arms.
* H-startgo/enqueue: the task is valid until `osSpTaskStartGo` or
  `submit_rsp_task`; select if conversion is valid and the first bad address
  appears in one of those boundaries in both arms.
* H-request-state: request-only changes a scheduler/task field before the
  fault; select only if the request-only arm diverges in the complete bounded
  state table before the first bad address.

Discriminating measurement: in one build/run, log the task guest pointer and
all task fields at `osSpTaskStartGo`, `TO_PTR`, and `submit_rsp_task`, plus the
first host address rejected by the RDRAM accessor. A whole-RDRAM/task-validity
control must fire in the same run. The first site to emit `0x400128d47` splits
conversion from start/enqueue; any request-only-only field divergence selects
the third hypothesis. If no site sees it, remain blocked on a native crash
stack with symbols.

```sh
rg -n -C 8 "TO_PTR|osSpTaskStartGo_recomp|submit_rsp_task|0x400128d47|SP_YIELDED_REQUEST_ONLY" src lib ../N64Recomp/RecompiledFuncs tools
sed -n '1220,1265p' lib/N64ModernRuntime/ultramodern/src/events.cpp
sed -n '44,112p' lib/N64ModernRuntime/librecomp/src/sp.cpp
zsh tools/run_m5_yield_ab.sh
```

Do not rerun `tools/run_m5_yield_ab.sh` until this audit identifies a route
qualification fix or confirms the tuple is correctly active and the failure is
understood.
