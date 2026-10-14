# Next work unit

HYPOTHESIS-ID: external-retail-entry-boundary

WORK UNIT: retry the parked external retail-entry boundary with one
independent retail-oracle run. Do not modify runtime behavior or treat a
missing oracle core as a retail null.

Competing hypotheses:

* H-retail-entry: the retail run reaches the target external-entry handoff and
  supplies a PC/VI/route witness that can be joined to the port boundary.
* H-retail-route-absent: whole-RDRAM and VI positive controls fire, but the
  selected driven route never reaches the target handoff; this is a route gap,
  not a null about the target.
* H-oracle-setup: the positive control cannot run because the debugger core or
  ROM setup is unavailable; record the concrete setup failure and stop.

DISCRIMINATING MEASUREMENT: the same oracle invocation must show the
whole-RDRAM write positive control, VI polling/trace, and the target
external-entry PC (or an explicit route-absent/setup result). A target PC hit
with its previous PC and VI origin selects H-retail-entry; zero target hits is
usable only when the whole-RDRAM and VI controls are positive.

Exact commands:

    tools/oracle/build_core.sh
    tools/oracle/build.sh
    tools/oracle/build/rs64_oracle --core <debugger-core.dylib> --rom <retail.z64> --secs 180 --watch-write 0x0:0x800000 --vi-poll --watch-pc <external-entry-pc>
