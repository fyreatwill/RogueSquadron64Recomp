# Next work unit (s4492): M3 jal-rs_free class, unlinkAndFreeChildNpcNode

HYPOTHESIS-ID: m3-idiom-class-audit

Classify `unlinkAndFreeChildNpcNode`
(`.ovl.mission`, entry `0x800EC388`, size `0x150`, jal at
`0x800EC404`). ROM delay is `nop` at `0x800EC408`. The
instruction before the jal is `sw $v0, 0($a1)` at
`0x800EC400`. That store does not write `$a0`. Do not
re-audit `handleHUD` (closed s4491) or the mission frees
from `0x800CABB0` through `0x800EAAE4` (s3617–s3620).
s1814 renamed this function; that note is not a
classification. No runtime run unless a concrete invalid
writer is named and a guard is the selected fix.

Positive control, same scan: `rg -n "jal\\s+0x80001C98"`
must show closed `0x80083C58` in `funcs_20.c`, closed
`0x8007BE50` in `funcs_19.c`, and closed `0x800C1084` in
`funcs_33.c`. A scan that misses `0x800C1084` or
`0x8007BE50` is invalid. ROM word `0x0C000726` must match
`0x800EC404` and `0x800C1084`. Disassemble with
`scratch/agent/.venv-splat/bin/python` (rabbitizer).
System python3 has no rabbitizer. ROM:
`./rogue_squadron.z64`. Mission ROM offset is
`vram - 0x7FFFF400`. Menu and cinematic do not use that
difference. `0x800EC404` is past both overlay VRAM ends.

Name every original assignment of `$a0` from the prologue
through the free, every caller, and every callee
`jal rs_free`. Do not treat the symbol label as a caller.

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
above. Write `docs/M3-S4492-UNLINK-CHILD-NPC-RS-FREE-AUDIT.md`.
The outcome that selects Complete is one allocator return
freed once, or no path. The outcome that selects Gap is a
named non-allocator or already-freed writer on a reached
path. Any other split is Unevaluable.
