# Next work unit: qualify the M5 source-construction caller boundary

HYPOTHESIS-ID: m5-source-construction-caller-boundary

Run one rebuilt canonical real-audio/LLE/ungated/solo/spin-yield port and the
independent retail oracle. Keep the guest store, audio waits, caps, predicates,
slot state, and host writeback unchanged. The existing generated hook reports
`ra=0`; the next discriminator must use an independent caller witness rather
than treating that field as a guest fact.

Competing hypotheses and discriminator:

- H-source-caller-same: phase-keyed retail and port executions of the
  `0x800078EC` producer join to the same caller identity and argument shape;
  the zero payload is downstream of a matched producer route.
- H-source-caller-split: the paired phase-keyed caller/argument table differs
  between retail and port, identifying a route/context split before the zero
  store.
- H-route-invalid: either whole-RDRAM control or title/hangar phase gate is
  absent, or the port crashes/stalls before the paired witness is complete.

Before building, verify the existing source-context probe and its positive
control in `docs/debug-trace-env-vars.md`. Build once. Run the oracle first
with the whole-RDRAM watch, exact `0x800078EC` execution watch, and title/
hangar phase buckets; then run the port from `build/` with the source-context
probe and `PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1`. Use the new host
caller/stack or dispatch-context field in the same phase-keyed table; do not
add a standalone counter. A qualified matching table selects H-source-caller-
same; a qualified mismatch selects H-source-caller-split; any missing control
or phase selects H-route-invalid.
