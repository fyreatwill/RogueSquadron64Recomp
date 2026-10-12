# NEXT: qualify a distinct mission-entry input route for attached-mesh oracle
HYPOTHESIS-ID: m3-attached-mesh-mission-route

The s4667 corrected oracle run was instrument-valid and reached title plus
512-wide hangar/attract origins, but the prescribed Start/A schedule did not
establish a mission phase and the handler stayed at zero. Do not repeat that
schedule. The next single unit is one oracle run using the same boot presses,
then a distinct post-512 input sequence with PIF tracing: Start at 80s, Start
at 86s, A at 92s, and Start at 100s. Keep the whole-RDRAM control and both PC
watches. Use Rice video and run 180s:

tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/Cellar/mupen64plus/2.6.0/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 180 --hit-cap 200 --watch-write 0x0:0x800000 --watch-pc 0x8005427C,0x80001ACC --press 6.2:start,11.2:start,16.1:start,80:start,86:start,92:a,100:start --hold-ms 150 --vi-trace --pif-trace > scratch/agent/s4668_attached_mesh_route/oracle.log 2>&1

Competing hypotheses and discriminator:

- H1: the distinct post-512 sequence reaches mission; handler executions and
  same-phase `rs_free` predecessor rows classify the action-2 frees.
- H2: it reaches mission but the handler remains absent; the static gap is
  route-absent for this mission entry.
- H3: it remains hangar/attract; the input route, not the handler contract,
  is still the blocker.
- H4: the whole-RDRAM control or VI trace fails; the run is invalid.

The discriminator is whole-RDRAM control plus a new 512-to-mission route
transition, followed by phase-qualified counts for `0x8005427C` and
`0x80001ACC`. No guard or mitigation is authorized from a null result.
