# NEXT work unit (s2282) — phase-gated C88 route requalification

HYPOTHESIS-ID: m5-keyon-pointer-branch-discriminator

## Work unit

Run one same-build, phase-gated staggered C88 route pair using the established
eleven-Start recipe. Launch the C88=0 control first. Launch C88=1 only after
the control emits `512 @ 0x006AB400`; retain the retail oracle in the same
iteration with its whole-RDRAM, title/hangar, all-eight-PC, and field-bucket
controls. Do not compare key-on fields unless both port arms reach the
hangar. Do not change runtime behavior, key-on returns, divide guards, slot
stores, audio defaults, or LLE route gates.

## Competing hypotheses and discriminating measurement

- **H-C88-route:** C88 changes route behavior. If C88=0 reaches the gated
  hangar and C88=1 then fails before the same target, C88 is a route
  antecedent; no key-on field comparison is allowed.
- **H-RouteLoad:** the concurrent pair was load-sensitive. If C88=0 reaches
  the hangar and the staggered C88=1 arm also reaches title/hangar, the C88
  value is not the route discriminator at this scope and the target join can
  use the qualified arms.
- **H-CoverageInvalid:** the C88=0 control, the retail controls, or the
  delayed C88=1 arm lacks its required phase gate. Any missing gate leaves the
  key-on pointer/data and branch-state hypotheses unevaluable.

The single discriminating table is keyed by `arm(C88), phase, origin, width`
and records `launch_gate, title_gate, hangar_gate, last_phase,
timeout_or_crash, keyon_rows_by_PC, b40_route_control, route_state_control`.
The retail acceptance row remains whole-RDRAM >=10,000 writes, title/hangar,
all eight transfer PCs, and `overflow=0` for every field bucket. A qualified
key-on comparison requires both C88 arms to reach `512 @ 0x006AB400`.

## Exact commands

1. Create `scratch/agent/run_s2282_m5_c88_staggered_route.sh` with
   `apply_patch`. It must launch the retail oracle and C88=0 arm, poll the
   explicit phase-origin line, launch C88=1 only after the first C88=0 hangar
   gate, enforce 150-second oracle and 220-second per-port deadlines, SIGKILL
   every remaining process, and print the complete table. Use distinct logs
   for both arms and retain `PROBE_PHASE_WIDTH=1024` and
   `PROBE_KEYS_FROM_PHASE=1`.
2. Run the driver from the repository root:

```sh
zsh scratch/agent/run_s2282_m5_c88_staggered_route.sh s2282_m5_c88_staggered_route
```

3. Summarize the retail controls and both phase tails with bounded grep/tail
   commands. If either launch or hangar gate is absent, record
   H-CoverageInvalid and do not interpret any key-on null or off-target row.
