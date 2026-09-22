# Next work unit: identify the post-PCM drain divergence and status consumer

HYPOTHESIS-ID: m5-ai-post-pcm-consumer

Session 3713 selected `H-AudioDrainDivergence` for the measured host boundary:
both arms reached title/hangar and passed RSP controls, but hangar real audio
had 43 `set-next` drain rows with raw queue depth 0–4581 bytes while silent had
132 rows with 741–4581 bytes. Both arms' PCM joins were zero and only real
audio had image-stage rows. No target-phase `get-status`/`get-length` call ran.
This is single-source port evidence.

Competing hypotheses:

- `H-AudioDrainParity`: both arms expose the same queued-byte drain/status
  state and join it to the image-stage handoff.
- `H-AudioDrainDivergence`: the observed host drain cadence/depth differs after
  the matched host state. Current result selects this at the port boundary.
- `H-AudioDrainNotConsumed`: drain/status matches, but the image-stage path
  consumes a different or later audio state. Still open because status/length
  was not called in the target phase.

Discriminator: one phase-gated table of raw SDL queue depth, adjusted
`get_remaining_audio_bytes`, AI status/length call sites, PCM drain/queue
identity, and the first image-stage join, carrying the matched `22047 Hz`
state on both port arms. A repeated depth/cadence difference selects
divergence; matching depth with no status/image-stage join keeps not-consumed
open. Both arms must pass RSP controls and reach title/hangar.

Use the paired driver:

`DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build --config Debug --target RogueSquadron64Recomp`

`zsh scratch/agent/run_s3436_m5_port_frequency_contract.sh`

Do not alter the selector, clear, audio route, task, or payload.
