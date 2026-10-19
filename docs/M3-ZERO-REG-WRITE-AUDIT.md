# M3 audit: writes to $zero (s5557)

Class: any MIPS instruction whose destination is r0 (lw $zero prefetch idiom,
movz/movn $zero, addu $zero, jalr $zero, mfc1 $zero ...). Risk: generated C
either writes a live `ctx->r0` (poisoning every later "read of zero") or emits
`0 = ...` (does not compile).

Enumeration (N64Recomp/RecompiledFuncs/*.c, 57 files):
- `grep -h 'ctx->r0' *.c | wc -l` = 0. Reads of $zero are emitted as literal 0
  and no statement stores into r0.
- Positive control, same grep form: `ctx->r2 = ` 55248 hits, r4 26180, r3 19629,
  so the pattern/shape is correct and r0 absence is real, not a typo.
- The library compiles, so no `0 = ...` statement exists either.
- Generator side: N64Recomp/src/recompilation.cpp:758 explicitly skips the
  movz/movn rd==0 case (the local patch); other ops are skipped by the
  upstream rd==0 handling, consistent with the 0-hit census.

Verdict: class DEAD BY CONSTRUCTION (0 live sites, 0 to guard). Closed; no
code change. Caveat: the census is on the generated C, not a per-ROM-opcode
count of $zero-destination instructions (not needed - the outcome is observable).
