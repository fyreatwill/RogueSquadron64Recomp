1. The planned M5 route-preparation unit could not produce its discriminating
   title/hangar table because the required retail execution watch at
   `0x80019CD8` slowed the 45-second oracle capture to boot-only rows.

2. This iteration's fixed capture visibly passed the whole-RDRAM positive
   control at 10,000 callbacks and logged 64 executions of `0x80019CD8`, but
   every route row was `320 @ 0x006DD280`; no target VI phase was observed.
   The process was SIGKILLed after it remained in the non-target phase. The
   evidence is recorded in `scratch/agent/s2975_m5_route_oracle/RESULTS.md`.

3. The single experiment that would refute this explanation is the same
   oracle capture with a phase-aware route-PC breakpoint that is armed only
   after a target VI boundary, while retaining the whole-RDRAM positive
   control in that same run.
