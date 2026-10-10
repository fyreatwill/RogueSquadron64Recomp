# Next work unit (s4480): M3 jal-rs_free class, saveServiceWorker

HYPOTHESIS-ID: m3-idiom-class-audit

Classify the one original `jal rs_free` in `saveServiceWorker`
(`RecompiledFuncs/funcs_17.c`, entry `0x8006F2CC`, generated near
line 5512, free at `0x8006F378`). The delay slot is
`addu $a0, $s0, $zero`. `0x8006F380` is `j 0x8006F318`, so the
free is inside a loop. Do not re-audit
`runIdleFramesAndLoadSaveData` (closed s4479). No runtime run
unless a concrete invalid writer is named and a guard is the
selected fix.

Positive control, same scan: `rg -n "jal\\s+0x80001C98" funcs_17.c`
must still show closed `0x8006DA28` and this site `0x8006F378`.
Also confirm `0x8006C8C4` still matches in `funcs_16.c`. A scan
that misses `0x8006DA28` is invalid. ROM word `0x0C000726` must
match both PCs.

`$s5` is the incoming `$a0` (`addu $s5, $a0` at `0x8006F2D4`).
`$s0` is assigned from `$v0` at `0x8006F334`, after
`jal 0x80006F24` (`recvServiceMessage`). The `beql` at
`0x8006F370` writes a byte through `$s2` on the taken path only.
It does not write `$s0`. Do not treat `$s5` as the freed pointer
unless the `0x8006F334` rebind does not dominate on the path that
reaches `0x8006F378`. The back-edge can free a different `$s0`
on each trip; name each assignment that can reach the free.

Hypotheses:
- H-NextClassComplete: every assignment of `$s0` that can reach
  the free is the matching allocator return, and each such
  pointer is freed once. No guard.
- H-NextClassGap: `$s0` can be a non-allocator value, or a pointer
  a sibling already freed, with the writer named. Only then is a
  guard in scope, and it needs an ORIGIN line.
- H-NextClassUnevaluable: more than one pointer identity can reach
  `$a0`.

Discriminator: the complete original assignment list for `$s0`
between the function prologue and each reach of `0x8006F378`,
plus every callee `jal rs_free` and every caller argument. Write
`docs/M3-S4480-SAVE-SERVICE-WORKER-RS-FREE-AUDIT.md`.
