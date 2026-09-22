# Next work unit: qualify the first consumer after PCM queueing

HYPOTHESIS-ID: m5-ai-post-pcm-consumer

Session 3712 selected `H-AIStateParity` for the port: real and silent arms both
reached title/hangar and matched host `set-frequency` plus first PCM-consumer
rows at `22047 Hz`; only real audio reached image-stage rows. The next boundary
is audio drain/status and its image-stage join.

Competing hypotheses:

- `H-AudioDrainParity`: both arms expose the same queued-byte drain/status
  state and join it to the image-stage handoff.
- `H-AudioDrainDivergence`: drain/status or its handoff differs after the
  matched host state.
- `H-AudioDrainNotConsumed`: drain/status matches, but the image-stage path
  consumes a different or later audio state.

Discriminator: one phase-gated table of `get_remaining_audio_bytes`, AI status,
PCM drain/queue identity, and the first image-stage join, carrying the matched
`22047 Hz` state on both port arms. Matching drain/status and join rows select
parity; a different drain or join selects divergence; matching drain with no
image-stage join selects not-consumed. Both arms must pass RSP controls and
reach title/hangar.

Use the existing bounded frequency-contract driver as the route qualification
and extend its one build with the new side-effect/consumer table:

`DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build --config Debug --target RogueSquadron64Recomp`

`zsh scratch/agent/run_s3436_m5_port_frequency_contract.sh`

Do not alter the selector, clear, audio route, task, or payload.
