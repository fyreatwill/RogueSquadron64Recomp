# NEXT work unit (s2457) — capture the first-null resolver caller

HYPOTHESIS-ID: m5-first-null-resolver-boundary

## Work unit

Add one host-side, first-hit-only capture at the existing `get_function` entry
for `addr == 0`, including native return address/backtrace, the requested
address, and `g_rs64_last_guest_pc`; retain the existing indirect positive
control in the same qualified port run. This is a bounded diagnostic change,
not a behavior change and not permission to stub missing functions.

## Competing hypotheses and discriminator

- H-ResolverGeneratedCaller: the first null has a generated native caller and
  a symbol-derived or register-derived guest target absent from the map.
- H-ResolverEntryPolicy: the first null originates at thread entry or another
  runtime resolver boundary, not a generated in-game callsite.
- H-StaleGuestBreadcrumb: the native caller and `g_rs64_last_guest_pc` do not
  agree; `0x80001F88` is stale/unrelated to the null lookup.

The discriminator is one first-null row containing native caller, backtrace,
requested target, guest-PC breadcrumb, and whether the same run's indirect
positive control resolves. A generated caller with a real target selects
H-ResolverGeneratedCaller; a runtime caller selects H-ResolverEntryPolicy;
disagreement between native caller and guest breadcrumb selects
H-StaleGuestBreadcrumb. Missing the positive control is a non-result.

## Exact commands

1. Before building, inspect the existing resolver and control:

   `rg -n "get_function\\(|LOOKUP_FUNC|rs64_log_tickfunc_caller|backtrace" lib/N64ModernRuntime/librecomp/src lib/N64ModernRuntime/N64Recomp/src`

2. Add the first-null-only capture in
   `lib/N64ModernRuntime/librecomp/src/overlays.cpp` at `get_function`, using
   the existing log gate and `backtrace` helpers. Keep the positive-control
   path unchanged. Build once with the qualified route; do not set
   `ROGUESQ_STUB_MISSING_FUNCS`.

3. Run one 120-second qualified port capture from `build/`, with
   `ROGUESQ_LOG_M5_SECOND_EXEC=1`, capturing stdout/stderr to
   `scratch/agent/s2457_port_null_resolver.log`; SIGKILL the process if the
   watchdog expires.

4. Expected selection: one first-null row with a native caller and a live
   positive-control resolution. Zero rows or no positive control is a
   non-result; do not enable a mitigation or resume second-range provenance.
