# NEXT work unit (s2886) — M5 route/contract discriminator

HYPOTHESIS-ID: m5-route-contract-discriminator

The M5 design gate is now current in `docs/M5-AUDIO-PLAN.md`; no audio
behavior change is authorized by the inventory alone.

## Work unit

Run one ground-truth-first M5 discriminator that can repair or replace the
pre-title route qualification before interpreting downstream audio rows. The
generated-symbol campaign is complete through `0x800C0000`; do not reopen it
unless a new placeholder appears.

## Competing hypotheses and discriminator

- H-RouteState: a distinct retail writer/state relation predicts the route
  transition and can be compared against the port.
- H-RouteInvalid: the same-build image/silent port pair again stops before the
  target phase, leaving downstream audio unevaluable.
- H-PostDispatch: both arms qualify title/hangar and a named task/service/
  slot/PCM relation selects the next M5 contract edge.

The single discriminating measurement is one phase-keyed table containing the
whole-RDRAM retail positive control, the selected retail writer/state event,
matching port route controls, and all downstream task/service/slot/PCM rows.
Only a target-phase writer equivalence or a qualified post-dispatch gap may
select a behavior change; pre-title nulls remain unevaluable.

## Exact next commands

1. Read the current M5 plan and identify one distinct writer-backed
   post-dispatch/state discriminator; ask the retail oracle first and arm its
   whole-RDRAM positive control.
2. Add all retail and port arms/counters in one instrumented build, phase-gated
   on VI transitions (`PROBE_PHASE_WIDTH=1`, `PROBE_KEYS_FROM_PHASE=1`).
3. Run the oracle and both same-build port arms concurrently from `build/`,
   capture to a non-dot final path, and SIGKILL the process group.
4. Record the complete table and either name the legitimate writer/ordering
   edge or leave the route invalid; do not land a mitigation.

## Expected outcomes

- Retail target-phase writer plus port equivalence authorizes one contract
  change.
- A pre-title stop selects H-RouteInvalid and leaves downstream audio nulls
  unevaluable.
- Qualified target-phase task/audio divergence selects the named next edge;
  otherwise no behavior change is authorized.
