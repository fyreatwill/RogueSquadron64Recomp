# NEXT work unit (s2302) — M5 key-on route discriminator

HYPOTHESIS-ID: m5-keyon-new-route-discriminator

## Work unit

Resume the parked M5 key-on tuple contract only through one new route
discriminator. Do not repeat the s2280–s2282 C88 pair as-is. Build one
same-iteration capture containing the retail oracle controls and both port C88
arms, but gate the C88=1 launch on a new port route fingerprint collected
from C88=0. The fingerprint must include every phase transition from the
initial 640 route through title and hangar, the existing B40/route-state
controls, and the first key-on census row; it must be phase-keyed by VI origin,
not elapsed time. Launch C88=1 only after C88=0 has supplied the fingerprint
and reached `512 @ 0x006AB400`. Compare retail tuple fields only if both arms
reach the same hangar window. No pointer/data, branch-state, key-on return,
or mitigation conclusion is authorized on a route-invalid result.

## Competing hypotheses and discriminating measurement

- H-C88RouteLoad: C88 changes the port route fingerprint before the first
  target origin; the two arms diverge in phase or state after identical B40,
  route-state, input, and title controls.
- H-InputPhase: the prior failures are launch-phase sensitivity; the new
  phase-keyed C88=0 fingerprint reaches the target and permits a qualified
  C88=1 arm, while the route fingerprint remains otherwise equivalent.
- H-RouteIntrinsic: both arms still stop at the same initial-640 route after
  the positive controls, so C88 is not selected as the route discriminator.
- H-CoverageInvalid: retail whole-RDRAM/title/hangar controls, the port
  fingerprint controls, or the required common target window fail.

The discriminator is the complete same-build table keyed by arm and VI phase:
`arm,origin,width,route-state-count,B40-count,key-on-count,last-guest-PC`.
Every possible table outcome selects one hypothesis above; it is not a
single breadcrumb or a post-hoc field addition.

## Exact commands

1. Ask ground truth before adding the route instrument:

   `grep -a -E 'positive-control threshold|origin=0x00790400 width=1024|origin=0x006ab400 width=512|pc-field-dump|m5-keyon-pointer-branch' scratch/agent/s2282_m5_c88_staggered_route/retail.log | tail -80`

   The retail whole-RDRAM threshold, title, hangar, and eight-PC controls
   must be present. If they are not, repair the oracle recipe before building.

2. In the existing port route probe, add one bounded phase-keyed fingerprint
   table for both C88 arms and one new driver that launches C88=1 only after
   the C88=0 fingerprint reaches the target. Keep the existing B40, route,
   key-on, input, and independent retail controls. Do not change game logic.

3. Build once if the probe is in generated/runtime code:

   `cmake --build build --config Debug --target RogueSquadron64Recomp`

4. Check and run the single new driver:

   `zsh -n scratch/agent/run_s2302_m5_c88_route_discriminator.sh`

   `zsh scratch/agent/run_s2302_m5_c88_route_discriminator.sh`

Kill every process with SIGKILL from the driver. Report the complete arm × VI
phase table before interpreting the tuple fields. No runtime behavior or
mitigation is authorized by this work unit.
