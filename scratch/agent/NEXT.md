# NEXT work unit — configured-host PatchesLib validation

HYPOTHESIS-ID: m5-patcheslib-host-validation

Session 3320 established the independent retail target publication edge.
The M5 behavior change remains gated because the capture did not identify a
missing port image-task/output relation. The configured Windows/MIPS host is
still the open dependency; do not repeat its local absence checks here.

## Competing hypotheses

- `H-GuardBuildWorks`: the configured host builds `PatchesLib` successfully.
- `H-GuardSourceFails`: the host reaches the MIPS/build stage and reports a
  patch-source or linker failure.
- `H-GuardHostMissing`: the configured host or required MIPS inputs remain
  unavailable.

## Discriminator

Run the configured-host build once. A successful `PatchesLib` target selects
`H-GuardBuildWorks`; a compiler/linker/source diagnostic after the MIPS stage
selects `H-GuardSourceFails`; inability to invoke the target or find required
MIPS inputs selects `H-GuardHostMissing`.

## Exact command

```sh
cmake --build build --config Debug --target PatchesLib
```

Record the host, target result, and any compiler/linker diagnostic in a new
evidence file. No M5 Step 3 or behavior change is authorized by a failed host
validation.
