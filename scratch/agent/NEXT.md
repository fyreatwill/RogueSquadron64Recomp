# Next work unit (s4494): M3 jal-rs_free class, full-list walk

HYPOTHESIS-ID: m3-idiom-class-audit

Classify the second `jal rs_free` in `freeAllObjectContextPoolNodes`
(`.ovl.mission`, entry `0x800EC514`, size `0x74`, jal at
`0x800EC564`). ROM delay is `sw $v0, -0x3F2C($s0)` at
`0x800EC568`. That store writes the full-list head
`0x8010C0D4`, not `$a0`. `$a0` is the `lw` from
`0x8010C0D4` at `0x800EC55C`. Do not re-audit the
partial-list jal at `0x800EC538` (closed s4493). The next
`jal rs_free` after this one is `0x800EED48`.
No runtime run unless a concrete invalid writer is named and
a guard is the selected fix.

Positive control, same scan: `rg -n "jal\\s+0x80001C98"`
must show closed `0x800EC538` and closed `0x800EC404` in
`funcs_40.c`, closed `0x800C1084` in `funcs_33.c`, and
closed `0x8007BE50` in `funcs_19.c`. A scan that misses
`0x800EC538` or `0x800EC404` is invalid. ROM word
`0x0C000726` must match `0x800EC564` and `0x800EC538`.
Disassemble with `scratch/agent/.venv-splat/bin/python`
(rabbitizer). System python3 has no rabbitizer. ROM:
`./rogue_squadron.z64`. Mission ROM offset is
`vram - 0x7FFFF400`. `0x800EC564` is past both menu and
cinematic VRAM ends.

Name every original assignment of `$a0` from the second
loop's entry through this jal, every caller, and every
callee `jal rs_free`. Do not treat the symbol label as a
caller. s4493 enumerated the partial-list writers and
showed a slab is spliced out of one list before it is
pushed onto the other. Use that as a lead, not as the
classification: re-check the `0x8010C0D4` stores, the
delay, and whether this walk can free a node the
partial-list walk already freed.

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
`docs/M3-S4494-FREE-ALL-OBJECT-POOL-FULL-LIST-RS-FREE-AUDIT.md`.
The outcome that selects Complete is one allocator return
freed once per walked node, or no path. The outcome that
selects Gap is a named non-allocator or already-freed
writer on a reached path. Any other split is Unevaluable.
