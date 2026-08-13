# NEXT work unit (s878)

HYPOTHESIS-ID: m3-coalesce-value-legitimacy

Perform one source/API audit of the oracle debugger callback and memory-read
interfaces to identify a safe deferred way to capture the value written by the
four coalescer watch ranges. Do not add a guard or change game behavior. If a
safe channel is found, specify its phase/control validation recipe; if not,
record the exact ABI limitation and pivot to a different independent ground
truth source.

Competing hypotheses:

- H-deferred-read-safe: the core exposes a safe deferred value read or
  value-bearing breakpoint callback.
- H-no-safe-value-api: the callback ABI exposes only flags/address/PC and a
  deferred read cannot preserve the writer association.
- H-oracle-phase-stall: the value route is safe, but the retail phase driver
  still cannot reach the late writer.

Discriminating measurement: source/API evidence that a deferred read can run
without stopping VI progress while retaining the triggering watch address/PC.
That selects H-deferred-read-safe; absence of such an ABI selects
H-no-safe-value-api; a safe sampler whose controls still remain at width 320
selects H-oracle-phase-stall.

Exact commands: inspect `tools/oracle/rs64_oracle.c` and the debugger symbols
used by `tools/oracle/build.sh`; consult `tools/oracle/README.md`; then make
one bounded source/API change only if the ABI supports it. No game build or
animating A/B run unless the audit identifies a safe value channel.
