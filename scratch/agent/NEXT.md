# NEXT work unit — complete the port-side slot/status route qualification

HYPOTHESIS-ID: m5-step1-slot-status-consumer

Complete the port-side qualification for the retail slot/status relation. The
retail oracle result is valid and selects `H-RetailSlotConsumer`; the port image
arm reached title but not hangar because logging was too heavy. Use the existing
bounded hooks, no `ROGUESQ_LOG_ALL`, and one 180-second phase-gated image arm.
Do not add a behavior change or mitigation.

## Competing hypotheses

- `H-RetailSlotConsumer`: retail slot/status writes are followed by the
  target consumer; the missing port edge is this contract relation.
- `H-RetailStatusOnly`: retail writes status without a target slot consumer;
  move upstream to the writer's input/dispatch relation.
- `H-PortMatchesRetail`: the qualified port has the same slot/status writer
  and order, so the current symptom is downstream.
- `H-PortRouteStillIncomplete`: the port again fails to reach hangar, so no
  port-side comparison is evaluable.

## Discriminator

The prior oracle watch passed whole-RDRAM and emitted target-phase slot/status
writes plus all four named PC controls. The next port run is valid only if it
reaches `512 @ 0x006AB400`; matching writer/order rows select
`H-PortMatchesRetail`, while another pre-hangar stop selects
`H-PortRouteStillIncomplete` and keeps the missing edge open.

## Exact starting checks

```sh
sed -n '1,220p' tools/oracle/README.md
rg -n 'slot|output|PCM|B40|route|candidate' docs/M5-AUDIO-PLAN.md docs/CURRENT-TRUTH.md
```

Use the already rebuilt Debug target and run:

```sh
zsh scratch/agent/run_s3327_m5_slot_status_port.sh
```

The script uses bounded phase/task/PCM diagnostics, a 180-second watchdog, and
SIGKILL. The expected discriminating outcome is hangar reachability followed
by matching or absent slot/status rows; no behavior change is authorized.
