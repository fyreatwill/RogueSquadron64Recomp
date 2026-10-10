# Next work unit (s4490): M3 jal-rs_free class, audioSeqFree

HYPOTHESIS-ID: m3-idiom-class-audit

Classify `audioSeqFree`
(`/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_20.c`,
entry `0x80083C50`, jal at `0x80083C58`). ROM delay is
`nop` at `0x80083C5C`. The prologue saves `$ra` and
does not write `$a0`, so the freed value is the
incoming argument. Do not re-audit `0x80082DC0`
(closed s4489), `0x80082D98` (closed s4488), or
`0x80082D5C` (closed s4487). No runtime run unless a
concrete invalid writer is named and a guard is the
selected fix.

Positive control, same scan: `rg -n "jal\\s+0x80001C98" funcs_20.c`
must show closed `0x80082430`, closed `0x80082D5C`,
closed `0x80082D98`, closed `0x80082DC0`, and this
site. Also confirm closed `0x8007BE50`, closed
`0x8007B23C`, and closed `0x8007A814` still match in
`funcs_19.c`, `0x80072E40` still matches in
`funcs_18.c`, and `0x8006F378` still matches in
`funcs_17.c`. A scan that misses `0x80082DC0` or
`0x8007BE50` is invalid. ROM word `0x0C000726` must
match `0x80082DC0` and `0x80083C58`. Disassemble with
`scratch/agent/.venv-splat/bin/python` (rabbitizer).
System python3 has no rabbitizer. ROM:
`./rogue_squadron.z64`. `.text` rom = vram -
`0x7FFFF400`.

A first scan, not a classification: jal word
`0x0C020F14` occurs zero times in the ROM, and the
32-bit constant `0x80083C50` occurs zero times.
`audioSeqMallocZero` (`0x80083C28`) jumps to
`0x80083C38`, calls `rs_malloc`, and returns at
`0x80083C48`. It does not fall into `audioSeqFree`.
Find every `jalr` or function-pointer path that can
still enter `0x80083C50`, and name `$a0` on each one.
If none exists, say whether an unreferenced free is
H-NextClassComplete (no path reaches the jal) or
unevaluable.

Hypotheses:
- H-NextClassComplete: every path that reaches the
  jal passes one allocator return, freed once, or no
  path reaches the jal. No guard.
- H-NextClassGap: a reached path passes a
  non-allocator value, or a pointer already freed,
  with the writer named. Only then is a guard in
  scope, and it needs an ORIGIN line.
- H-NextClassUnevaluable: more than one pointer
  identity can reach `$a0`, or a possible indirect
  entry cannot be accepted or rejected.

Discriminator: every original assignment of `$a0`
from the prologue through the free, every caller or
indirect entry, and every callee `jal rs_free`. Write
`docs/M3-S4490-AUDIO-SEQ-FREE-RS-FREE-AUDIT.md`.
