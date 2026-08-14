# NEXT work unit (s992)

HYPOTHESIS-ID: m4-zero-shade-writer

## One work unit

Implement and dry-run one regeneration-safe, env-gated pass in
`../N64Recomp/fixup_game_funcs.py` that wraps only generated ordinary store
statements for the two shared phase-4/phase-6 pages. It must record guest PC,
width, physical address, and phase immediately before assignment. Do not edit
generated files by hand, change shade behavior, or add a guard.

## Competing hypotheses and discriminating measurement

- H-generated-target: exact target overlap is found with a matching guest PC.
- H-generated-unrelated: only non-target writes on the shared pages match.
- H-runtime-copy: no generated-store overlap is found.

Discriminating measurement: fixup match count first, then same-run positive
controls plus phase-4/phase-6 exact-target versus non-target generated-store
records. Exact-target records select H-generated-target; only non-target
records select H-generated-unrelated; zero generated records leaves
H-runtime-copy selected.

## Exact commands

Before editing, inspect the existing phase/page-fault hooks and fixup path:

`rg -n "vtx-write-fault|PROBE_PHASE_WIDTH|PROBE_KEYS_FROM_PHASE|MEM_[BHW]|MEM_W" src ../N64Recomp tools`

Add the pass to the fixup script, verify a nonzero match count on regenerated
output, then build and run one capture:

`env ROGUESQ_LOG_VTX_GENERATED_WRITES=1 ROGUESQ_LLE_FORCE=1 PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 PROBE_PHASE_TIMEOUT=180 PROBE_START=0 PROBE_KEYS='20:start' zsh tools/probe.sh scratch/agent/probe_s992 180 1`

Require F5/shade, all-DMA, and the new generated-store positive controls. If
the fixup pass cannot distinguish assignments, stop with its match-count
measurement rather than inserting a temporary generated-file probe.
