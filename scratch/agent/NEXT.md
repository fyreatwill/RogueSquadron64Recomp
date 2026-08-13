# NEXT work unit (s874)

HYPOTHESIS-ID: m3-video-ready-display-gate-audit

Perform one source-only whole-idiom audit of `setDisplayMode`,
`reapplyDisplayMode`, `setVideoReadyFlag`, `setViModeType`, and
`thread3_video_handle`, including every writer/read/callsite in the chain
before `runVideoFrameTick`. Do not build or run. Classify each site as
initialization, per-frame update, gate, or dead/unreachable, and identify the
exact predicate/value that could keep startup at VI width 320. Do not add a
guard or alter behavior.

Competing hypotheses:

- H-video-ready-port-gate: a port readiness/display-mode writer or predicate is
  systematically stale or missing.
- H-retail-state-machine: the port pre-tick gates are complete; the width-320
  stall is outside this call chain.
- H-audio-display-coupling: a display-mode transition depends on an audio
  completion path that remains stubbed.

Discriminating measurement: a complete source inventory with no audio
dependency selects H-retail-state-machine; a missing/stale readiness writer
selects H-video-ready-port-gate; an audio-only producer for a transition
predicate selects H-audio-display-coupling. An incomplete callsite inventory
is unevaluable.

Exact command from the repo root:

```sh
rg -n "setDisplayMode|reapplyDisplayMode|setVideoReadyFlag|setViModeType|thread3_video_handle|8000274C|80003380|8008EA14|8011.*2DEF" ../N64Recomp/RecompiledFuncs src lib/N64ModernRuntime
```

Read bounded windows around every generated-function hit. Do not build or run.
Record the inventory and source-only conclusion in the session ledger and
CURRENT-TRUTH.
