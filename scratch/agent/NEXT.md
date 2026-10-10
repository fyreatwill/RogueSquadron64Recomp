# Next work unit (s4487): M3 jal-rs_free class, releaseModelAnimSlot

HYPOTHESIS-ID: m3-idiom-class-audit

Classify the first original `jal rs_free` in
`releaseModelAnimSlot`
(`/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_20.c`,
entry `0x80082CFC`, size `0x11C`, free at `0x80082D5C`).
ROM: `lw $a0, 0xC($v0)` at `0x80082D58` (`0x8C44000C`),
jal word `0x0C000726`, delay `addiu $s1, $s1, 1` at
`0x80082D60` (`0x26310001`). The delay does not write
`$a0`. The freed value is the word at `0xC($v0)`. Do not
re-audit `applyCheatCodeFromInput` (closed s4486). Do not
classify the two later jals in this same function
(`0x80082D98`, `0x80082DC0`) in this unit. No runtime run
unless a concrete invalid writer is named and a guard is
the selected fix.

Positive control, same scan: `rg -n "jal\\s+0x80001C98" funcs_20.c`
must show closed `0x80082430` and this site. Also confirm
closed `0x8007BE50`, closed `0x8007B23C`, and closed
`0x8007A814` still match in `funcs_19.c`, `0x80072E40`
still matches in `funcs_18.c`, and `0x8006F378` still
matches in `funcs_17.c`. A scan that misses `0x80082430`
or `0x8007BE50` is invalid. ROM word `0x0C000726` must
match `0x80082430` and `0x80082D5C`. Disassemble with
`scratch/agent/.venv-splat/bin/python` (rabbitizer).
System python3 has no rabbitizer. ROM:
`./rogue_squadron.z64`. `.text` rom = vram - `0x7FFFF400`.

A first scan, not a classification: `$v0` at the load is
`$s1 << 4` plus the word loaded from `-0x5664($at)` at
`0x80082D4C`. `$s1` starts at 0 (`addu $s1, $zero, $zero`
at `0x80082D38`) and the delay increments it after the
jal. The loop back-edge is `bne` at `0x80082D78`. Name
the allocator that wrote `0xC` of that `0x10`-stride
record, whether this loop frees each record once, and
whether `0x80082D98` later frees the same pointer.

Hypotheses:
- H-NextClassComplete: the word at `0xC($v0)` is a
  matching allocator return, and that pointer is freed
  once. No guard.
- H-NextClassGap: that word can be a non-allocator
  value, or a pointer a sibling already freed, with the
  writer named. Only then is a guard in scope, and it
  needs an ORIGIN line.
- H-NextClassUnevaluable: more than one pointer identity
  can reach `$a0`.

Discriminator: every original assignment of the record
base and of `$s1` from the prologue through the free,
every store that can produce the word at `0xC` of that
record, plus every callee `jal rs_free` and every caller
argument. Write
`docs/M3-S4487-RELEASE-MODEL-ANIM-SLOT-RS-FREE-AUDIT.md`.
