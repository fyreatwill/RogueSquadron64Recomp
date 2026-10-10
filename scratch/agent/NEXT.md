# Next work unit (s4481): M3 jal-rs_free class, walkDatTreeAndCollectSubtypes

HYPOTHESIS-ID: m3-idiom-class-audit

Classify the one original `jal rs_free` in
`walkDatTreeAndCollectSubtypes` (`RecompiledFuncs/funcs_18.c`,
entry `0x80072AF8`, size `0xE8`, free at `0x80072B8C`). The
instruction immediately before the jal is `lw $a0, 8($s0)` at
`0x80072B88`. The delay slot is `nop`, so it does not replace
`$a0`. Do not re-audit `saveServiceWorker` (closed s4480). No
runtime run unless a concrete invalid writer is named and a
guard is the selected fix.

Positive control, same scan: `rg -n "jal\\s+0x80001C98" funcs_17.c`
must still show closed `0x8006DA28` and `0x8006F378`. Also confirm
`0x8006C8C4` still matches in `funcs_16.c`. A scan that misses
`0x8006F378` is invalid. ROM word `0x0C000726` must match
`0x8006F378` and `0x80072B8C`.

`$s0` is the incoming `$a0` (`addu $s0, $a0` at `0x80072B00`) and
is restored at `0x80072BD4`, after the free. Do not treat `$s0`
as the freed pointer. The freed value is the word at `8($s0)`.
The function does not store that word. The free is skipped when
byte 0 is `255` (`beq` at `0x80072B10`) and when bit `0x80` of
byte 0 is clear (`beq` at `0x80072B18` to `0x80072BA0`). Both the
count-zero branch (`0x80072B24` to `0x80072B88`) and the loop
fall-through execute the `lw $a0` before the jal. After the free,
`sb` of `255` at `0($s0)` runs in the delay slot of `j 0x80072BD0`.

Hypotheses:
- H-NextClassComplete: the word at `8($s0)` is the matching
  allocator return, and each such pointer is freed once. No guard.
- H-NextClassGap: that word can be a non-allocator value, or a
  pointer a sibling already freed, with the writer named. Only
  then is a guard in scope, and it needs an ORIGIN line.
- H-NextClassUnevaluable: more than one pointer identity can
  reach `$a0`.

Discriminator: the writer of `8($s0)` on every path that reaches
`0x80072B8C`, plus every callee `jal rs_free` and every caller
argument. Write
`docs/M3-S4481-WALK-DAT-TREE-AND-COLLECT-SUBTYPES-RS-FREE-AUDIT.md`.
