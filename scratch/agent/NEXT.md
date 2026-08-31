# NEXT work unit — re-qualify the port route before the direct-writer edge

HYPOTHESIS-ID: m5-port-route-requalification

Do exactly one bounded route-requalification experiment next iteration. Run
the last known-good port recipe from `build/` with all new M5 logging disabled.
If it reaches title and hangar, repeat the same binary invocation with the
existing M5 logs enabled. Do not modify output, waits, slots, status handling,
consumer dispatch, or PCM writeback.

Competing hypotheses:

- `H-PortLoggingTrigger`: the new M5 logging combination triggers the early
  scheduler crash.
- `H-PortRouteRegression`: the current binary or route fails independently of
  the new logging.
- `H-PortRecipeMismatch`: the prior known-good recipe is not the recipe being
  invoked by the current launcher.

Discriminating measurement: title and hangar VI transitions plus crash/exit
status in the no-log baseline. Reachability in the no-log arm with failure in
the logging arm selects `H-PortLoggingTrigger`; the same scheduler SIGSEGV in
both selects `H-PortRouteRegression`; a different early failure selects
`H-PortRecipeMismatch`.

Exact constraints: launch from `build/`, use the ROM there, arm the canonical
Start schedule, use a non-dot-prefixed capture path, and terminate with
SIGKILL. No oracle or new instrumentation is needed before this baseline;
Session 3382 already supplied the retail ground truth and passed its positive
control.
