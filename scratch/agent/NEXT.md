# Next work unit (s4482): M3 jal-rs_free class, initWaterSprayParticles

HYPOTHESIS-ID: m3-idiom-class-audit

Classify the one original `jal rs_free` in
`initWaterSprayParticles` (`RecompiledFuncs/funcs_18.c`,
entry `0x80072CF0`, size `0x1D4`, free at `0x80072E40`). The
instruction immediately before the jal is `addu $a0, $s3, $zero`
at `0x80072E3C`. The delay slot is `addu $s0, $v0, $zero` at
`0x80072E44`. It writes `$s0`, not `$a0`. Do not re-audit
`walkDatTreeAndCollectSubtypes` (closed s4481). No runtime run
unless a concrete invalid writer is named and a guard is the
selected fix.

Positive control, same scan: `rg -n "jal\\s+0x80001C98" funcs_18.c`
must still show closed `0x80072B8C` and this site. Also confirm
`0x8006F378` still matches in `funcs_17.c` and `0x8006C8C4` still
matches in `funcs_16.c`. A scan that misses `0x80072B8C` is
invalid. ROM word `0x0C000726` must match `0x80072B8C` and
`0x80072E40`.

A first scan found one `$s3` assignment: `addu $s3, $v0, $zero`
at `0x80072DD4`, after `jal load_asset` (`0x8006488C`). That
jal's delay slot is `addu $a0, $s1, $zero` and does not write
`$v0`. `sw $s3, 0x44($sp)` at `0x80072D50` saves `$s3` and does
not assign it. Confirm this is the only assignment that reaches
the free, what `load_asset` returns, and whether any callee or
caller frees that pointer first.

Hypotheses:
- H-NextClassComplete: `$s3` at `0x80072E40` is the matching
  allocator return, and that pointer is freed once. No guard.
- H-NextClassGap: `$s3` can be a non-allocator value, or a
  pointer a sibling already freed, with the writer named. Only
  then is a guard in scope, and it needs an ORIGIN line.
- H-NextClassUnevaluable: more than one pointer identity can
  reach `$a0`.

Discriminator: every original assignment of `$s3` from the
prologue through the free, plus every callee `jal rs_free` and
every caller argument. Write
`docs/M3-S4482-INIT-WATER-SPRAY-PARTICLES-RS-FREE-AUDIT.md`.
