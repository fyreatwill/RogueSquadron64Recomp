# Next work unit (s4489): M3 jal-rs_free class, releaseModelAnimSlot tree free

HYPOTHESIS-ID: m3-idiom-class-audit

Classify the third original `jal rs_free` in
`releaseModelAnimSlot`
(`/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_20.c`,
entry `0x80082CFC`, size `0x11C`, free at `0x80082DC0`).
ROM: `lw $a0, -0x5670($at)` at `0x80082DBC` (`0x8C24A990`),
jal word `0x0C000726`, delay `nop` at `0x80082DC4`. The
delay does not write `$a0`. The freed value is the word
at slot `+0x00`. The jal is reached only when
`lbu $v0, -0x565F($at)` at `0x80082DA8` is nonzero
(`beqz` target `0x80082DC8`). Do not re-audit
`0x80082D5C` (closed s4487) or `0x80082D98` (closed
s4488). No runtime run unless a concrete invalid writer
is named and a guard is the selected fix.

Positive control, same scan: `rg -n "jal\\s+0x80001C98" funcs_20.c`
must show closed `0x80082430`, closed `0x80082D5C`, closed
`0x80082D98`, and this site. Also confirm closed
`0x8007BE50`, closed `0x8007B23C`, and closed `0x8007A814`
still match in `funcs_19.c`, `0x80072E40` still matches in
`funcs_18.c`, and `0x8006F378` still matches in `funcs_17.c`.
A scan that misses `0x80082D98` or `0x8007BE50` is invalid.
ROM word `0x0C000726` must match `0x80082D98` and
`0x80082DC0`. Disassemble with
`scratch/agent/.venv-splat/bin/python` (rabbitizer). System
python3 has no rabbitizer. ROM: `./rogue_squadron.z64`.
`.text` rom = vram - `0x7FFFF400`.

A first scan, not a classification: the only
`lui $at, 0x8014` stores of immediate `-0x5670` are
`sw $zero` at `0x80082898` (`resetModelAnimSlotTable`),
`sw $a0` at `0x80082944` (`allocateModelAnimSlot`), and
`sw $zero` at `0x80082DD0` (after this jal). The byte at
`-0x565F` is cleared at `0x800829A0` and set to 1 at
`0x80082BA8` by `flattenAnimTreeAndAllocateSlot` when the
returned id is nonzero. `parseModelAnimType2Entry` only
loads `-0x5670` (`0x800835E4`). Confirm the store at
`0x80082944` is allocate's incoming `$a0`, that this
`$a0` is the `rs_malloc` at `0x80082B2C`, that no callee
frees it before this jal, and that the byte-zero path
does not reach the jal. Name the id-0 path if it can put
a different value in `$a0` (byte offset `-0x14` loads
`0x8013A97C`). The post-jal `sw $zero` does not feed
this jal on the same call.

Hypotheses:
- H-NextClassComplete: the word at slot `+0x00` is a
  matching allocator return on every path that reaches
  the jal, and that pointer is freed once. No guard.
- H-NextClassGap: that word can be a non-allocator
  value, or a pointer a sibling already freed, with the
  writer named. Only then is a guard in scope, and it
  needs an ORIGIN line.
- H-NextClassUnevaluable: more than one pointer identity
  can reach `$a0`.

Discriminator: every original assignment of the slot base
and of the word at `+0x00` from the prologue through the
free, every store that can produce that word, the gate
byte's stores, plus every callee `jal rs_free` and every
caller argument. Write
`docs/M3-S4489-RELEASE-MODEL-ANIM-SLOT-TREE-RS-FREE-AUDIT.md`.
