# Next work unit (s4498): M3 jal-rs_free class, model-animation reset

HYPOTHESIS-ID: m3-idiom-class-audit

Classify the `jal rs_free` in `reset_and_free_model_animations`
(`.ovl.mission`, entry `0x800F9F6C`, size `0x64`) at
`0x800F9F94`. ROM delay is `nop` at `0x800F9F98`. That delay
does not write `$a0`. Re-verify the delay. Do not reclassify
`0x800EED50` (closed s4497). The nop was observed while naming
this site; it is not a classification.
No runtime run unless a concrete invalid writer is named and
a guard is the selected fix.

Positive control, same scan: mission ROM word `0x0C000726`
must be present at closed `0x800EED50`, closed `0x800EED48`,
and closed `0x800EC564`. `.text` word at closed `0x8007BE50`
must match. A scan that misses `0x800EED50` or `0x800EC564`
is invalid. `RecompiledFuncs/` was absent at s4497; do not
treat a missing tree as a failed control if the ROM words
match. Disassemble with `scratch/agent/.venv-splat/bin/python`
(rabbitizer). System python3 has no rabbitizer. ROM:
`./rogue_squadron.z64`. Mission ROM offset is
`vram - 0x7FFFF400`. `0x800F9F94` is past both menu and
cinematic VRAM ends.

Name every original assignment of `$a0` from the function
entry through this jal, every caller, and every callee
`jal rs_free`. The delay does not supply `$a0`, so the
reaching writer is earlier in the function or in the
caller. Do not treat the symbol label as a caller.

Hypotheses:
- H-NextClassComplete: every path that reaches the jal
  passes one allocator return, freed once, or no path
  reaches the jal. No guard.
- H-NextClassGap: a reached path passes a non-allocator
  value, or a pointer already freed, with the writer
  named. Only then is a guard in scope, and it needs an
  ORIGIN line.
- H-NextClassUnevaluable: more than one pointer identity
  can reach `$a0`, or a possible indirect entry cannot
  be accepted or rejected.

Discriminator: the assignments, callers, and callee frees
above. Write
`docs/M3-S4498-RESET-AND-FREE-MODEL-ANIMATIONS-RS-FREE-AUDIT.md`.
The outcome that selects Complete is one allocator return
freed once, or no path. The outcome that selects Gap is a
named non-allocator or already-freed writer on a reached
path. Any other split is Unevaluable.
