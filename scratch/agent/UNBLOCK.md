# UNBLOCK (s5359): route 4 (escalate)
Route 1 (refute): the toolchain only gates fresh PatchesLib source qualification; existing-artifact
qualification stands (CURRENT-TRUTH item 4). No observation makes a compiler unnecessary for *fresh*
compilation. Re-checked: mips64-elf-gcc, mips-linux-gnu-gcc, zig, rustc, llvm-mc absent; Apple clang
--print-targets lists no MIPS. /opt/homebrew/bin/ld.lld exists (linker only, no compiler).
Route 2 (local): listing /opt/homebrew/opt and bin is blocked by the sandbox (outside allowed dirs), so
a Homebrew LLVM with a MIPS backend could not be checked; installing is a human decision anyway.
Route 3 (re-scope): s5356 already re-scoped to the M3 idiom audit, which finished (177 jump tables,
0 defects). M3/M4/M5 are closed; no remaining un-run unit that does not need the blocker.
Refuting experiment: run `/opt/homebrew/opt/llvm/bin/clang --print-targets | grep -i mips` (or
`brew install mips64-elf-gcc`). If a MIPS-capable clang exists, fresh PatchesLib qualification can proceed
with `clang --target=mips64 -c` + the existing ld.lld.
