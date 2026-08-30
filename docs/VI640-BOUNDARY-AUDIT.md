# VI-640 boundary audit

Session 3262 (2026-08-29) audited the local source for the state edge that
should request the post-640 VI mode.

## Findings

- `src/main/upstream_compat.cpp` observes and forwards `osViSetMode`, then
  records the requested width and committed VI registers. It does not choose
  the mode.
- The host-side `update_screen` path only consumes the committed VI registers;
  it has no target-mode request suppression or terminal-route branch.
- The only local reference to `applyPendingViChanges` is
  `tools/apply_s802_vi_selector_probe.py`, which expects the generated caller
  to invoke it at `0x80019914`. The generated `RecompiledFuncs/` tree is absent
  from this checkout, so the function body, its state loads, and its branch
  successors cannot be enumerated here.
- The local source therefore cannot distinguish `H-RequestState` from
  `H-BoundaryConsumer` or `H-Phase4SteadyState`. The existing same-width
  `osViSetMode` observation proves only that a request occurred; it does not
  expose the missing producer state or establish that a target request was
  issued.

## Consequence

No build or runtime instrumentation was justified. The next satisfying input
is the generated function body (or an independently captured ground-truth
execution trace for its state inputs) from the configured regeneration host.
Do not repeat the receive identity capture or add another host-side VI field
until that input identifies a concrete state edge.
