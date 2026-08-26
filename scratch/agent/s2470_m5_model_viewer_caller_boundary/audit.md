# s2470 M5 model-viewer caller boundary

The independent retail control completed with `oracle_rc=0`. Its whole-RDRAM
watch and driven VI schedule were active; the run reached the driven title and
hangar route controls. This qualifies the port route comparison but does not
claim retail execution of a generated port caller.

The qualified port build used `ROGUESQ_AUDIO_UCODE=0`,
`ROGUESQ_LLE_FORCE=1`, `ROGUESQ_SPIN_YIELD=1`, `ROGUESQ_LLE_UNGATED=1`,
`ROGUESQ_LLE_SOLO=1`, and `ROGUESQ_LOG_M5_PRETARGET=1`. The fixup census found
one generated `runMenuModelViewerScreen(rdram, ctx)` callsite, in
`menuOverlayInit`, at `0x800C5C9C`. The phase-4 live capture emitted:

```
caller=menuOverlayInit callsite=0x800C5C9C
r31=0x00000000 r4=0x00000000 r5=0x00000000
```

The resolver positive control for `0x8009123C` fired 85 times in the same run.
The run then reached the known null dispatch through
`runMenuModelViewerScreen` -> `setupCameraMatrices` ->
`traverseSceneGraphRecursive` -> `convertMat3x4ToN64Mtx` and aborted; the
existing setup-caller rows again showed `r31=0`.

## Discriminator

- H-ModelViewerCallerZero: selected; the sole static caller supplies zero.
- H-ModelViewerCallerNonzero: refuted at this boundary; no nonzero caller row
  was observed.
- H-UnreachableModelViewerCaller: refuted; the sole statically selected caller
  emitted a live phase-4 row.

This closes the `runMenuModelViewerScreen` caller census. It does not identify
the earlier caller that supplies zero to `menuOverlayInit`, and no guard,
stub, dispatch, audio, output, or task-data change was made.
