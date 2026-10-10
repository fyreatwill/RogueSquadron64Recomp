# Next work unit (s4484): M3 jal-rs_free class, npcShieldUpdate

HYPOTHESIS-ID: m3-idiom-class-audit

Classify the one original `jal rs_free` in `npcShieldUpdate`
(`RecompiledFuncs/funcs_19.c`, entry `0x8007AEF8`, size
`0xD20`, free at `0x8007B23C`). The last `$a0` write before
the jal is `lw $a0, 0x38($s3)` at `0x8007B238`. The delay
slot is `nop` at `0x8007B240`. It does not write `$a0`.
`j 0x8007BBF0` at `0x8007B230` skips this free. Do not
re-audit `downscaleImageHalfResBoxFilter` (closed s4483).
No runtime run unless a concrete invalid writer is named
and a guard is the selected fix.

Positive control, same scan: `rg -n "jal\\s+0x80001C98" funcs_19.c`
must show closed `0x8007A814` and this site. Also confirm
`0x80072E40` still matches in `funcs_18.c`, and `0x8006F378`
still matches in `funcs_17.c`. A scan that misses
`0x8007A814` is invalid. ROM word `0x0C000726` must match
`0x8007A814` and `0x8007B23C`.

A first scan found two `$s3` writes before the free:
`lw $s3, 4($s4)` at `0x8007AF2C`, then `addu $s3, $v0, $zero`
at `0x8007AF70` after `jal rs_malloc` (`0x80001ACC`) at
`0x8007AF68`. The freed word is `0x38($s3)`, not `$s3`
itself. No `sw` with immediate `0x38` appears in this
function before the free. Name the writer of that word,
whether `$s3` at the load is still the malloc return,
whether any callee frees that pointer first, and whether
a later path frees it again.

Hypotheses:
- H-NextClassComplete: the word at `0x38($s3)` is a matching
  allocator return, and that pointer is freed once. No guard.
- H-NextClassGap: that word can be a non-allocator value, or
  a pointer a sibling already freed, with the writer named.
  Only then is a guard in scope, and it needs an ORIGIN line.
- H-NextClassUnevaluable: more than one pointer identity can
  reach `$a0`.

Discriminator: every original assignment of `$s3` from the
prologue through the free, every store that can produce
`0x38($s3)`, plus every callee `jal rs_free` and every
caller argument. Write
`docs/M3-S4484-NPC-SHIELD-UPDATE-RS-FREE-AUDIT.md`.
