# Next: check the PatchesLib toolchain gate

The generated-symbol NEXT item was stale: Session 5336 rechecked
`0x800927B0` and found the semantic name synchronized across generated C,
header, overlay registration, project TOML, fixup mapping, and companion map.
Do not repeat that census or rename by address.

Competing hypotheses and discriminator:

- H1: `mips64-elf-gcc` and `mips64-elf-ld` are available; PatchesLib can be
  qualified with the documented build pipeline.
- H2: one or both tools are absent; qualification is blocked on the external
  toolchain and no source change is authorized.
- H3: tools exist but fail version/target checks; capture the exact failure
  before deciding whether configuration or a human-supplied toolchain is
  needed.

Discriminating measurement: run `command -v mips64-elf-gcc mips64-elf-ld`
and, for any found binaries, run `--version` and `-dumpmachine`. H1 requires
both binaries with a MIPS target; H2 is a missing binary; H3 is an incompatible
or unusable binary. Do not build until H1 is selected.

Commands:

```sh
command -v mips64-elf-gcc mips64-elf-ld
mips64-elf-gcc --version
mips64-elf-gcc -dumpmachine
mips64-elf-ld --version
```

HYPOTHESIS-ID: patcheslib-toolchain-gate
