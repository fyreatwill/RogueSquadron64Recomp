# NEXT work unit — identify the indirect callback pointer source

HYPOTHESIS-ID: m5-callback-indirect-pointer-source

## What has run and what artifacts exist

Session 3340 proved that retail reaches `registerSiCallback` from
`0x800919EC` five times, and the port's marker at that indirect site passes
`0x8009123C` into the entry in title and hangar phases. The load immediately
before the call is `lw $v0, -0x662C($v0)` at `0x800919D4`, reading physical
`0x001099D4`; the next writer/source boundary is unresolved.

## Competing hypotheses

- `H-PointerWriter`: a generated guest writer sets the indirect function
  pointer at `0x801099D4` to `0x80007910` or an equivalent callback target.
- `H-StalePointer`: the port's pointer is pre-existing/stale and the indirect
  call is only a consumer; no target-phase writer occurs.
- `H-HostDispatch`: the pointer is supplied by a host/runtime overlay or
  loader path, so neither generated writer census nor retail guest writes
  identifies it.

The discriminating measurement is one same-run writer census for physical
`0x001099D4:0x001099D8`, with retail and port arms plus whole-RDRAM positive
controls. A target-phase retail writer identifies `H-PointerWriter`; no
retail writer but a target-phase port writer selects `H-StalePointer` as a
port-only defect; no writer in either arm with valid indirect transfers
selects `H-HostDispatch`. A null is invalid unless the whole-RDRAM control
fires.

## Exact next commands

Before adding a new instrument, run the retail oracle with the existing
whole-RDRAM positive control and a physical write watch on
`0x001099D4:0x001099D8`, plus the existing callback execution watch:

    tools/oracle/build/rs64_oracle --core ../rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom ../rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 120 --watch-write 0x0:0x800000 --watch-write 0x1099D4:0x1099D8 --watch-pc 0x80007910 --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start --hold-ms 150

Then add the corresponding phase-gated port writer census through the fixup
path, build once, and run:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh scratch/agent/run_s3333_m5_callback_reachability.sh

The positive-control rows must include host-boundary and task-handoff controls,
and the run must reach title 1024 and hangar 512. No pointer writer or
behavioral change is authorized until both arms are valid.
