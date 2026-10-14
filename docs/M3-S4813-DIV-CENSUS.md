# M3 integer-divide idiom census (s4813)

Tool: `tools/census_div.py [RecompiledFuncs dir]`. Scope: every `div`, `divu`,
`ddiv`, `ddivu` in `../N64Recomp/RecompiledFuncs/funcs_*.c`.

Total 427 sites: div 144 (131 register, 13 literal-zero divisor), divu 103
(92/11), ddiv 112 (71/41), ddivu 68 (41/27). Literal-zero total 92, 335 register.

## Literal-zero divisor (92 sites) - proof-of-dead

All 92 sit in four oversized symbols that are data decoded as code:
`audioCompandS16` (44 sites), `__OSGlobalIntMask` (33), `data_gap_800CC3D4` (7),
`static_3_800A2114` (8, overlapping addresses 0x800A2150-0x800A219C with
audioCompandS16). Evidence the sites are data, not compiler output:
- Every sampled site is either `.word 0x0000XXXX` (high half zero, rs=rt=0
  SPECIAL funct encodings 0x1A-0x1F) or `$zero, $zero` operand forms, interleaved
  with `lb $x, -N($zero)` filler and `tgeu $zero,$zero` (`do_break`) words. gcc
  never emits `div $zero,$zero,$zero`.
- The whole 4-symbol set is walked as straight-line fallthrough; no real code
  branches into the middle (single-source: not re-proved with a call-graph walk).

Not independently proved unreachable at runtime (no hit counter was built).
Second line of evidence that they are inert: 427 sites compile and the port runs
title/hangar/mission soaks (s4785, s4788) with 0 SIGFPE.

## Register divisor (335 sites)

MIPS leaves a zero divisor to the preceding `break 7` check; recomp emits the
raw C `/` and `%`. On this host (arm64) hardware `sdiv`/`udiv` by zero returns 0
and does not trap, so no SIGFPE. `DDIV` guards INT64_MIN / -1; 32-bit `div` is
done in 64-bit so INT_MIN / -1 cannot overflow. `DDIVU` is unguarded but
equally non-trapping on arm64.

## Verdict

Class closed on arm64: no guard landed (no named writer, no observed fault).
Residual: an x86-64 build would SIGFPE on any zero-divisor execution; the 92
literal-zero sites would also be compile-time UB. Revisit only if a non-arm64
target is ever built.
