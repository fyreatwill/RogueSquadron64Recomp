# Next work unit (s4496): M3 jal-rs_free class, preload songs

HYPOTHESIS-ID: m3-idiom-class-audit

Session 4495 was maintenance (CURRENT-TRUTH over 60 KB). It did not
classify this site. The work unit is unchanged.

Classify the first `jal rs_free` in `preloadSceneReferencedSongs`
(`.ovl.mission`, entry `0x800EEA54`, size `0x328`) at
`0x800EED48`. ROM delay is `addu $a0, $s2, $zero` at
`0x800EED4C`. That delay writes `$a0`. The only `$s2`
write before the jal in this function is `addu $s2, $v0`
at `0x800EEC08`, after `jal rs_malloc` at `0x800EEBF8`.
Do not classify the second jal at `0x800EED50` (delay
`addu $a0, $s3, $zero`, also writes `$a0`). The prologue
`lw $s2` in the epilogue is at `0x800EED68`, after both
jals. Re-check the save of incoming `$s2` and every other
assignment that can reach `0x800EED48`.
No runtime run unless a concrete invalid writer is named and
a guard is the selected fix.

Positive control, same scan: `rg -n "jal\\s+0x80001C98"`
must show closed `0x800EC564` and closed `0x800EC538` in
`funcs_40.c`, closed `0x800C1084` in `funcs_33.c`, and
closed `0x8007BE50` in `funcs_19.c`. A scan that misses
`0x800EC564` or `0x800EC538` is invalid. ROM word
`0x0C000726` must match `0x800EED48` and `0x800EC564`.
Disassemble with `scratch/agent/.venv-splat/bin/python`
(rabbitizer). System python3 has no rabbitizer. ROM:
`./rogue_squadron.z64`. Mission ROM offset is
`vram - 0x7FFFF400`. `0x800EED48` is past both menu and
cinematic VRAM ends.

Name every original assignment of `$a0` and `$s2` from the
function entry through this jal, every caller, and every
callee `jal rs_free`. Do not treat the symbol label as a
caller. The sole `jal 0x800EEA54` found while naming this
site is `0x800EFB9C`, inside `preloadSceneSongsWrapper`
(`0x800EFB94`). Re-verify that; do not inherit it.

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
`docs/M3-S4496-PRELOAD-SCENE-REFERENCED-SONGS-RS-FREE-AUDIT.md`.
The outcome that selects Complete is one allocator return
freed once, or no path. The outcome that selects Gap is a
named non-allocator or already-freed writer on a reached
path. Any other split is Unevaluable.
