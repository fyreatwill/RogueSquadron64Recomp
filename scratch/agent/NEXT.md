# NEXT work unit — census port parity for multiple frequency-writer inputs

HYPOTHESIS-ID: m5-frequency-writer-contract

Session 3435 selected `H-Multiple331E0Inputs`: the independent oracle's
phase-gated `0x800331E0` field census had 3,735 distinct tuples in the
`0x00790400` bucket and 4,088 in `0x00790800`; its target post-value watch had
701 samples and 64 distinct values. The direct target/result join is still
incomplete.

Competing hypotheses and the single discriminating measurement:

- `H-PortTupleFamilyMatch`: the port exposes the same phase-gated tuple family;
  the gap is after the writer-input contract.
- `H-PortTupleFamilyMissing`: the port tuple family differs or is absent;
  the gap is an earlier port input/dispatch contract.
- `H-PhaseJoinMissing`: the port target/result witness cannot be joined to the
  recorded tuple family, leaving the field model or join key unevaluable.

Exact work: add one phase-scoped port witness at the recompiled
`func_800331E0` boundary for the same field tuple columns used by the oracle,
plus the existing whole-RDRAM/VI/title/hangar controls and target/result
witness; build once, run once, and compare the complete tuple-family sets.
One matching family selects `H-PortTupleFamilyMatch`; no matching family
selects `H-PortTupleFamilyMissing`; live result rows without a join select
`H-PhaseJoinMissing`. Do not change waits, slots, dispatch, clear behavior, or
PCM writeback.

Build command: `cmake --build build --config Debug --target RogueSquadron64Recomp`.
Run from `build/Debug` with the existing phase-qualified M5 census recipe,
armed for the tuple witness and all passive breadcrumbs; capture to
`scratch/agent/s3436_m5_port_frequency_contract/run.log` and SIGKILL the game
after the title and hangar gates (or the validated timeout).

Run command:
`tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 75 --hit-cap 200 --watch-write 0x0:0x800000 --watch-write 0x165ED0:0x165ED4 --watch-pc 0x800331E0 --pc-phase-log-width 0x00790400:1024 --pc-phase-log-width 0x00790800:1024 --pc-field-dump 0x800331E0 --pc-hist-watch 1 --pc-hist-phase 0x00790400:1024 --pc-hist-phase 0x00790800:1024 --post-value-watch 1 --post-value-pc 0x800331E0 --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start --hold-ms 150 > scratch/agent/s3435_m5_frequency_contract/oracle.log 2>&1`.
