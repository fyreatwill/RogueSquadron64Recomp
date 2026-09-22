# Next work unit: qualify callback ownership/cadence after interleaved order

HYPOTHESIS-ID: m5-ai-post-pcm-consumer-ownership

Session 3718 rejected a stable image-before-consumer scheduling boundary. The
real hangar arm had 174 image-stage rows and 83 printed consumer rows; adjacent
cross-stream events occurred in both directions (46 image-after-consumer and
47 consumer-after-image). Silent reached the target phase and fired its RSP
control but emitted no image rows because its RSP arm is intentionally stubbed.
The retail oracle remains unavailable because its debugger-enabled core is
absent.

This next unit is one complete phase-gated source/thread/route table, not
another queue-threshold field.

Competing hypotheses:

- `H-CallbackOwnershipBoundary`: image-stage and PCM callbacks use distinct
  source/thread paths and route ordinals, selecting a host ownership boundary.
- `H-SharedCallbackState`: both callbacks use the same source/thread and route
  generation while queue mismatches persist, keeping
  `H-AudioDrainNotConsumed` open at host consumer state.
- `H-CallbackInstrumentAbsent`: any missing source/thread/route control makes
  the table unevaluable; no ownership conclusion is allowed.

Discriminator: one phase-gated table containing callback source, thread ID,
route ordinal, queue depth, callback sequence, and timestamp for every target
image-stage and exact consumer event. Both target VI transitions and the
RSP-source positive control must fire in both arms. If the callbacks have
distinct source/thread and stale route ordinals, select
`H-CallbackOwnershipBoundary`; if they share source/thread and route
generation while queue mismatches persist, keep `H-AudioDrainNotConsumed`
open; if fields or controls are absent, repair the instrument before inferring
anything.

Commands:

`DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build --config Debug --target RogueSquadron64Recomp`

`zsh scratch/agent/run_s3436_m5_port_frequency_contract.sh`
