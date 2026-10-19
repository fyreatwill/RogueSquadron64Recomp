Single next work unit: run the M6 secondary title-boot plume experiment under
lldb. This is the bounded pivot after two non-joining M4 schema attempts and
the exhausted generated-symbol sweep. Before launching, check the macOS
session is unlocked with `CGSSessionScreenIsLocked`; if locked, do not treat a
nohangar/no-recurrence result as evidence.

Competing hypotheses and discriminator:

1. H1: the reported ~1/7 title-boot plume SIGSEGV is a real remaining defect;
   a looped lldb run will recur and its backtrace will identify the writer.
2. H2: the plume report was an environmental or stale-artifact failure; the
   bounded lldb loop completes without SIGSEGV and reaches the title route.
3. H3: the loop cannot reach a qualified title phase because screen/session
   state or launch infrastructure is invalid; the controls expose that before
   any crash conclusion.

The discriminator is a real SIGSEGV with `si_addr`, lldb backtrace, and guest
writer attribution versus a bounded set of clean title boots with the screen
unlock, launch, title-origin, and crash-marker controls all passing. A clean
run does not reopen M4 or authorize a guard; a recurrence requires naming the
writer before any fix.

Expected checks and run:

    python3 - <<'PY'
    import Quartz
    print(Quartz.CGSSessionScreenIsLocked())
    PY
    rg -n 'plume|lldb|title' scratch/agent/s5452* scratch/agent/s5406* tools | head -100
    sed -n '1,220p' scratch/agent/s5452_plume_lldb_title.sh

Use the existing lldb recipe as the starting point, loop a bounded number of
title boots, capture each run to a path whose final component does not begin
with `.`, and SIGKILL the process group. Do not add a runtime guard based only
on a recurrence; capture the backtrace and writer first.

HYPOTHESIS-ID: m6-title-plume-lldb
