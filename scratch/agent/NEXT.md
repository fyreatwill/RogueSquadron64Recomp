# NEXT work unit (s2343) — M5 B40 gate provenance census

HYPOTHESIS-ID: m5-descriptor-source-reachability

## Work unit

Run one ground-truth-first, no-behavior-change census of every named writer and
consumer boundary for guest byte `0x800A0F50`, retaining the s2342 pre-gate
outcome table, s2341 parent/gate rows, s2340 sequencer rows, the callback helper
positive control, all target route/task/DMA/guest-receive/PCM/filter/render/
key-on controls, and both stub/image arms. Use the existing B40 route/writer
breadcrumbs with `ROGUESQ_LOG_M5_B40_WRITER=1`; add only the minimum
regeneration-safe field needed to join writer PC/value rows to the existing
`0x80091468` branch rows. Do not change a writer, gate consumer, store,
default, slot, task, or audio behavior.

## Competing hypotheses and discriminating measurement

- H-CoverageInvalid: the retail whole-RDRAM/target/mode-gate-status/title/
  hangar controls, target writer-PC controls, requested-zero PC, callback
  registration, both port arms, or a retained same-run positive control fails.
- H-PortGateZeroLegitimate: the retail target-phase writer/value table and both
  port target-phase writer rows agree that the live gate byte is legitimately
  zero when `0x80091468` takes its bypass target.
- H-PortWriterMismatch: retail executes a named target-phase writer with a
  nonzero value, but the corresponding port writer row is missing or stores
  zero in both arms while the branch still reads zero.
- H-PortGateReadbackMismatch: a port writer row stores a nonzero value and the
  physical port watch confirms it, but the same-arm `0x80091468` row still has
  `lhs=0`, separating a readback/alias/ordering defect from writer reachability.
- H-PortPhaseClassifierMismatch: writer rows, physical watch rows, and branch
  rows are positive, but the `(phase,width,origin,ordinal)` join fails only
  under the target classifier; the broad controls remain positive.

The discriminator is one table keyed by `(arm, phase, width, origin, ordinal,
row, edge, writer_pc, old, requested, stored, observed_gate, branch_taken,
branch_lhs, branch_rhs, target)`. Require a retail whole-RDRAM positive
control and target-window/mode/status/title/hangar controls before interpreting
any retail null; require `port_controls=1` in both arms before interpreting a
port null. Select H-PortGateZeroLegitimate, H-PortWriterMismatch,
H-PortGateReadbackMismatch, or H-PortPhaseClassifierMismatch only when the
writer/value/branch rows split the hypotheses in both arms and the retained
positive controls pass. Otherwise report H-Unresolved without changing
behavior.

## Exact commands

The retail preflight must run before adding any new port field. Arm the
whole-RDRAM and physical target-window watches, `0xA0F50` byte watch,
mode/gate/status and callback-registration watches, both title/hangar origins,
and `--watch-pc` for the named B40 writers
`0x8008E9F8,0x8008EA34,0x8008EB40,0x8008EB7C,0x8008EC88,0x8008ECEC,0x8008ED48`,
the s2342 pre-gate/parent/gate/callsite PCs, retained scheduler/callback/
service PCs, and descriptor/key-on/decode/filter controls. Save it under a
non-dot final path and require the positive-control gate before building.

    tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 75 --watch-write 0x0:0x800000 --watch-write 0x165000:0x16B000 --watch-write 0xA0F50:0xA0F54 --watch-write 0x141AD0:0x141AF0 --watch-write 0x1498A:0x1498C --watch-write 0x154620:0x154624 --watch-write 0x11A8A4:0x11A8B4 --hit-cap 64 --watch-pc 0x8008E9F8,0x8008EA34,0x8008EB40,0x8008EB7C,0x8008EC88,0x8008ECEC,0x8008ED48,0x8009123C,0x8009142C,0x80091454,0x80091468,0x80091484,0x80091544,0x800915F8,0x800914A4,0x80091564,0x80091618,0x8008C9AC,0x8008CA14,0x80019B74,0x8009B5A8,0x80092128,0x80092230,0x8009231C,0x80090B68,0x80090C28,0x8009C904,0x8009D740,0x8009D7D0 --pc-phase-log-width 0x006AB400:512 --vi-trace --status-poll --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start > scratch/agent/s2343_m5_b40_gate_oracle.log 2>&1
    python3 ../rogue_squadron64/tools/make_elf.py
    (cd ../N64Recomp && build/N64Recomp rogue_squadron.toml)
    (cd ../N64Recomp && python3 fixup_game_funcs.py)
    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh -n scratch/agent/run_s2343_m5_b40_gate_provenance.sh
    zsh scratch/agent/run_s2343_m5_b40_gate_provenance.sh s2343_m5_b40_gate_provenance
