# NEXT work unit — qualify port parity at the retail VI edge

HYPOTHESIS-ID: m5-port-vi-edge-parity

## Single work unit

Add a phase-scoped probe at the host equivalent of retail instruction
`0x800357A8`, the first post-width VI-register publication identified in the
local ELF, then run one validated port capture. Keep the existing VI-context
and host voice-audit controls in the same run. No audio, route, or VI behavior
change is authorized by this unit.

## Competing hypotheses

- `H-PortEdgePresent`: the port reaches the new edge in the same target phase
  buckets as its VI controls, selecting a downstream parity investigation.
- `H-PortRouteStopsBeforeEdge`: controls pass but the port stops at pre-title
  640, so the edge row is unevaluable and the route boundary remains upstream.
- `H-PortProbeAbsent`: the port reaches a target phase but the new edge row is
  absent while the independent controls fire, selecting a host parity defect.

## Discriminating measurement

One Debug build must carry the new phase-scoped probe and both existing
positive controls. A run that reaches title `1024` and hangar `512` with the
new edge row selects `H-PortEdgePresent`; a controls-positive run that stops
at pre-title `640` selects `H-PortRouteStopsBeforeEdge`; target-phase controls
with no new edge row selects `H-PortProbeAbsent`. A null without target-phase
reach is unevaluable.

## Exact commands

```sh
rg -n "update_vi|VI_ORIGIN_REG|vi-context|voice-audit" src lib tools scratch/agent | head -120
cmake --build build --config Debug --target RogueSquadron64Recomp
env ROGUESQ_LOG_M5_VI_EDGE=1 zsh scratch/agent/run_s3143_m5_port_vi_edge.sh
```

The script must capture to a non-dot final path, watchdog itself, and SIGKILL
the game. Do not change audio or route behavior until the phase-keyed controls
select one of the three outcomes.
