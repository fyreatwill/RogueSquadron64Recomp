# Next work unit (s4444): re-derive the s4441 B1 crash without the 247-node assumption (m5-ai-event-cadence)

HYPOTHESIS-ID: m5-ai-event-cadence

State (s4443): 0x801FB3F0 next=0x801FB408 is a legitimate init link (guest 0x8008F90C); no unnamed writer. Arm B (115 Hz) survived 150 s; arm A crashed (host bus error far=0x38000950e, guest x1=0x80091378).
Hypotheses: (a) pool block is larger and the B1 crash has another cause (read s4441 B1 log, find the actual faulting node/addr); (b) crash rate is cadence-independent and noisy; (c) arm A's bus error is a new shape.
Discriminator: offline re-read of scratch/agent/s4441 port_B logs and the s4443 port_A crash block (guest pc, node address vs the init chain end); then 4 repeats per arm via `zsh /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/s4443/run.sh <label> <none|115>` for crash rates.
Note: shell cwd can drift; use absolute paths.
