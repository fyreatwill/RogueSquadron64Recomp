# NEXT: qualify mission entry using a hangar-origin action sequence
HYPOTHESIS-ID: m3-attached-mesh-mission-route

Session 4669 selected H3 again: with the installed Rice plugin, the route
reached 512-wide only at known attract/demo origins and the handler ran 280
times there. The run later exited 138 during Rice shader compilation, so do
not interpret its duration as a stability result. Use a genuinely different
control: the oracle README says the verified boot presses reach a hangar at
about 38s and that continued Start presses advance out of it. Run the verified
boot presses, then press A once at 40s while the first 512 phase is active and
do not send later Start/A/Z presses. Keep the installed Rice path, whole-RDRAM
control, both PC watches, VI tracing, and PIF tracing:

tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 120 --hit-cap 200 --watch-write 0x0:0x800000 --watch-pc 0x8005427C,0x80001ACC --press 6.2:start,11.2:start,16.1:start,40:a --hold-ms 150 --vi-trace --pif-trace > scratch/agent/s4670_attached_mesh_hangar_action/oracle.log 2>&1

Competing hypotheses and discriminator:

- H1: the hangar-origin A action enters a mission phase and the handler
  executes there; retain its origin and `rs_free` predecessor rows.
- H2: a 512 hangar origin appears but A does not enter a mission; handler rows
  remain attract/demo-only.
- H3: the route never reaches the known hangar origin or the whole-RDRAM
  control fails; the run is invalid.

The discriminator is a 512 origin of `0x006AB400` or `0x00690800` followed by
a distinct mission VI origin, with the positive control at 10,000 callbacks.
No guard or mitigation is authorized.
