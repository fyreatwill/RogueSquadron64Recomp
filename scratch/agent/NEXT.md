# Next work unit (s4497): M3 jal-rs_free class, mark array

HYPOTHESIS-ID: m3-idiom-class-audit

Classify the second `jal rs_free` in `preloadSceneReferencedSongs`
(`.ovl.mission`, entry `0x800EEA54`, size `0x328`) at
`0x800EED50`. ROM delay is `addu $a0, $s3, $zero` at
`0x800EED54`. That delay writes `$a0`. Do not reclassify the
first jal at `0x800EED48` (closed s4496). The `$s3` register
write observed while classifying that site was `addu $s3, $v0`
at `0x800EEAAC`, after `jal rs_malloc` at `0x800EEAA4`.
Re-verify it. `blez $a0, 0x800EED50` at `0x800EEBEC` also
targets this jal, so a path reaches it without the second
`rs_malloc`. The epilogue `lw $s3` is at `0x800EED64`, after
this jal. Re-check every other assignment that can reach
`0x800EED50`.
No runtime run unless a concrete invalid writer is named and
a guard is the selected fix.

Positive control, same scan: `rg -n "jal\\s+0x80001C98"`
must show closed `0x800EED48` and closed `0x800EC564` in
`funcs_40.c`, closed `0x800C1084` in `funcs_33.c`, and
closed `0x8007BE50` in `funcs_19.c`. A scan that misses
`0x800EED48` or `0x800EC564` is invalid. ROM word
`0x0C000726` must match `0x800EED50` and `0x800EED48`.
Disassemble with `scratch/agent/.venv-splat/bin/python`
(rabbitizer). System python3 has no rabbitizer. ROM:
`./rogue_squadron.z64`. Mission ROM offset is
`vram - 0x7FFFF400`. `0x800EED50` is past both menu and
cinematic VRAM ends.

Name every original assignment of `$a0` and `$s3` from the
function entry through this jal, every caller, and every
callee `jal rs_free`. Do not treat the symbol label as a
caller. The sole `jal 0x800EEA54` found while classifying
the previous site is `0x800EFB9C`, inside
`preloadSceneSongsWrapper` (`0x800EFB94`). Re-verify that;
do not inherit it.

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
`docs/M3-S4497-PRELOAD-SCENE-REFERENCED-SONGS-MARK-ARRAY-RS-FREE-AUDIT.md`.
The outcome that selects Complete is one allocator return
freed once, or no path. The outcome that selects Gap is a
named non-allocator or already-freed writer on a reached
path. Any other split is Unevaluable.
