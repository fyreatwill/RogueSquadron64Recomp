# Next work unit (s4493): M3 jal-rs_free class, freeAllObjectContextPoolNodes

HYPOTHESIS-ID: m3-idiom-class-audit

Classify the first `jal rs_free` in `freeAllObjectContextPoolNodes`
(`.ovl.mission`, entry `0x800EC514`, size `0x74`, jal at
`0x800EC538`). ROM delay is `sw $v0, -0x3F30($s0)` at
`0x800EC53C`. That store writes the partial-list head, not
`$a0`. `$a0` is the `lw` from `0x8010C0D0` at `0x800EC530`.
Do not re-audit `unlinkAndFreeChildNpcNode` (closed s4492).
The second jal in this function, `0x800EC564`, is a separate
site (the `0x8010C0D4` list). Classify `0x800EC538` only.
No runtime run unless a concrete invalid writer is named and
a guard is the selected fix.

Positive control, same scan: `rg -n "jal\\s+0x80001C98"`
must show closed `0x800EC404` in `funcs_40.c`, closed
`0x800C1084` in `funcs_33.c`, and closed `0x8007BE50` in
`funcs_19.c`. A scan that misses `0x800EC404` or
`0x800C1084` is invalid. ROM word `0x0C000726` must match
`0x800EC538` and `0x800EC404`. Disassemble with
`scratch/agent/.venv-splat/bin/python` (rabbitizer).
System python3 has no rabbitizer. ROM:
`./rogue_squadron.z64`. Mission ROM offset is
`vram - 0x7FFFF400`. `0x800EC538` is past both menu and
cinematic VRAM ends.

Name every original assignment of `$a0` from the prologue
through this jal, every caller, and every callee
`jal rs_free`. Do not treat the symbol label as a caller.
s4492 already showed this walk frees slabs still linked at
`0x8010C0D0`, and that `unlinkAndFreeChildNpcNode` unlinks
a slab before its own free. Use that as a lead, not as the
classification: re-check the load, the delay, and whether
the same slab can be freed twice on one walk.

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
`docs/M3-S4493-FREE-ALL-OBJECT-POOL-RS-FREE-AUDIT.md`.
The outcome that selects Complete is one allocator return
freed once per walked node, or no path. The outcome that
selects Gap is a named non-allocator or already-freed
writer on a reached path. Any other split is Unevaluable.
