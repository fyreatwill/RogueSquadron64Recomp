# UNBLOCK (s5361): route 4 (escalate)
Route 1 (refute): the toolchain gates only fresh PatchesLib source qualification; existing-artifact
qualification stands (CURRENT-TRUTH item 4). No observation makes a compiler unnecessary for fresh compilation.
Route 2 (local): the refuting experiment (`/opt/homebrew/opt/llvm/bin/clang --print-targets | grep -i mips`) was
attempted this iteration. The sandbox denied it (path outside allowed dirs, approval required in non-interactive
mode), so it is unverified, not negative. Installing anything is a human decision regardless.
Route 3 (re-scope): M3/M4/M5 are closed; no un-run unit remains that does not need the blocker.
Refuting experiment (human): run the command above, or `brew install mips64-elf-gcc`.
