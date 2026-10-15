# Next work unit

HYPOTHESIS-ID: m5-audio-destub

Resolve the selected mission attribution drift with one bounded join. Extend
the existing `scratch/agent/s4923_mission_longevity.sh` capture so the nearest
transition-window event ordinal, route ordinal/row, and PCM join event are
reported together for both `0x00690400` and `0x00620400`. Keep the first-512
gate, one Start/A pair, all passive breadcrumbs, and the current default
audio behavior. Build once and run one same-build capture; do not add a guard
or skip.

Competing hypotheses and discriminator:

1. H-origin-label: the same audio event sequence retains a stable route
   ordinal/row across the origin change, while only the VI origin label moves.
   Stable ordinal/row joins select a VI-origin attribution defect.
2. H-route-reinit: the origin change coincides with a new route ordinal or
   row and the PCM event sequence restarts. A discontinuity selects route
   reinitialization during the handoff.
3. H-route-invalid: the first-512 gate, post-key `0x00690400`, following
   `0x00620400`, advancing counter, or PCM controls fail. Missing controls
   make the capture unevaluable and select no audio explanation.

Positive controls: phase output at `0x00690400`, audio-join PCM rows at both
origins, advancing `update_screen`, nonzero global task/PCM rows, and zero
crash/abort markers. The ordinal/row continuity table is the discriminator.

Exact baseline command:

`cmake --build build --config Debug --target RogueSquadron64Recomp && zsh scratch/agent/s4923_mission_longevity.sh`

Inspect only `scratch/agent/s4923_mission_longevity/summary.txt` and bounded
`grep -a` matches from `run.log`; kill any manual process with SIGKILL.
