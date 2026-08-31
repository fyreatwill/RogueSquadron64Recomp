# NEXT work unit — trace the selected frequency writer contract

HYPOTHESIS-ID: m5-frequency-writer-contract

Session 3434 selected `H-Candidate331E0`: it directly wrote target
`0x165ED0` in both corrected title buckets, with 442/442 nonzero post-store
samples. `0x80033420` had only 8/8 zero-valued samples.

Competing hypotheses and the single discriminating measurement:

- `H-Stable331E0Input`: all phase-gated `0x800331E0` executions use one stable
  caller/input tuple; the port can be compared at that contract.
- `H-Multiple331E0Inputs`: phase-gated executions use multiple caller/input
  tuples; caller-specific parity is the next boundary.
- `H-PhaseJoinMissing`: the candidate's field/argument dump does not join the
  nonzero target writes, exposing an oracle join defect or wrong field model.

Exact work: run one oracle arm with whole-RDRAM control, target
`0x165ED0:0x165ED4`, both phase buckets, `--watch-pc 0x800331E0`,
`--pc-field-dump 0x800331E0`, and `--post-value-pc 0x800331E0`. Use the same
validated Start schedule and retain the target writer histogram. A single
phase-gated caller/input tuple selects `H-Stable331E0Input`; two or more
tuples select `H-Multiple331E0Inputs`; live nonzero target joins without a
matching field row select `H-PhaseJoinMissing`.
Do not change waits, slots, dispatch, clear behavior, or PCM writeback.

Run command:
`tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 75 --hit-cap 200 --watch-write 0x0:0x800000 --watch-write 0x165ED0:0x165ED4 --watch-pc 0x800331E0 --pc-phase-log-width 0x00790400:1024 --pc-phase-log-width 0x00790800:1024 --pc-field-dump 0x800331E0 --pc-hist-watch 1 --pc-hist-phase 0x00790400:1024 --pc-hist-phase 0x00790800:1024 --post-value-watch 1 --post-value-pc 0x800331E0 --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start --hold-ms 150 > scratch/agent/s3435_m5_frequency_contract/oracle.log 2>&1`.
