# NEXT: qualify mission entry by acting during the 512-wide phase
HYPOTHESIS-ID: m3-attached-mesh-mission-route

Session 4658 selected H3: its new post-512 timing still visited only known
attract/demo origins, although the handler ran 148 times. Do not repeat the
title-time sequence. Run one new oracle route, keeping the verified boot
presses, then act after the first 512-wide phase: A at 72s, Start at 105s, A
at 120s, and Z at 140s. Keep the whole-RDRAM control, both PC watches, Rice,
VI tracing, and PIF tracing:

tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/Cellar/mupen64plus/2.6.0/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 180 --hit-cap 200 --watch-write 0x0:0x800000 --watch-pc 0x8005427C,0x80001ACC --press 6.2:start,11.2:start,16.1:start,72:a,105:start,120:a,140:z --hold-ms 150 --vi-trace --pif-trace > scratch/agent/s4669_attached_mesh_route/oracle.log 2>&1

Competing hypotheses and discriminator:

- H1: a mission phase appears and the handler executes there; retain its
  origin and `rs_free` predecessor rows for the action-2 contract.
- H2: a mission phase appears but the handler remains absent; the static gap
  is route-absent for this mission entry.
- H3: the route remains title/attract/hangar-like 512-wide; input delivery or
  menu state is still the blocker.
- H4: the whole-RDRAM control or VI trace fails; the run is invalid.

The discriminator is a new 512-phase input transition, qualified by the
10,000-hit whole-RDRAM control, then phase-qualified origins for
`0x8005427C` and `0x80001ACC`. No guard or mitigation is authorized.
