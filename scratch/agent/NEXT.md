# NEXT work unit (after s679 maintenance)

HYPOTHESIS-ID: m3-post-exit-fs-stall

Run the completed, phase-scoped LLE E9 provenance audit for backlog item 1
(legacy -421). Do not
alter translation behavior. The s678 build already contains the persistent
probe and the harness already exports `ROGUESQ_LOG_E9_PROVENANCE=1`.

Commands:

    env BUDGET_S=1200 TARGET_PULSED=1 zsh scratch/agent/s670_postsec2_pulse_freeroll.sh

## Competing hypotheses

- **H-f5-dispatch-skip:** the Factor 5 command loop never dispatches aligned
  guest E9 commands in the target tasks.
- **H-f5-handler-noemit:** guest E9 dispatches, but its handler emits no E9
  into the output ring.
- **H-dpc-submit-loss:** the handler writes E9 into the output ring, but the
  corresponding byte range is not forwarded to `processRDPLists`.

## Discriminating measurement

For each phase-scoped target task, join guest walker E9 addresses to ucode
dispatch hits, output-ring E9 writes, DPC submit ranges, and authoritative E9.
Same-run controls must show the complete chain for at least one authoritative
E9 task.

- Early tasks 1–4 must print `[e9-prov]` controls. Target records appear only
  from task 6500 onward; use completed section-2/advance records as the
  independent positive control.
- Guest E9 absent at ucode dispatch: H-f5-dispatch-skip.
- Dispatch present but no output write: H-f5-handler-noemit.
- Output write present but no deferred submit coverage: H-dpc-submit-loss.
- Submit contains E9 but authoritative decode is absent: refine the existing
  output-ring advance capture around that exact emitted address.
