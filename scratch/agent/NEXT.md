# Next work unit

HYPOTHESIS-ID: external-retail-entry-boundary

WORK UNIT: retry the external retail-entry boundary on the qualified retail
route using the known Rice video plugin and documented Start schedule. Do not
modify runtime behavior.

Competing hypotheses:

* H-retail-entry: title/hangar VI controls become positive and the retail run
  reaches `0x800903F0`, supplying a PC/VI/route witness for the handoff.
* H-retail-route-absent: title/hangar VI controls are positive, but
  `0x800903F0` remains zero; the handoff is absent on the driven retail route.
* H-oracle-route: Rice/input setup fails to leave 320-wide pre-title, so a
  zero target count remains route-invalid and the setup recipe needs repair.

DISCRIMINATING MEASUREMENT: one invocation must show the whole-RDRAM control,
VI transitions through title `1024 @ 0x00790400` and hangar
`512 @ 0x006AB400`, and the target-PC count. A target hit joined to its
previous PC and VI origin selects H-retail-entry. Zero target hits are usable
only when both title and hangar controls are positive. Remaining at 320 is
H-oracle-route, not a retail null.

Exact commands:

    ./tools/oracle/build_core.sh
    ./tools/oracle/build.sh
    ./tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start --hold-ms 150 --secs 180 --watch-write 0x0:0x800000 --vi-poll --vi-trace --watch-pc 0x800903F0

Capture to `scratch/agent/soak_results/oracle_s4845.log`; interpret only the
positive controls and phase rows from that same file.
