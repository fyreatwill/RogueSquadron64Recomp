# Next work unit: runtime A/B of clang-built C heap patch vs shipped asm patch
HYPOTHESIS-ID: patcheslib-c-vs-asm-runtime
Toolchain present: build with `make CC=mips64-elf-gcc LD=mips64-elf-ld` (pass CPPFLAGS include path when building outside patches/; see scratch/patchq).
Fresh C patch recomps+compiles (s5365). Hypotheses: H1 C patch (clang) is behaviourally equal to asm patch on the hangar route; H2 clang codegen diverges (guard semantics differ); H3 C patch never selected because asm-only build is the CMake default.
Discriminator: build both arms in separate build dirs (rule 13), run the s5330 autopilot route to hangar 0x006AB400/VI512, compare heap-guard counters/crash status in one iteration. Positive control: same-run guard counter must fire.
