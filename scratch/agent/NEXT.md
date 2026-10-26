# Optional MIPS source-to-ELF patch qualification (G5 sweep complete, s6268)
HYPOTHESIS-ID: mips-c-patch-qualification
Goal: with mips64-elf-gcc 14.2, build a trivial C patch into patches.elf, load it, and qualify with the two-arm discipline (patched vs unpatched, same phase-gated run, positive control that the patch visibly fires). Pick a harmless target (e.g. a counter incremented in a hot function) and read the counter. If nothing applicable, take M6 mission endurance on an untested route.
