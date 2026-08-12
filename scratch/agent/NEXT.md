# NEXT work unit (after s731 source-tagged L_12A0 capture)

HYPOTHESIS-ID: m3-postsec2-lle-control-flow

Build one regeneration-safe, phase-latched direct-frame depth audit for cap
rows. It must retain the stack-depth at every direct `0x06` → `L_12A0` push,
its matching pop/resume, and synthetic-cap end, then report per-depth push,
pop, resume, and active-frame counts in a bounded task summary. Do not rerun
the unchanged source-tag capture.

## Competing hypotheses

- **H-cap-truncates-valid-stack:** the push/pop surplus is only the bounded
  set of live direct-`0x06` frames when the synthetic cap stops the task; their
  depths remain properly nested and no completed frame is missing a resume.
- **H-direct-lifecycle-leak:** one or more direct `0x06` pushes at a depth do
  not obtain their expected pop/resume before later work reuses or escapes that
  depth, supplying the cap chain.
- **H-counter-alias:** the existing total surplus is an artifact of slot-keyed
  bookkeeping under depth reuse; a depth-local event ledger is balanced.

## Discriminating measurement

In one build, add depth-local counters keyed by the `L_12A0` save depth (not
the reused slot map) and a bounded first/last event ring. At cap, report the
per-depth ledger alongside current depth and the existing source totals. A
balanced nested ledger with only current-depth active frames selects
H-cap-truncates-valid-stack; a completed-depth deficit or resume mismatch
selects H-direct-lifecycle-leak; balanced depth rows despite the old total
surplus select H-counter-alias. The positive control is the existing
section-2 direct-only tag plus matching push/pop/resume in the same run.

## Commands

    rg -n -C 8 'L_12A0:|L_12C4:|L_12DC:|rs64_e9prov_frame_(push|pop|resume)' build/factor5_ucode/factor5_ucode_recompiled.c
    rg -n -C 8 'FRAME_AUDIT_MARKER|L12A0_SOURCE_MARKER|L_12A0|L_12C4|L_12DC' tools/fixup_factor5_ucode.py src/rsp/dpc_bridge.cpp
    python3 tools/fixup_factor5_ucode.py
    cd build && cmake --build . -j8
    env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_E9_PROVENANCE=1 PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 PROBE_KEYS='3:start 7:start 11:start 15:a 100:start 130:start 160:a 190:start 220:a 250:start' zsh ../tools/probe.sh ../scratch/agent/s732_direct_frame_depth 300 2
