# NEXT work unit (s1116)

HYPOTHESIS-ID: retail-oracle-mode-state-route

Run one bounded retail-oracle capture using the already-built debugger core and
the documented eleven-Start hangar-driving schedule. Arm independent controls
and all eight audited writer PCs in the same run:

```sh
tools/oracle/build/rs64_oracle \
  --core "$ORACLE_CORE" --rom build/rogue_squadron.z64 --secs 120 \
  --press 8:start,14:start,20:start,26:start,32:start,38:start,44:start,50:start,56:start,62:start \
  --watch-write 0x0:0x800000 \
  --watch-pc 0x80017CA0,0x80017CB0,0x80017CD0,0x80017CEC,0x8001BA80,0x8001BA88,0x80019D9C,0x80019F60 \
  --vi-trace --pif-trace
```

Use the repository's actual debugger-core path in place of `$ORACLE_CORE` if
needed. Capture output under `scratch/agent/soak_results/`, and use SIGKILL if
a watchdog is required. Do not trust a target null unless whole-RDRAM, PIF,
and VI controls are positive.

Competing hypotheses:

- H-retail-reaches-hangar — the established schedule reaches 512 and produces
  a phase-qualified writer table.
- H-retail-stays-prephase — controls remain positive but retail stays at width
  320/640, so the mode-record caller/argument route is the boundary.
- H-writer-watch-invalid — the run reaches 512 but the PC-watch arm is absent
  or misconfigured; this is refuted if controls are positive and an audited PC
  fires.

Discriminator: VI phase plus positive controls. A 512 hangar phase with audited
PC hits selects H-retail-reaches-hangar; positive controls with no 512/1024
select H-retail-stays-prephase; a positive-control failure invalidates the run
and selects only H-writer-watch-invalid for repair.
