Single next work unit: run one bounded lldb-attach loop on the qualified
default (HLE) route to determine whether the plume title-boot question is
reachable under the debugger. The prior forced-LLE attach loop was
non-qualifying: lldb control passed, but title origin was 0/8 and all attempts
remained in the 640 phase.

Competing hypotheses and discriminator:

1. H1: default-route title boots are debugger-reachable; a SIGSEGV stop or
   `[plume-null-color-attachment]` identifies the remaining plume writer.
2. H2: default-route boots reach `origin=0x00790400` and complete cleanly;
   the plume recurrence is not reproduced in this qualified sample.
3. H3: attaching lldb itself prevents the qualified route from reaching title;
   the injected SIGSEGV control passes but title-origin positive control is 0/4.

The discriminator is the same-run control plus per-attempt title-origin count:
only attempts that reach `origin=0x00790400` are evidence for H1/H2. Any lldb
SIGSEGV stop gets its `bt 30`, registers, and `si_addr` preserved; no guard is
authorized from a recurrence without naming the writer. If H3 wins, stop
rerunning lldb and use the in-process crash handler on the next unit.

Ground truth already checked this iteration: `/usr/sbin/ioreg -n Root -d1`
reported an on-console session and no `CGSSessionScreenIsLocked=Yes`. The
Python Quartz module is unavailable.

Exact run shape: copy the fixed recipe
`scratch/agent/s5576_plume_lldb_title8_fixed.sh` to a new scratch recipe,
remove `ROGUESQ_LLE_FORCE=1`, `ROGUESQ_LLE_UNGATED=1`, and
`ROGUESQ_LLE_SOLO=1` from `COMMON`, set `N=4`, retain the injected SIGSEGV
lldb control, run from `build/`, and SIGKILL both game and lldb PIDs after
each attempt. Capture under `scratch/agent/soak_results/`.

HYPOTHESIS-ID: m6-title-plume-lldb
