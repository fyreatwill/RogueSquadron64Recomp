# NEXT work unit (s2456) — audit the pre-phase null-dispatch boundary

HYPOTHESIS-ID: m5-prephase-null-dispatch

## Work unit

Perform one bounded static call/symbol audit of the pre-phase
`get_function(0)` abort from `convertMat3x4ToN64Mtx` at guest PC `0x80001F88`,
then ask the retail oracle whether the corresponding guest PC executes on the
driven route. Do not change behavior or add a diagnostic field.

## Competing hypotheses and discriminator

- H-NullMissingGeneratedTarget: the port abort is a generated callsite whose
  target should resolve to a real retail/decomp symbol but is absent from the
  generated function map.
- H-NullLegitimateZero: the callsite intentionally resolves to zero or a
  runtime no-op, and the abort is a runtime policy mismatch.
- H-NullBadGuestData: the generated caller computes or loads zero from a
  corrupted/unsupported guest data path rather than naming a missing symbol.

The discriminator is one complete table of every generated/runtime
`get_function` callsite: guest PC, lookup expression/target, caller symbol,
and matching retail/decomp address range, plus a retail oracle row for
`0x80001F88` with whole-RDRAM and GPR controls. A real mapped target at the
crashing callsite selects H-NullMissingGeneratedTarget; a complete zero-target
contract with retail execution selects H-NullLegitimateZero; a non-symbol-
derived zero/data load selects H-NullBadGuestData. Missing oracle controls or
no retail target-PC row is a non-result.

## Exact commands

1. First enumerate the static table without editing or building:

   `rg -n "get_function\\(|convertMat3x4ToN64Mtx|0x80001F88|Failed to find function" src lib RecompiledFuncs tools`

   Read only bounded windows around each hit and record the complete table in
   `scratch/agent/s2456_m5_null_dispatch/audit.md`.

2. Ask the retail oracle for ground truth in one run:

   `tools/oracle/build/rs64_oracle --core "/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib" --rom "/Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64" --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 60 --watch-write 0x0:0x800000 --watch-pc 0x80001F88 --pc-phase-log-width 0x6ab400:512 --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start > scratch/agent/s2456_oracle.log 2>&1`

   Require `[gpr-ctl]`, whole-RDRAM hits, and report whether the target PC
   executes in the driven route before interpreting the static table.

3. Do not rerun the 120-second port provenance capture until this boundary is
   classified; the current route aborts at 4.3s before its phase gate.
