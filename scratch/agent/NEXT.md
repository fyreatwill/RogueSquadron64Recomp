# NEXT work unit (after s713: static dispatch table is DMA/overlay-opaque)

HYPOTHESIS-ID: m3-postsec2-lle-control-flow

Implement one regeneration-safe, phase-gated live dispatch/advance probe for
backlog item 1. In `tools/fixup_factor5_ucode.py`, log each of the six
reference inline-data opcodes' opcode, live table word, handler entry `r17`,
and return-to-fetch `r17`; preserve the existing passive breadcrumbs. Build
once and run a single phase-gated recipe that reaches post-sec2 if possible.
The live table snapshot must print for every selected family before any
mismatch counter is interpreted. s713 found that the static C contains table
loads but no table stores, so a further static pass cannot settle the advance.

## Competing hypotheses

- **H-advance-conformant:** every live inline command has the reference total;
  the capped stream is not caused by a generated Factor 5 pointer bug.
- **H-advance-mismatch:** a live inline command resumes at the wrong address,
  manufacturing the long command chain that reaches the cap.
- **H-live-family-absent:** the driven phase contains none of a selected
  reference opcode; the instrument must report this explicitly rather than
  treating a zero mismatch count as conformance.

## Discriminating measurement

For each observed selected opcode, compare `exit_r17 - entry_r17` to its
reference extra advance (16, 32, conditional 16, 16, 8, 8). Positive control:
the same log line must show the live `DMEM[0xD6]/[0x64]` table word resolving
to the handler being measured; at least one selected family must appear in the
phase. An unequal delta selects H-advance-mismatch; all observed equal with
the table control live supports H-advance-conformant for those families; no
selected opcode selects H-live-family-absent.

## Commands

    rg -n -C 8 'MoveMem|TriGen|Tri\b|TexrectGen|SetOtherMode|inline data|Opcode' \
      docs/F5-UCODE-REFERENCE.md
    rg -n -C 6 'L_1090:|L_10C8:|L_1268:|L_12E4:|L_12EC:|L_14D4:' \
      build/factor5_ucode/factor5_ucode_recompiled.c
    python3 tools/fixup_factor5_ucode.py
    cd build && cmake --build . -j8
    env PROBE_PHASE_WIDTH=512 PROBE_KEYS_FROM_PHASE=1 PROBE_KEYS="3:start 7:start" \
      zsh ../tools/probe.sh

Append the live table and verdict to `docs/F5-UCODE-REFERENCE.md`. If an
advance is wrong, correct the regeneration-safe fixup and rerun the same
phase-gated control in this iteration.
