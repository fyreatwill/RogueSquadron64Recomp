# UNBLOCK (session after s5343)
Route taken: 3 (re-scope). Route 1 check: Apple clang --print-targets lists no
MIPS target, so the dependency (a MIPS cross compiler) can't be refuted; the
Makefile hardcodes mips64-elf-gcc/ld. Probing other paths (Homebrew dirs) is
outside the allowed directories; installing a toolchain is a human decision.
The existing patches.elf already qualifies the host-side path, so the fresh
source build is verification-only, not on the critical path. NEXT.md rewritten
to an offline M3 idiom audit; blocker recorded as an open dependency in
CURRENT-TRUTH. Refuting experiment for the escalation case: put
mips64-elf-gcc/ld on PATH and rerun the s5343 command list.
