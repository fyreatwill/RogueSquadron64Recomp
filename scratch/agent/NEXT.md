# Next work unit: identify the host audio drain consumer/callback

HYPOTHESIS-ID: m5-ai-post-pcm-consumer

Session 3714 confirmed `H-AudioDrainDivergence` with an independent retail
busy/success control and a corrected same-build pair. Retail had 4,335 target
`set-next`/busy/success triples and no reject branch. Port real audio had 114
target `set-next` rows, depth 741–3813, and 471 image-stage rows; silent had
29, depth 741–4581, and zero image-stage rows. Both port arms had zero target
status/length calls and zero nonzero PCM rows. The port queue consumer/callback
boundary remains unresolved.

Competing hypotheses:

- `H-AudioDrainParity`: both arms expose the same host enqueue/dequeue cadence
  and queued-byte state before image-stage handoff.
- `H-AudioDrainDivergence`: the host consumer/callback cadence or queue depth
  differs between real and silent arms. Current result selects this at the
  port boundary.
- `H-AudioDrainNotConsumed`: the host queue state matches, but image-stage
  consumes a different or later audio state. Still open downstream, but guest
  status/length is not the measured discriminator.

Discriminator: one phase-gated table of `queue_audio_buffer` enqueue rows,
SDL callback/dequeue rows, raw and adjusted queue depth, PCM buffer identity,
and the first image-stage join, carrying the matched `22047 Hz` state on both
port arms. Matching enqueue with divergent callback/dequeue cadence selects a
host consumer explanation; matching cadence with divergent image-stage joins
keeps `H-AudioDrainNotConsumed` open. Both arms must pass RSP controls and
reach title/hangar.

Use the paired driver after adding the host callback table:

`DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build --config Debug --target RogueSquadron64Recomp`

`zsh scratch/agent/run_s3436_m5_port_frequency_contract.sh`

Do not alter the selector, clear, audio route, task, or payload.
