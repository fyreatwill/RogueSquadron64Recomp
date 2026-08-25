# NEXT work unit (s2344) — M5 C88 writer treatment validation

HYPOTHESIS-ID: m5-c88-writer-treatment

## Work unit

Run one same-build, phase-gated A/B of the `0x8008EC88` guest writer arm,
across both silent and Factor 5 image audio arms:

| audio arm | C88 control | C88 treatment |
|---|---:|---:|
| stub (`ROGUESQ_AUDIO_UCODE=0`) | `ROGUESQ_M5_C88_VALUE=0` | `=1` |
| image (`ROGUESQ_AUDIO_UCODE=1`) | `ROGUESQ_M5_C88_VALUE=0` | `=1` |

Keep `ROGUESQ_M5_B40_VALUE=0`; do not change the generated store, gate
consumer, task, slot, voice, or PCM code. The treatment is opt-in through the
existing environment arm only. Retain `writer_seq`/`0x80091468` rows and all
s2343 controls. ORIGIN: the existing host force-zero at `0x8008EC88` is the
writer mismatch under test; retail post-store evidence now says its original
nonzero value is legitimate, but this iteration must not promote it.

## Competing hypotheses and discriminating measurement

- H-CoverageInvalid: the fresh retail post-value/whole-RDRAM/target/status/
  title/hangar controls, or any of the four port arms' route, task/DMA,
  guest-receive, PCM, filter, render, key-on, callback-helper, or writer
  positive controls fails.
- H-C88WriterRestoresGate: with `C88=1`, both audio arms store nonzero at
  `0x8008EC88`, the joined `0x80091468` branch reads nonzero and does not take
  the zero-gate bypass, and a downstream task/slot/voice/PCM transition appears
  that is absent from the same-audio `C88=0` control.
- H-C88ReadbackMismatch: the treatment writer stores nonzero, but the joined
  branch still reports `lhs=0`; this selects a readback/alias/order defect,
  not writer reachability.
- H-C88GateNotSufficient: the treatment branch reads nonzero, but the complete
  task/slot/voice/PCM row remains unchanged or invalid in both audio arms.
- H-C88RouteOnly: treatment changes route/phase reachability but produces no
  new downstream audio contract signal; do not call this audio progress.

The discriminator is one table keyed by
`(audio_arm,c88,phase,width,origin,writer_seq,writer_pc,requested,stored,
branch_taken,branch_lhs,branch_rhs,target,task,slot,voice,pcm_source,
pcm_consumer)`. Require the fresh retail value witness and all four
same-build `port_controls=1` rows before interpreting any null. Select only
when control/treatment pairs are phase-valid in both audio arms. A treatment
that merely changes route or avoids a crash is not success.

## Exact commands

Run the independent retail witness before the port build/run. The post-value
watch must show `0x8008EC88` nonzero in target-like rows while the whole-RDRAM
watch fires:

    tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 75 --watch-write 0x0:0x800000 --watch-write 0x165000:0x16B000 --watch-write 0xA0F50:0xA0F54 --watch-write 0x141AD0:0x141AF0 --watch-write 0x1498A:0x1498C --watch-write 0x154620:0x154624 --watch-write 0x11A8A4:0x11A8B4 --hit-cap 64 --pc-hist-watch 2 --pc-hist-phase 0x00790400:1024 --pc-hist-phase 0x006AB400:512 --post-value-watch 2 --post-value-pc 0x8008E9F8,0x8008EA34,0x8008EB40,0x8008EB7C,0x8008EC88,0x8008ECEC,0x8008ED48 --post-value-pc-detail --watch-pc 0x8008E9F8,0x8008EA34,0x8008EB40,0x8008EB7C,0x8008EC88,0x8008ECEC,0x8008ED48,0x8009123C,0x8009142C,0x80091454,0x80091468,0x80091484,0x80091544,0x800915F8,0x800914A4,0x80091564,0x80091618,0x8008C9AC,0x8008CA14,0x80019B74,0x8009B5A8,0x80092128,0x80092230,0x8009231C,0x80090B68,0x80090C28,0x8009C904,0x8009D740,0x8009D7D0 --pc-phase-log-width 0x006AB400:512 --vi-trace --status-poll --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start > scratch/agent/s2344_m5_c88_oracle.log 2>&1
    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh -n scratch/agent/run_s2344_m5_c88_writer_treatment.sh
    zsh scratch/agent/run_s2344_m5_c88_writer_treatment.sh s2344_m5_c88_writer_treatment

The driver must launch all four arms itself from `build/`, use the same
eleven-Start schedule, phase-gate on `1024 @ 0x00790400` and `512 @
0x006AB400`, and terminate each process group with SIGKILL.
