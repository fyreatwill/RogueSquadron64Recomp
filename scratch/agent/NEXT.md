# NEXT work unit (after s681 phase-scope result)

HYPOTHESIS-ID: m3-post-exit-fs-stall

Make the E9 provenance capture genuinely phase-scoped, then run its same-run
audit for backlog item 1 (legacy -421). Do not alter translation behavior.
s681 proved the absolute task window is invalid: it captured 8200–8263, but
the actual section-2 marker was at task 8800. Replace the static target range
with a latch armed by the real section-2 overlay transition and capture its
first 64 post-latch tasks. Also count E9 at every emitted output-ring command,
not just when an emitted range begins with E9; the current `emit` counter is a
range-head proxy.

Commands:

    export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer
    python3 tools/fixup_factor5_ucode.py
    cd build && cmake --build . -j8
    cd .. && env BUDGET_S=2400 TARGET_PULSED=1 SEC2_SETTLE_S=0 POST_PULSE_HOLD_S=15 MAX_HOLD_S=45 zsh scratch/agent/s670_postsec2_pulse_freeroll.sh

## Competing hypotheses

- **H-f5-dispatch-skip:** the Factor 5 command loop never fetches the aligned
  walker E9s in the post-section-2 tasks.
- **H-f5-handler-noemit:** L_1090 fetches E9, but no E9 command is written to
  the output ring.
- **H-dpc-submit-loss:** E9 is written to the output ring but its containing
  range is not forwarded to `processRDPLists`.
- **H-walker-nonexecuted-path:** the walker sees E9s on paths L_1090 does not
  execute.

## Discriminating measurement

For each of the first 64 tasks after the section-2 latch, join walker E9 count
to L_1090 fetches, per-command output E9 writes, containing DPC submit ranges,
and authoritative E9. Same-run controls must show the complete chain for at
least one authoritative E9 task.

- Early tasks 1–4 must print `[e9-prov]` controls. The first target record
  must be after the logged section-2 transition; reject the run otherwise.
  Cross-check every target against its same-task `[dl-sync-probe2]` record.
- Walker E9 > guest fetches while each fetched E9 emits and submits:
  H-walker-nonexecuted-path.
- Guest E9 absent at L_1090: H-f5-dispatch-skip.
- Fetch present but no output write: H-f5-handler-noemit.
- Output write present but no deferred submit coverage: H-dpc-submit-loss.
- Submit contains E9 but authoritative decode is absent: refine the existing
  output-ring advance capture around that exact emitted address.
