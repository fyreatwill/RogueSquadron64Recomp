# NEXT work unit

HYPOTHESIS-ID: m3-post-exit-fs-stall

Build one same-run LLE translation provenance audit for item -421. Instrument
the Factor 5 ucode dispatch boundary (through `tools/fixup_factor5_ucode.py`,
not a transient generated-file edit) to count and tag guest E9 command
addresses, and correlate those tags with DPC writes/submits for the same task.
Preserve the s677 authoritative advance positive control. Do not inject, drop,
or change command lengths.

Commands:

    python3 tools/fixup_factor5_ucode.py
    ./submodule-patches/export.sh
    DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build -j8
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

- Guest E9 absent at ucode dispatch: H-f5-dispatch-skip.
- Dispatch present but no output write: H-f5-handler-noemit.
- Output write present but outside/absent from submit: H-dpc-submit-loss.
- Submit contains E9 but authoritative decode is absent: refine the existing
  output-ring advance capture around that exact emitted address.
