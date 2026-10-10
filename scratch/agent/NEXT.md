# Next work unit (s4491): M3 jal-rs_free class, handleHUD

HYPOTHESIS-ID: m3-idiom-class-audit

Classify `handleHUD`
(`/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs`,
`.ovl.mission`, entry `0x800C0084`, size `0x1AE0`, jal at
`0x800C1084`). ROM delay is `nop` at `0x800C1088`. The
instruction before the jal is `lw $a0, 0x230($s2)`
(`0x8E440230` at `0x800C1080`). The freed value is that
word, not the incoming argument. Do not re-audit
`audioSeqFree` (closed s4490) or the `.text` destructor
and speech frees closed in s3602–s3607. Those docs cite
the `lw` address; the jal is the next instruction. No
runtime run unless a concrete invalid writer is named
and a guard is the selected fix.

Positive control, same scan: `rg -n "jal\\s+0x80001C98"`
must show closed `0x80083C58` in `funcs_20.c`, closed
`0x80082DC0` in `funcs_20.c`, and this site. Also confirm
closed `0x8007BE50` still matches in `funcs_19.c`. A scan
that misses `0x80083C58` or `0x8007BE50` is invalid. ROM
word `0x0C000726` must match `0x800C1084` and
`0x80083C58`. Disassemble with
`scratch/agent/.venv-splat/bin/python` (rabbitizer).
System python3 has no rabbitizer. ROM:
`./rogue_squadron.z64`. Mission ROM offset is
`vram - 0x7FFFF400`. Menu and cinematic do not use that
difference.

A first scan, not a classification: `$a0` at the jal is
`0x230($s2)`, and the next instruction is `j 0x800C1B20`.
Name `$s2` and every store of that object's `+0x230`.
Do not treat the symbol label as a caller.

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

Discriminator: every original assignment of `$s2` and
of the word at `+0x230` from the prologue through the
free, every caller, and every callee `jal rs_free`.
Write `docs/M3-S4491-HANDLE-HUD-RS-FREE-AUDIT.md`.
