# NEXT work unit (after s730 static 0x06 audit)

HYPOTHESIS-ID: m3-postsec2-lle-control-flow

Build one regeneration-safe, phase-latched source-attribution trace for every
entry to `L_12A0`. It must distinguish the normal `L_1090` table-1 opcode-06
dispatch from the DMA-fed `L_1298` overlay-table dispatch, and join each entry
to the existing push/unwind/resume frame records. Do not rerun an unchanged
TriGen continuation capture.

## Competing hypotheses

- **H-overlay12a0-unreached:** the retained `DMEM[0x78]=0x12A0` word is never
  selected by a cap-reachable overlay record; all phase-2 `L_12A0` entries are
  ordinary table-1 opcode `0x06` calls.
- **H-overlay12a0-paired:** the overlay table can select `L_12A0`, but its
  frame has the same depth save, child load, EndDL unwind, and parent resume
  as a normal display-list call.
- **H-overlay12a0-unpaired:** an overlay-table entry reaches `L_12A0` without
  a matching frame lifecycle and supplies the open cap chain.

## Discriminating measurement

In one build, retain the phase-2 latch and tag the pending source immediately
before each indirect dispatch: `L_1090` when table-1 target is `0x12A0`, and
`L_1298` when its table target is `0x12A0`. At `L_12A0`, emit the source tag,
opcode/command words, `r17`, `r20`, depth, and `r31`; join it to the existing
phase-scoped frame push/unwind/resume records by task and depth. "Direct only"
selects H-overlay12a0-unreached; an overlay tag followed by the complete frame
pair selects H-overlay12a0-paired; an overlay tag at a cap row with an absent
or mismatched unwind/resume selects H-overlay12a0-unpaired. The positive
control is phase-2 direct-0x06 tagging plus matching push/unwind/resume in the
same run; a branch counter alone is not sufficient.

## Commands

    rg -n -C 8 'L_1090:|L_1298:|L_12A0:|rs64_e9prov_frame_(push|unwind|resume)' build/factor5_ucode/factor5_ucode_recompiled.c
    rg -n -C 8 'FRAME_AUDIT_MARKER|L_1090|L_1298|L_12A0' tools/fixup_factor5_ucode.py
    python3 tools/fixup_factor5_ucode.py
    cd build && cmake --build . -j8
    env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_E9_PROVENANCE=1 ../tools/probe.sh
