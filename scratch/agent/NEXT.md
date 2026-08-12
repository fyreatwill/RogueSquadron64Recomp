# NEXT work unit (after s714: fetch-loop totals conflate triangle runs)

HYPOTHESIS-ID: m3-postsec2-lle-control-flow

Implement one regeneration-safe, phase-gated intra-handler `r17`
reconstruction for backlog item 1. Preserve the s714 live table probe and add
bounded events at each `r17` advance in live Tri entries `0x146C`/`0x1484` and
the TriGen overlay continuation selected by live `0x05`. Build once and run
the same VI-512-gated recipe. The existing live table rows remain the positive
control; an internal event without its matching live table target is invalid.

## Competing hypotheses

- **H-tri-run-conformant:** Tri's observed `+8/+24` fetch-loop deltas are
  composed of documented internal advances and triangle-run continuation.
- **H-tri-advance-mismatch:** an individual internal advance in live
  `0x146C`/`0x1484` differs from the reference command path.
- **H-trigen-advance-mismatch:** the live overlay continuation selected by
  opcode `0x05` has an incorrect internal total, rather than merely returning
  after a multi-command block.

## Discriminating measurement

For each Tri/TriGen sample, sum only the instrumented internal `r17` advances
belonging to its live handler invocation and compare that reconstruction to the
reference command/run path. Positive control: the same phase must print the
live table word selecting `0x146C`, `0x1484`, or the `0x05` overlay path.
Reference-consistent internal steps select H-tri-run-conformant; a wrong
individual internal step selects the matching mismatch hypothesis.

## Commands

    rg -n -C 8 'TriGen|Tri\b|inline data' docs/F5-UCODE-REFERENCE.md
    rg -n -C 8 '^L_146C:|^L_1484:|^L_15AC:|r17 = RSP_ADD32\(r17' \
      build/factor5_ucode/factor5_ucode_recompiled.c
    DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build -j8
    env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
      ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_INLINE_ADVANCE=1 \
      PROBE_PHASE_WIDTH=512 PROBE_KEYS_FROM_PHASE=1 PROBE_KEYS="3:start 7:start" \
      zsh tools/probe.sh scratch/agent/s715_inline_internal 30 1

Append the reconstruction and verdict to `docs/F5-UCODE-REFERENCE.md`. If an
internal advance is wrong, correct the regeneration-safe fixup and rerun the
same phase-gated control in that iteration.
