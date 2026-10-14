# M3 s4818 — trap / break / syscall / cop0 idiom census

Tool: `tools/census_trap.py` (static scan of `../N64Recomp/RecompiledFuncs/funcs_*.c`). Single-source (static), arm64 host.

Runtime semantics (`lib/N64ModernRuntime/librecomp/src/recomp.cpp`): `do_break()` prints and `exit()`s; `cop0_status_write` only models the FR bit (sets/clears `f_odd`, `mips3_float_mode`); `cop0_status_read` returns the shadow `status_reg`.

## do_break: 5635 sites
- 3613 sit in 22 data-as-code functions (>=50% of instruction comments are `.word`/do_break); 1762 of the remainder are in `audioCompandS16` (35889 instrs, 3172 `.word`), the same oversized data-decoded-as-code symbol closed in s4813.
- Real-code remainder (everything outside `audioCompandS16`, `__OSGlobalIntMask`, `data_gap_800CC3D4`): 213 are `break 6`/`break 7` (85 / 128) plus 2 `break 0/1`-shaped.
  `break 7` = divide-by-zero check, `break 6` = INT_MIN/-1 overflow check, both emitted by the compiler directly after a guarding branch (`beq divisor,$zero,...` skip). They execute only when the divisor is 0 / overflow, where retail raises a Break exception (game crash on hardware too). Port = clean exit with the vram printed. Equivalent; not a divergence.
- 45 sites from non-`break` mnemonics in 8 functions:
  - `rspbootTextPreamble` 19 (mtc0/mfc0/j): RSP boot microcode decoded as CPU code, never called by CPU path.
  - `static_3_800A2790` 18, `static_3_800A2114` 2, `static_3_800A2924` 2, `static_4_801096D8` 1 (`movz $zero,...`, all-`$zero` encodings), `data_gap_80040304` 1: `.word` data / gap symbols.
  - `steerOrientationTowardTargetPreamble` 1: a 3-instruction stub `j 0x8005EE74` whose target is inside the *next* symbol (`steerOrientationTowardTarget`, entry+4); the generator cannot branch across symbols so it traps. No call/reference to the Preamble symbol exists in generated code (only its definition); the real function is entered at 0x8005EE70. Dead stub.
  - `filterVoiceSampleBlock` 1 (`scd` at 0x8009D8C0, after misdecoded tail data): already audited s1970/s1971 (PATCH markers present).

## syscall: 81 sites
47 in `audioCompandS16`, 20 in `__OSGlobalIntMask`, 5 in `data_gap_800CC3D4`, 5+2+1 in `static_3_*` data symbols, 1 in `lvj_checkComplexObjectives` (one real-function hit, a single `syscall` word; unreachable-by-shape not proven — single-source). All other sites are data symbols already closed in s4813.

## cop0 status: 23 sites, all benign
1 in `audioCompandS16` (data). The rest are 11 mfc0/mtc0 pairs in the libultra-style matrix helpers (`mat3x4Multiply`, `transformVec3ByMat34`, `rotateVec3ByMat3x3`, `quaternionToMat3x4`, `projectPointToScreen`, `evalCubicSplineAtTime`, `transformAndEmitFaceVertices`): `mfc0 $at,Status; or $at,$at,0x04000000; mtc0 $at,Status` = set FR=1. The runtime models exactly that bit, and `CHECK_FR` asserts depend on it. No other Status bits matter in user-mode recomp.

## Verdict
Trap-instruction class closed on this host: no live path reaches an unintended do_break except the same div-by-zero / overflow conditions that fault on retail. Open (low value, not worth a guard): confirm `lvj_checkComplexObjectives` syscall site is behind a dead branch; add a hit counter only if a `Encountered break at original vram` line ever appears in a soak.

ORIGIN: no mitigation added; census tool + doc only.
