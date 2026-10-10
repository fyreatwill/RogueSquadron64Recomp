# Next work unit (s4479): M3 jal-rs_free class, runIdleFramesAndLoadSaveData

HYPOTHESIS-ID: m3-idiom-class-audit

Classify the one original `jal rs_free` in `runIdleFramesAndLoadSaveData`
(`RecompiledFuncs/funcs_17.c`, entry `0x8006D900`, generated line 167,
free at `0x8006DA28`). The delay slot is `addu $a0, $s0, $zero`.
Do not re-audit `load_naboo_starfighter` (closed s4478) or `initSaveData`
(closed s3653). s3653 and s3656 mention this function only as a caller
of `initSaveData` (`0x8006DA0C`) and `findManifestEntryByName`
(`0x8006D9D8`). That is not a classification of `0x8006DA28`.
No runtime run unless a concrete invalid writer is named and a guard
is the selected fix.

Positive control, same scan: `rg -n "jal\\s+0x80001C98" funcs_16.c` must
still show closed `0x8006B814` and `0x8006C8C4`. Also confirm `0x80005268`
still matches in `funcs_1.c`, and `0x8006DA28` still matches in
`funcs_17.c`. A scan that misses `0x8006C8C4` is invalid.

`$s0` is a loop counter at `0x8006D924` / `0x8006D984` and is rebound
with `addu $s0, $v0, $zero` at `0x8006DA00`, before `jal initSaveData`
and before the free. Do not treat the counter as the freed pointer
unless that rebind does not dominate on the path that reaches
`0x8006DA28`. `initSaveData` may free its own registers; name whether
any of those frees is this `$s0`.

Hypotheses:
- H-NextClassComplete: every assignment of `$s0` that can reach the free
  is the matching allocator return, and it is freed once. No guard.
- H-NextClassGap: `$s0` can be a non-allocator value, or a pointer a
  sibling already freed, with the writer named. Only then is a guard in
  scope, and it needs an ORIGIN line.
- H-NextClassUnevaluable: more than one pointer identity can reach `$a0`.

Discriminator: the complete original assignment list for `$s0` between
the function prologue and `0x8006DA28`, plus every callee `jal rs_free`
and every caller argument. Write
`docs/M3-S4479-RUN-IDLE-FRAMES-AND-LOAD-SAVE-DATA-RS-FREE-AUDIT.md`.
