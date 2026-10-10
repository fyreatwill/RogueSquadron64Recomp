# Next work unit (s4486): M3 jal-rs_free class, applyCheatCodeFromInput

HYPOTHESIS-ID: m3-idiom-class-audit

Classify the one original `jal rs_free` in
`applyCheatCodeFromInput`
(`/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_20.c`,
entry `0x80082270`, size `0x248`, free at `0x80082430`).
The delay slot is `addu $a0, $s5` at `0x80082434`. It
writes `$a0`, so the freed value is `$s5`. Do not
re-audit `heavyAttachedAudioEmitterNpcHandler` (closed
s4485). No runtime run unless a concrete invalid writer
is named and a guard is the selected fix.

Positive control, same scan: `rg -n "jal\\s+0x80001C98" funcs_20.c`
must show this site. Also confirm closed `0x8007BE50`,
closed `0x8007B23C`, and closed `0x8007A814` still match
in `funcs_19.c`, `0x80072E40` still matches in
`funcs_18.c`, and `0x8006F378` still matches in
`funcs_17.c`. A scan that misses `0x8007BE50` is invalid.
ROM word `0x0C000726` must match `0x8007BE50` and
`0x80082430`. Disassemble with
`scratch/agent/.venv-splat/bin/python` (rabbitizer).
System python3 has no rabbitizer. ROM:
`./rogue_squadron.z64`. `.text` rom = vram - `0x7FFFF400`.

A first scan, not a classification: the only `$s5`
assignment before the free is `addu $s5, $v0` at
`0x800822AC`, after `jal make_crc32_lut` (`0x80082544`)
at `0x800822A4`. The delay of that jal is
`sw $s1, 0x14($sp)` and does not write `$s5`.
`sw $s5, 0x24($sp)` at `0x800822A0` saves the incoming
register. The epilogue `lw $s5, 0x24($sp)` is after the
free. `bne` at `0x80082428` skips the jal
(`L_80082310`). `j 0x80082430` at `0x80082418` also
reaches it; its delay `sw` does not write `$a0` or
`$s5`. Name what `make_crc32_lut` returns, whether that
pointer is an allocator block, whether any callee frees
it first, and whether a later path frees it again.

Hypotheses:
- H-NextClassComplete: `$s5` is a matching allocator
  return, and that pointer is freed once. No guard.
- H-NextClassGap: `$s5` can be a non-allocator value, or
  a pointer a sibling already freed, with the writer
  named. Only then is a guard in scope, and it needs an
  ORIGIN line.
- H-NextClassUnevaluable: more than one pointer identity
  can reach `$a0`.

Discriminator: every original assignment of `$s5` from
the prologue through the free, the return value of
`make_crc32_lut`, plus every callee `jal rs_free` and
every caller argument. Write
`docs/M3-S4486-APPLY-CHEAT-CODE-FROM-INPUT-RS-FREE-AUDIT.md`.
