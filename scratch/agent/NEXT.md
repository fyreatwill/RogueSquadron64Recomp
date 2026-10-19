Single next work unit: run one bounded in-process crash-handler loop on the
qualified default (HLE) route, without lldb, to determine whether the plume
title-boot question is reachable outside the debugger. The corrected default
lldb loop had a passing control but title origin 0/4 after 120 seconds; all
attempts remained at phase 3, width 640, origin 0x696100.

Competing hypotheses and discriminator:

1. H1: the plume defect recurs outside lldb; an in-process crash marker or
   `[plume-null-color-attachment]` appears after a title-origin control.
2. H2: no-lldb boots reach `origin=0x00790400` and complete cleanly; the
   plume recurrence is not reproduced in this qualified sample.
3. H3: the default route itself fails to reach title without lldb; all attempts
   remain at `origin=0x696100` through the same gate.

The discriminator is the per-attempt title-origin count in a no-lldb run:
only attempts that reach `origin=0x00790400` are evidence for H1/H2. Preserve
the in-process crash marker and any plume breadcrumb; no guard is authorized
from a recurrence without naming the writer. If H3 wins, stop repeating this
title recipe and inspect the first non-debugger route blocker.

Ground truth already checked this iteration: `/usr/sbin/ioreg -n Root -d1`
reported an on-console session and no `CGSSessionScreenIsLocked=Yes`. The
Python Quartz module is unavailable.

Exact run shape: create a new self-contained recipe from
`scratch/agent/s5577_plume_lldb_default4.sh`, remove the lldb attach/control,
launch four no-lldb attempts from `build/` with the same `COMMON` variables,
wait up to 120 seconds for `origin=0x00790400` or an in-process crash marker,
then SIGKILL the game after each attempt. Capture under
`scratch/agent/soak_results/`.

HYPOTHESIS-ID: m6-title-plume-lldb
