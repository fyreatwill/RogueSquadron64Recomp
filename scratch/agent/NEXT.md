# NEXT: qualify the post-hangar mission transition with the verified route
HYPOTHESIS-ID: m3-attached-mesh-mission-route

The previous three-Start route was invalid: it never reached 512. Run one
oracle arm using the README's verified Rice schedule, then continue Start
presses past the hangar hold so the route has a chance to leave the hangar.
Keep the positive control and both execution watches; do not add a guard.

Exact command:

tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 120 --hit-cap 200 --watch-write 0x0:0x800000 --watch-pc 0x8005427C,0x80001ACC --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start,61:start,66:start --hold-ms 150 --vi-trace --pif-trace > scratch/agent/s4671_attached_mesh_post_hangar/oracle.log 2>&1

Competing hypotheses and discriminator:

- H1: the verified schedule reaches the hangar and a post-hangar Start
  transition reaches a distinct mission VI origin; the handler executes there.
- H2: the schedule reaches the hangar and leaves it, but only into known
  attract/demo or title origins; handler rows remain non-mission.
- H3: the positive control fails or the route never reaches the known 512
  hangar origin (`0x006AB400`/`0x00690800`), making the run invalid again.

The result is valid only with a positive-control count in the thousands and a
512-wide hangar origin. Select H1 only if a later, distinct VI origin follows
the hangar and a handler row is attributable to that phase; otherwise record
H2 or H3 as appropriate.
