# NEXT work unit (after s689 frame-caller audit)

HYPOTHESIS-ID: m3-post-exit-fs-stall

Attribute the command that enters `L_12A0` on the repeated cap path. s689
showed the net `push-pop=8` is not eight distinct slots: cap rows reuse slots
0 and 8, and the late pushes return through `r31=0x1088`. That is a dispatcher
return address, not a command identity. Do not alter decoding, submission, or
FULL_SYNC.

## Competing hypotheses

- **H-legitimate-open-chain:** the repeated `L_12A0` entries are valid Factor
  5 DL/branch opcodes with command-consistent target and return PC.
- **H-inline-data-dispatch:** the repeated entries follow an inline-data word
  misread as a DL/branch command, so its opcode/operands contradict the Factor
  5 command table.
- **H-state-corrupt:** the fetched command is valid, but its guest PC or the
  saved target changes without a corresponding decoder transition.

## Discriminating measurement

Extend the regeneration-safe `L_12A0` push marker with current `r17`, `r19`,
and `r20`; retain the first/last slot-0 push after caller `0x1088` and the
slot-8 push. Join those with the existing source-fetch records in
`[e9-prov]`. Keep four boot controls, the section-2 latch, and 64 target rows.
The visible positive control is the existing natural push→pop→resume chain
plus a command-consistent boot DL entry; a counter alone is insufficient.

- Valid 0x06/0x07 DL/branch commands with Factor-5-consistent operands:
  H-legitimate-open-chain supported.
- A non-command/inline-data-shaped opcode at the repeated push:
  H-inline-data-dispatch supported.
- Valid opcode but guest PC/target changes without its matching decoder path:
  H-state-corrupt supported.
- Missing boot/natural controls: reject the run.

## Commands

    # Extend the regeneration-safe L_12A0 marker through
    # tools/fixup_factor5_ucode.py, then build and reuse the phase-gated recipe.
    env DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer zsh -c 'cd build && cmake --build . -j8'
    env BUDGET_S=2400 TARGET_PULSED=1 SEC2_SETTLE_S=8 POST_PULSE_HOLD_S=15 MAX_HOLD_S=45 zsh scratch/agent/s670_postsec2_pulse_freeroll.sh
