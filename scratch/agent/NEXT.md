# NEXT work unit (after s732 direct-frame depth ledger)

HYPOTHESIS-ID: m3-postsec2-lle-control-flow

Build one regeneration-safe, phase-latched correlation trace between the
`L_1DB0` write of `DMEM[0x152]=0` and active depth-0 `L_12A0` overwrites.
Keep the current depth ledger and report bounded first/last reset-active and
reuse-push pairs for synthetic-cap tasks. Do not add a mitigation.

## Competing hypotheses

- **H-l1db0-reset-writer:** the TriGen continuation's sole generated
  `DMEM[0x152]=0` store occurs while depth 0 is active and immediately precedes
  each depth-0 reuse, so it is the concrete writer behind the lifecycle leak.
- **H-reset-is-boundary:** `L_1DB0` resets occur only with no active direct
  frame; the observed reuse has a different writer or control-flow cause.
- **H-host-ledger-ordering:** resets and reuses occur, but do not pair in one
  task sequence; the depth ledger's active state is not a causal ordering fact.

## Discriminating measurement

In one build, inject a callback immediately before the sole `L_1DB0`
`RSP_MEM_B(0X52, r18) = 0` store, passing the old byte and current `r17`.
The host must retain a bounded first/last pair ring of reset-active events and
the next depth-0 reuse push, reset counters per task, and print it only for
section-2 synthetic-cap rows. Reset-active count equal to reuse count with
ordered pairs selects H-l1db0-reset-writer; zero reset-active selects
H-reset-is-boundary; unpaired events select H-host-ledger-ordering. Positive
control: same run still has direct-only, balanced boot `0x06` rows and the
existing cap depth ledger reproduces depth-0 reuse.

## Commands

    rg -n -C 8 'L_1DB0:|RSP_MEM_B\(0X52, r18\) = 0|L_12A0:|rs64_e9prov_frame_push' build/factor5_ucode/factor5_ucode_recompiled.c
    rg -n -C 8 'FRAME_AUDIT_MARKER|L12A0_SOURCE_MARKER|L_1DB0|RSP_MEM_B\(0X52' tools/fixup_factor5_ucode.py src/rsp/dpc_bridge.cpp
    python3 tools/fixup_factor5_ucode.py build/factor5_ucode/factor5_ucode_recompiled.c
    cd build && cmake --build . -j8
    env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_E9_PROVENANCE=1 PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 PROBE_KEYS='3:start 7:start 11:start 15:a 100:start 130:start 160:a 190:start 220:a 250:start' zsh ../tools/probe.sh ../scratch/agent/s733_depth_reset_order 300 2
