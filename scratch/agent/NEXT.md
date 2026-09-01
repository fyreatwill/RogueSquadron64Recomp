# NEXT work unit — instrument the enclosing display-mode route

HYPOTHESIS-ID: m5-selector-route-gate

Session 3523 validly selected a phase-gated path difference: the real-audio
port reached title 1024 and hangar 512 with producer/store controls live, but
the known `setDisplayMode`/`reapplyDisplayMode` route and known AI callsite /
boundary rows were absent in hangar. Do one bounded diagnostic change: add a
regeneration-safe witness at the already-known `runVideoFrameTick` callers
and its conditional branch immediately around `reapplyDisplayMode`, then
build once and run one real-audio canonical arm. Include the existing route,
producer-context, selector-store, and AI-boundary controls with their
canonical environment names. No guest state or control flow may change.

Competing hypotheses and discriminator:

- `H-RouteGate`: `runVideoFrameTick` reaches its branch but suppresses
  `reapplyDisplayMode` in hangar; predicted branch-entry rows with no
  reapply/callsite rows.
- `H-AlternateCaller`: the branch is not the retail-equivalent path and a
  different caller reaches the stores; predicted live stores plus a
  separately observed alternate caller edge.
- `H-CallerParity`: the branch and reapply path are live in hangar but the
  known AI call is still absent; predicted hangar branch/reapply rows with
  zero AI rows, selecting an internal semantic mismatch.
- `H-CaptureInvalid`: startup controls or title/hangar phase rows are absent;
  predicted no valid comparison.

The discriminating table is phase-gated title 1024/hangar 512 rows for
runVideoFrameTick caller entry, branch taken/not-taken, reapply entry, known
AI callsite/boundary, producer context, and both selector stores. First run
the retail oracle with whole-RDRAM positive control and the existing
`0x80029E78` watch to qualify the independent route before building the new
port witness. Use SIGKILL for the port and capture logs under
`scratch/agent/s3524_*`.
