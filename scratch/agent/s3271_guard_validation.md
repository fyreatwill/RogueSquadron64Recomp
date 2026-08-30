# Session 3271 — free-list guard validation

## Work unit

Validate the Session 3270 `patches/heap_guards.c` guard-class change on the
configured host, requiring a successful `PatchesLib` build and then valid-path
plus controlled cyclic-chain validation.

## Competing hypotheses and discriminator

- `H-GuardValidPath`: the alignment and cycle guards compile and preserve the
  valid allocator/queue path.
- `H-GuardCatchesCorruption`: a controlled invalid or cyclic chain returns
  before queue mutation.
- `H-GuardBuildUnavailable`: this checkout still lacks the configured build
  prerequisites.

The discriminator was a successful `PatchesLib` build followed by the two
runtime fixtures. A missing target or prerequisite selects only the local
environment hypothesis; it provides no evidence about guard behavior.

## Measurement

Command:

```text
cmake --build build --config Debug --target PatchesLib
```

Result: exit 2 immediately:

```text
make: *** No rule to make target `PatchesLib'.  Stop.
```

The follow-up audit found `MIPS_TOOLCHAIN_DIR:PATH=E:/mips-toolchain` in
`build/CMakeCache.txt`, no `mips64-elf-gcc` or `mips64-elf-ld` on `PATH`, and
no `RecompiledPatches/` directory. Therefore neither compilation nor either
fixture ran. `H-GuardBuildUnavailable` is selected for this checkout only;
`H-GuardValidPath` and `H-GuardCatchesCorruption` remain unevaluable.
