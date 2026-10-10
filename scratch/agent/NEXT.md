# Next work unit (s4488): M3 jal-rs_free class, releaseModelAnimSlot array free

HYPOTHESIS-ID: m3-idiom-class-audit

Classify the second original `jal rs_free` in
`releaseModelAnimSlot`
(`/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_20.c`,
entry `0x80082CFC`, size `0x11C`, free at `0x80082D98`).
ROM: `lw $a0, -0x5664($at)` at `0x80082D94` (`0x8C24A99C`),
jal word `0x0C000726`, delay `nop`. The delay does not write
`$a0`. The freed value is the word at slot `+0x0C`. Do not
re-audit the per-channel free at `0x80082D5C` (closed s4487).
Do not classify the later jal in this same function
(`0x80082DC0`) in this unit. No runtime run unless a concrete
invalid writer is named and a guard is the selected fix.

Positive control, same scan: `rg -n "jal\\s+0x80001C98" funcs_20.c`
must show closed `0x80082430`, closed `0x80082D5C`, and this
site. Also confirm closed `0x8007BE50`, closed `0x8007B23C`,
and closed `0x8007A814` still match in `funcs_19.c`,
`0x80072E40` still matches in `funcs_18.c`, and `0x8006F378`
still matches in `funcs_17.c`. A scan that misses `0x80082D5C`
or `0x8007BE50` is invalid. ROM word `0x0C000726` must match
`0x80082D5C` and `0x80082D98`. Disassemble with
`scratch/agent/.venv-splat/bin/python` (rabbitizer). System
python3 has no rabbitizer. ROM: `./rogue_squadron.z64`.
`.text` rom = vram - `0x7FFFF400`.

A first scan, not a classification: slot `+0x0C` is
`D_8013A990` plus the 1-based id's `0x14` stride. s4487
named the store at `0x80082984` as
`rs_malloc(count << 4, 0)` from `0x80082968`. Confirm that
is the only store of this slot word, that no callee frees it
before this jal, and that the per-channel free at
`0x80082D5C` does not free this same pointer. Name the
count-zero path and the id-0 path if either can put a
different value in `$a0`.

Hypotheses:
- H-NextClassComplete: the word at slot `+0x0C` is a
  matching allocator return, and that pointer is freed
  once. No guard.
- H-NextClassGap: that word can be a non-allocator
  value, or a pointer a sibling already freed, with the
  writer named. Only then is a guard in scope, and it
  needs an ORIGIN line.
- H-NextClassUnevaluable: more than one pointer identity
  can reach `$a0`.

Discriminator: every original assignment of the slot base
and of the word at `+0x0C` from the prologue through the
free, every store that can produce that word, plus every
callee `jal rs_free` and every caller argument. Write
`docs/M3-S4488-RELEASE-MODEL-ANIM-SLOT-ARRAY-RS-FREE-AUDIT.md`.
