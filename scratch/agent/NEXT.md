# Next work unit (s4483): M3 jal-rs_free class, downscaleImageHalfResBoxFilter

HYPOTHESIS-ID: m3-idiom-class-audit

Classify the one original `jal rs_free` in
`downscaleImageHalfResBoxFilter` (`RecompiledFuncs/funcs_19.c`,
entry `0x8007A260`, size `0x60C`, free at `0x8007A814`).
The last `$a0` write before the jal is `addu $a0, $s5, $zero`
at `0x8007A7F8`. The delay slot is `sb $v1, 1($v0)` at
`0x8007A818`. It does not write `$a0`. Do not re-audit
`initWaterSprayParticles` (closed s4482). No runtime run
unless a concrete invalid writer is named and a guard is the
selected fix.

Positive control, same scan: `rg -n "jal\\s+0x80001C98" funcs_19.c`
must show this site. Also confirm `0x80072E40` and closed
`0x80072B8C` still match in `funcs_18.c`, and `0x8006F378`
still matches in `funcs_17.c`. A scan that misses `0x80072E40`
is invalid. ROM word `0x0C000726` must match `0x80072E40` and
`0x8007A814`.

A first scan found one `$s5` write before the free:
`addu $s5, $v0, $zero` at `0x8007A320`, after `jal rs_malloc`
(`0x80001ACC`) at `0x8007A318`. That jal's delay slot is
`addu $a0, $s0, $zero`. The next use is `zmemcpy` at
`0x8007A32C` (`$a0 = $s5`, `$a1 = $s2`, `$a2 = $s0`). Confirm
this is the only assignment that reaches the free, what
`$s0` is at the malloc, whether any callee clobbers `$s5`
or frees that pointer first, and whether a later path frees
it again.

Hypotheses:
- H-NextClassComplete: `$s5` at `0x8007A814` is the matching
  allocator return, and that pointer is freed once. No guard.
- H-NextClassGap: `$s5` can be a non-allocator value, or a
  pointer a sibling already freed, with the writer named. Only
  then is a guard in scope, and it needs an ORIGIN line.
- H-NextClassUnevaluable: more than one pointer identity can
  reach `$a0`.

Discriminator: every original assignment of `$s5` from the
prologue through the free, plus every callee `jal rs_free` and
every caller argument. Write
`docs/M3-S4483-DOWNSCALE-IMAGE-HALF-RES-BOX-FILTER-RS-FREE-AUDIT.md`.
