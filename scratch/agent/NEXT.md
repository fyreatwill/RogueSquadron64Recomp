# NEXT work unit (mark the reachable 640-row state gate)

HYPOTHESIS-ID: m3-vi640-transition-writer

The s805 source audit found no post-initialization writer that can convert the
mode table's 640 rows into 1024. The smallest reachable discriminator is the
row-selection state: `initVideoSubsystem` uses its configuration bytes,
`applyPendingViChanges` uses pending masks plus selector bytes, and
`swapBufferWithViMode` uses selector bytes before copying to `0x80128C90`.
Add one regeneration-safe, phase-scoped marker at those predicates in the
existing generated-function fixup, then run one bounded VI-640 capture.

## Competing hypotheses

- H-mode-buffer-writer (now disfavored): a direct buffer is initialized or
  overwritten with a 640-only row after the table is available. Prediction:
  the next marker sees a concrete post-table store/copy.
- H-state-gate (selected): a reachable predicate keeps choosing the 640 row.
  Prediction: the marker records stable selector/config bytes and a 640 row
  while the 1024 row remains available in the same table.
- H-missing-dispatch (disfavored): a distinct 1024 publisher cannot reach the
  three direct callers. Prediction: the marker remains silent while the
  existing direct-call controls continue to fire.

## Discriminating measurement

The same-run marker is the discriminator: a post-table 640 store selects
H-mode-buffer-writer; a live predicate selecting the 640 row with no 1024
writer selects H-state-gate; a silent reachable predicate with direct-call
controls still firing selects H-missing-dispatch. The s805 source audit is
already the required concrete-site identification; do not add a mitigation.

## Exact commands

```sh
python3 tools/fixup_game_funcs.py
DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build -j8
env ROGUESQ_LOG_VI_CALLERS=1 ROGUESQ_LOG_VI_SELECTOR=1 \
  PROBE_PHASE_WIDTH=640 PROBE_LEAVE_OK=1 zsh tools/probe.sh
```

Retain the host `osViSetMode` positive control, all three direct-call markers,
the selector marker, and the oracle whole-RDRAM/VI controls. A positive
predicate record with a 640 row and no 1024-row selection advances H-state-gate;
an observed post-table 640 write advances H-mode-buffer-writer; silent
predicate markers with direct-call controls firing advances H-missing-dispatch.
