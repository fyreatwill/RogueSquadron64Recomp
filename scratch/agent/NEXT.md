# Next: qualify PatchesLib after the MIPS toolchain is supplied

The generated-symbol NEXT item was stale: Session 5336 rechecked
`0x800927B0` and found the semantic name synchronized across generated C,
header, overlay registration, project TOML, fixup mapping, and companion map.
Do not repeat that census or rename by address.

Session 5338 remains blocked on H2: neither required executable is available on
this host. This is an external prerequisite, not a reason to run an
unqualified build or repeat the availability check. Once a human supplies or
installs the toolchain, run the following single work unit.

Competing hypotheses and discriminator:

- H1: `mips64-elf-gcc` and `mips64-elf-ld` are available; PatchesLib can be
  qualified with the documented build pipeline.
- H2: one or both tools are absent; this is the result selected in Session
  5337, and qualification is blocked on the external toolchain.
- H3: tools exist but fail version/target checks; capture the exact failure
  before deciding whether configuration or a human-supplied toolchain is
  needed.

Discriminating measurement after supply: both binaries must resolve, report a
MIPS target, and complete the documented PatchesLib generation/compile/link
pipeline. H1 selects qualification; H3 selects a toolchain/configuration
failure with its exact diagnostic. Do not build while H2 remains true.

Commands:

```sh
command -v mips64-elf-gcc mips64-elf-ld
mips64-elf-gcc --version
mips64-elf-gcc -dumpmachine
mips64-elf-ld --version
```

HYPOTHESIS-ID: patcheslib-toolchain-gate
