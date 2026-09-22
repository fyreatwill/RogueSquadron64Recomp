# Next work unit: qualify the internal AI-frequency return contract

HYPOTHESIS-ID: m5-ai-frequency-return-contract

Session 3710 selected `H-SelectorInputWriterParity`: independent retail and
both port arms agree that `0x80091CC8` writes `0x561F` to `0x80165ED0`, and
the `0x8009192C` load/caller preserve it. The remaining boundary is the
internal producer that receives source `0x5622` and returns the setup value
before that store.

Competing hypotheses:

- `H-AIFrequencyReturnParity`: retail and port execute the same internal call
  and return `0x561F`; the remaining image divergence is downstream.
- `H-AIFrequencyReturnDivergence`: the port's internal call or return differs
  and causes the selector setup to take a different later path.
- `H-AIFrequencyProducerState`: the call/return ABI matches, but the producer
  reads different state or table data before returning.

Discriminator: one phase-gated call/entry/return table for the internal
AI-frequency producer, carrying call PC, callee PC, source argument,
returned value, return PC, and relevant state/table pointer on retail and
both port arms. Matching call/return/source/state rows select parity;
different callee, return, or state selects the corresponding divergence;
matching ABI with different producer state selects `H-AIFrequencyProducerState`.
All arms must pass whole-RDRAM/RSP positive controls and reach title/hangar.

Use the existing bounded frequency-contract driver if its inputs are still
valid; otherwise repair it before running:

`DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build --config Debug --target RogueSquadron64Recomp`

`zsh scratch/agent/run_s3436_m5_port_frequency_contract.sh`

Do not alter the selector, clear, audio route, task, or payload.
