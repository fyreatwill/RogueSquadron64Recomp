# Next work unit: qualify the post-return AI side-effect boundary

HYPOTHESIS-ID: m5-ai-post-return-side-effect

Session 3711 selected `H-AIFrequencyReturnParity`: the valid port run and
independent retail evidence both show `a0=0x5622` entering `0x80029D20` and
the actual result `0x561F` reaching the setup store. The next boundary is the
post-return hardware/host audio-state side effect and its consumer.

Competing hypotheses:

- `H-AIStateParity`: retail and port perform the same post-return state update
  and consumer sees the same frequency/state tuple.
- `H-AIStateDivergence`: the host side effect or consumer state differs after
  the matched `0x561F` return.
- `H-AIStateNotConsumed`: the side effect matches, but the downstream image
  path does not consume it or consumes a later value.

Discriminator: one phase-gated table of the post-return AI state write,
host `set_audio_frequency` input, and the first downstream consumer, carrying
the matched `0x5622 -> 0x561F` tuple and state/consumer identity on retail and
both port arms. Matching side-effect and consumer rows select parity; a
different state or consumer selects the corresponding divergence; matching
state with no consumer match selects `H-AIStateNotConsumed`. All arms must
pass whole-RDRAM/RSP positive controls and reach title/hangar.

Use the existing bounded frequency-contract driver as the route qualification
and extend its one build with the new side-effect/consumer table:

`DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build --config Debug --target RogueSquadron64Recomp`

`zsh scratch/agent/run_s3436_m5_port_frequency_contract.sh`

Do not alter the selector, clear, audio route, task, or payload.
