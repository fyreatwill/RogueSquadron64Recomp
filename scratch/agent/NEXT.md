# NEXT work unit (bounded source audit of the recurring pre-gate crash)

HYPOTHESIS-ID: m3-vi1024-boot-crash-pivot

Do one read-only source audit; do not build or run. The `[vi-arg]` capture
thread stalled for three consecutive iterations: s811, s812, and s813 all
failed to reach 1024, and s812/s813 independently reproduced
`initVideoBootWrapper+2196`, `si_addr=0x3800002CC`, guest PC `0x80001C94`.

## Competing hypotheses

- H-boot-crash-malformed-state: the fault is a legitimate guest-side bad
  pointer/state consumed by the `0x80001C94` return path or its caller.
- H-boot-crash-host-translation: the guest PC is only a stale stamp and the
  host fault comes from a runtime pointer translation or probe-side access.
- H-boot-crash-independent: the two matching signatures are a shared
  last-guest-PC label over a different host instruction, so no single guest
  state explanation is justified.

## Discriminating measurement

Map guest `0x80001C94` to the exact generated instruction and surrounding
host code, then map the faulting host instruction/operand from the two run
logs to its source access. Enumerate every access in the immediate return
path and every caller edge into `initVideoBootWrapper`; compare the mapped
fault operand with `si_addr=0x3800002CC` and the saved register values. A
single concrete malformed guest operand advances H-boot-crash-malformed-state;
an unrelated host/runtime access with a stale guest stamp advances
H-boot-crash-host-translation; non-unique mappings advance
H-boot-crash-independent. Do not add a guard or mitigation from this audit.

## Exact commands

```sh
rg -n "80001C94|initVideoBootWrapper|0x3800002CC|last-guest-pc" \
  ../N64Recomp/RecompiledFuncs/funcs_0.c \
  ../N64Recomp/RecompiledFuncs/funcs_4.c \
  src lib
sed -n '34080,34380p' ../N64Recomp/RecompiledFuncs/funcs_4.c
sed -n '3260,3340p' ../N64Recomp/RecompiledFuncs/funcs_0.c
rg -n "initVideoBootWrapper\(" ../N64Recomp/RecompiledFuncs
```

Use the two s813 logs under `scratch/agent/soak_results/` only as bounded
crash evidence; do not rerun the phase-gated capture until this audit has a
classified result.
