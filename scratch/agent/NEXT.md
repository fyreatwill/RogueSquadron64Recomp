# Next work unit (s4485): M3 jal-rs_free class, heavyAttachedAudioEmitterNpcHandler

HYPOTHESIS-ID: m3-idiom-class-audit

Classify the one original `jal rs_free` in
`heavyAttachedAudioEmitterNpcHandler`
(`/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_19.c`,
entry `0x8007BC18`, size `0x650`, free at `0x8007BE50`).
The last `$a0` write before the jal is `lw $a0, 0x38($s2)`
at `0x8007BE4C`. The delay slot is `nop` at `0x8007BE54`.
It does not write `$a0`. `j 0x8007C240` at `0x8007BE44`
(delay `nop` at `0x8007BE48`) skips this free. Do not
re-audit `npcShieldUpdate` (closed s4484). No runtime run
unless a concrete invalid writer is named and a guard is
the selected fix.

Positive control, same scan: `rg -n "jal\\s+0x80001C98" funcs_19.c`
must show closed `0x8007A814`, closed `0x8007B23C`, and this
site. Also confirm `0x80072E40` still matches in `funcs_18.c`,
and `0x8006F378` still matches in `funcs_17.c`. A scan that
misses `0x8007A814` or `0x8007B23C` is invalid. ROM word
`0x0C000726` must match `0x8007B23C` and `0x8007BE50`.
Disassemble with `scratch/agent/.venv-splat/bin/python`
(rabbitizer). System python3 has no rabbitizer. ROM:
`./rogue_squadron.z64`. `.text` rom = vram - `0x7FFFF400`.

A first scan, not a classification: `$s2` is loaded from
`4($s3)` at `0x8007BC48`, then replaced by `addu $s2, $v0`
at `0x8007BC7C` after `jal rs_malloc` (`0x80001ACC`) at
`0x8007BC74`. Size `0x180` is `addiu $a0, $zero, 0x180` at
`0x8007BC6C`. Flags 0 are `addu $a1, $zero` at `0x8007BC70`,
before the jal. The delay slot `addu $s1, $a2` at
`0x8007BC78` does not write `$a0`. `sw $s2, 4($s3)` at
`0x8007BC8C` publishes that return. `addiu $a0, $s2, 0x38`
at `0x8007BCE0` is the delay of the other
`allocateNpcMeshVertexBuffer` call (`jal 0x8007A870` at
`0x8007BCDC`). The freed word is `0x38($s2)`, not `$s2`
itself. Name the writer of that word, whether `$s2` at the
load is still that malloc return, whether any callee frees
that pointer first, and whether a later path frees it again.

Hypotheses:
- H-NextClassComplete: the word at `0x38($s2)` is a matching
  allocator return, and that pointer is freed once. No guard.
- H-NextClassGap: that word can be a non-allocator value, or
  a pointer a sibling already freed, with the writer named.
  Only then is a guard in scope, and it needs an ORIGIN line.
- H-NextClassUnevaluable: more than one pointer identity can
  reach `$a0`.

Discriminator: every original assignment of `$s2` from the
prologue through the free, every store that can produce
`0x38($s2)`, plus every callee `jal rs_free` and every
caller argument. Write
`docs/M3-S4485-HEAVY-ATTACHED-AUDIO-EMITTER-NPC-HANDLER-RS-FREE-AUDIT.md`.
