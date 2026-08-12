# NEXT work unit (after s679 maintenance)

HYPOTHESIS-ID: m3-post-exit-fs-stall

Run the corrected, phase-scoped LLE E9 provenance audit for backlog item 1
(legacy -421). Do not alter translation behavior. The probe retains the four
boot controls and targets tasks 8200–8263, which contain the previously
observed post-section-2 E9 divergence. s680's corrected build was not scored:
four rerolls were recovery-silent and the only recovery-active attempt reached
the 1200-second global cap before section 2. Shorten the post-section-2 hold
because the provenance records are printed before that old 180-second hold.

Commands:

    env BUDGET_S=2400 TARGET_PULSED=1 SEC2_SETTLE_S=0 POST_PULSE_HOLD_S=15 MAX_HOLD_S=45 zsh scratch/agent/s670_postsec2_pulse_freeroll.sh

## Competing hypotheses

- **H-f5-dispatch-skip:** the Factor 5 command loop never fetches the aligned
  walker E9s in the target tasks.
- **H-f5-handler-noemit:** the L_1090 fetch occurs, but its handler emits no
  E9 into the output ring.
- **H-dpc-submit-loss:** the handler writes E9 into the output ring, but the
  corresponding byte range is not forwarded to `processRDPLists`.
- **H-walker-nonexecuted-path:** the inline-data-aware walker sees E9s on a
  path that L_1090 never executes; its E9 census cannot explain the plateau.

## Discriminating measurement

For each phase-scoped target task, join the task-numbered walker E9 count to
the L_1090 guest-fetch count, output-ring E9 writes, DPC submit ranges, and
authoritative E9. Same-run controls must show the complete chain for at least
one authoritative E9 task.

- Early tasks 1–4 must print `[e9-prov]` controls. Target records appear only
  for tasks 8200–8263; cross-check them against the same task-numbered
  `[dl-sync-probe2]` records. The task-6500 recovery chain is a positive
  control for the instrument but not evidence about the plateau.
- Walker E9 > guest fetches while each fetched E9 emits and submits:
  H-walker-nonexecuted-path.
- Guest E9 absent at L_1090: H-f5-dispatch-skip.
- Fetch present but no output write: H-f5-handler-noemit.
- Output write present but no deferred submit coverage: H-dpc-submit-loss.
- Submit contains E9 but authoritative decode is absent: refine the existing
  output-ring advance capture around that exact emitted address.
