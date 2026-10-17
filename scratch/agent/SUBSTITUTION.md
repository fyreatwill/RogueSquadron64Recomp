The planned fresh PatchesLib source qualification could not run because its
required cross-toolchain was absent. This iteration measured empty results for
`command -v mips64-elf-gcc` and `command -v mips64-elf-ld`; the expected local
candidate paths were also absent. The single experiment that would refute this
explanation is to install or expose the documented MIPS toolchain, rerun those
two commands, and observe both executable paths before building.
