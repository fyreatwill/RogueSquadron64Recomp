# NEXT work unit — compare port route/order with the retail target writer

HYPOTHESIS-ID: m5-route-boundary-port-writer-parity

The retail target phase is valid and actively writes physical
`0x00790000..0x00790C00`, principally from guest PC `0x800078EC`; the
adjacent `0x8008EB00..0x8008ED00` candidate range is not that writer in the
capture. The port image/silent pair is still route-invalid before title, so
this unit measures the port boundary only and makes no audio/output change.

## Competing hypotheses

- `H-PortWriterParity`: both port arms reach a comparable phase-640 route and
  host writeback relation for physical `0x00790000..0x00790C00`, supplying the
  second evidence line for the retail writer relation.
- `H-PortWriterMismatch`: the port reaches its valid phase-640 control but its
  route/order or writeback destination differs from the retail relation.
- `H-PortTargetStillMissing`: controls are live but neither arm reaches a
  target row, leaving the retail writer and port boundary unjoined.
- `H-PortCoverageInvalid`: either arm lacks its dispatch/VI positive control,
  so no parity conclusion is allowed.

## Discriminator

Run both audio arms from one build with phase-gated logs. Require dispatch and
VI positive controls in each arm, phase-640 route/order rows, host writeback
destination/caller/order, and the image-versus-silent distinction. A port row
covering physical `0x00790000..0x00790C00` with matching route ordering
selects `H-PortWriterParity`; a valid phase-640 row with a different
destination/order selects `H-PortWriterMismatch`; missing target rows select
`H-PortTargetStillMissing`; missing controls select
`H-PortCoverageInvalid`.

## Exact command

From the repository root, run the existing same-build pair recipe in both
arms; its script launches and SIGKILLs each game and captures separate logs:

```sh
env ROGUESQ_LOG_ALL=1 zsh scratch/agent/run_s2335_m5_descriptor_filter_boundary.sh s3275_m5_route_writer_parity
```

Use the script's `driver.log`, `stub.log`, and `image.log`. Summarize
`[vi-callers-control]`, `[m5-port-vi-control]`,
`[m5-port-retail-target]`, `[m5-route-transition]`, `[m5-route-order]`,
`[m5-host-boundary]`, and target-span/writeback rows, keeping the positive
controls and phase keys in the same table. Do not run M5 Step 3 from this
result alone; it requires the like-for-like relation plus the existing
guard-build prerequisite.
