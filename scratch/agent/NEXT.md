# Next work unit (s4478): M3 jal-rs_free class, load_naboo_starfighter

HYPOTHESIS-ID: m3-idiom-class-audit

Classify the one original `jal rs_free` in `load_naboo_starfighter`
(`RecompiledFuncs/funcs_16.c`, entry `0x8006C780`, generated line 17901,
free at `0x8006C8C4`). The delay slot is `addu $a0, $s2, $zero`.
Do not re-audit `loadCraftShadowTextures` (closed s4477). No runtime run
unless a concrete invalid writer is named and a guard is the selected fix.

Positive control, same scan: `rg -n "jal\\s+0x80001C98" funcs_16.c` must
still show closed `0x8006B814` and the target `0x8006C8C4`. Also confirm
`0x80005268` still matches in `funcs_1.c`. A scan that misses `0x8006B814`
is invalid.

Hypotheses:
- H-NextClassComplete: every assignment of `$s2` that can reach the free is
  the matching allocator return, and it is freed once. No guard.
- H-NextClassGap: `$s2` can be a non-allocator value, or a pointer a sibling
  already freed, with the writer named. Only then is a guard in scope, and
  it needs an ORIGIN line.
- H-NextClassUnevaluable: more than one pointer identity can reach `$a0`.

Discriminator: the complete original assignment list for `$s2` between the
function prologue and `0x8006C8C4`, plus every callee `jal rs_free` and
every caller argument. Write `docs/M3-S4478-LOAD-NABOO-STARFIGHTER-RS-FREE-AUDIT.md`.

The `beql` at `0x8006C8BC` only redirects `$s0` on the taken path; do not
assume it changes `$s2`. Read the producers of `$s2` before concluding.
