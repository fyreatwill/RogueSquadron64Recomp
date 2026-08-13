# NEXT work unit (s880)

HYPOTHESIS-ID: m3-coalesce-independent-ground-truth-pivot

Perform one bounded audit of a different independent ground-truth route for
the four coalescer watch ranges. Start with the available retail ROM/core
artifacts and identify one route that can associate a post-write value with a
guest PC without relying on the stock debugger callback ABI. Do not add a
runtime guard, change game behavior, or run an animating A/B unless the audit
identifies a concrete route and its controls.

Competing hypotheses:

- H-core-write-trace: an existing retail core trace/disassembly hook can emit
  post-write value plus guest PC without changing emulation behavior.
- H-static-retail-proof: retail ROM disassembly/data-flow can prove the value
  legitimacy of the coalescer writers without a dynamic sampler.
- H-no-independent-route: neither available artifact provides the required
  writer/value association, so the legitimacy question must be parked.

Discriminating measurement: source/API or artifact evidence showing whether a
post-write value and its guest writer PC can be obtained independently of the
recompiled runtime. A concrete safe route selects H-core-write-trace or
H-static-retail-proof; absence selects H-no-independent-route.

Exact commands: inspect the local oracle core for existing trace hooks and the
retail ROM/decomp artifacts for a bounded writer/data-flow proof, using `rg`
and bounded `sed` windows. No game build or soak is planned for this audit.
