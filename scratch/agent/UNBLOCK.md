# UNBLOCK (s5363): route 4 (escalate)
Route 1 (refute): fresh PatchesLib source qualification needs a compiler by definition; existing-artifact
qualification already stands (CURRENT-TRUTH item 4). No observation makes the compiler unnecessary.
Route 2 (local): searched the four allowed trees (RogueSquadron64Recomp, N64Recomp, rogue_squadron64,
rs64-oracle, depth 4) for `*mips*gcc*`: nothing. `/opt/homebrew/opt/llvm/bin/clang --print-targets` and
listing /opt/homebrew/opt are denied by the sandbox (outside allowed dirs) -> still unverified, not negative.
Route 3 (re-scope): M3/M4/M5 closed; no unit remains that avoids the blocker.
Human experiment: `/opt/homebrew/opt/llvm/bin/clang --print-targets | grep -i mips`; if a MIPS target
shows, tell the loop and it can proceed. Else `brew install mips64-elf-gcc` (human decision) or stop the loop.
