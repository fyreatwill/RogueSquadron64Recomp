# NEXT work unit (s879)

HYPOTHESIS-ID: m3-coalesce-value-legitimacy

Perform one source/API audit of the oracle debugger callback and memory-read
interfaces. Determine whether a value written by the four coalescer watch
ranges can be sampled later without stopping VI progress while retaining the
triggering writer address and PC. Do not change game behavior, add a guard, or
run an animating A/B unless the audit finds a safe value channel.

Competing hypotheses:

- H-deferred-read-safe: the core exposes a deferred value read or a
  value-bearing breakpoint callback.
- H-no-safe-value-api: the callback ABI exposes only flags/address/PC, and a
  deferred read cannot preserve writer association.
- H-oracle-phase-stall: a safe sampler exists, but retail still cannot leave
  VI width 320 under the validated input schedule.

Discriminating measurement: inspect the actual callback and memory-read ABI in
`tools/oracle/rs64_oracle.c`, its debugger symbols, and
`tools/oracle/README.md`. A documented safe deferred value route selects
H-deferred-read-safe; an ABI limitation selects H-no-safe-value-api; a safe
route whose positive whole-RDRAM/PIF/VI controls still remain at width 320
selects H-oracle-phase-stall.

Exact commands: use `rg` and bounded `sed` windows over the oracle sources and
README, then make at most one bounded source/API change if supported. No game
build is required for a source-only audit.
