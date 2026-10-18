# UNBLOCK (s5365): route 4 (escalate)
Route 1: fresh PatchesLib source qualification needs a MIPS compiler by definition; no observation removes that. Existing-artifact qualification already stands.
Route 2: `/opt/homebrew/opt/llvm/bin/clang --print-targets` and `clang --print-targets | grep mips` are both refused by the permission layer (piped commands / path outside allowed dirs) -> still unverified, not negative.
Route 3: CURRENT-TRUTH already records this as a non-blocking open dependency; no remaining work unit avoids it (M3/M4/M5 closed).
Human experiment that refutes the block: run `/opt/homebrew/opt/llvm/bin/clang --print-targets | grep -i mips` yourself. A MIPS line means no install is needed.
