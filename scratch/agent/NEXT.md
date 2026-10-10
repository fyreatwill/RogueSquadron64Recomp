# Next work unit (s4500): M3 jal-rs_free class, player aux buffers, second free

HYPOTHESIS-ID: m3-idiom-class-audit

Classify only the second `jal rs_free` in `freePlayerAuxBuffersIfActive`
(`.ovl.mission`, entry `0x80100F40`, size `0x68`) at `0x80100F90`.
ROM delay is `nop` at `0x80100F94`. That delay does not write `$a0`.
Re-verify the delay. Do not reclassify `0x80100F84` (closed s4499).
The `lw $a0, 0xC($s0)` at `0x80100F8C` was observed while naming
this site; it is not a classification.
No runtime run unless a concrete invalid writer is named and a
guard is the selected fix.

Before calling `.ovl.mission` exhausted, re-run the scan from
`0x80100F94` to the overlay end (`0x8010B6D0`). s4499 reported no
later `jal rs_free` there. That claim is single-source until this
scan repeats it. A hit past this jal is the following site, not a
reason to classify anything else in this session.

Positive control, same scan: mission ROM word `0x0C000726` must be
present at closed `0x800F9F94`, closed `0x800EED50`, closed
`0x800EC564`, and closed `0x80100F84`. `.text` word at closed
`0x8007BE50` must match. This jal must be the same word. A scan
that misses `0x800F9F94` or `0x800EC564` is invalid.
`RecompiledFuncs/` was absent at s4499; do not treat a missing
tree as a failed control if the ROM words match. Disassemble with
`scratch/agent/.venv-splat/bin/python` (rabbitizer). System python3
has no rabbitizer. ROM: `./rogue_squadron.z64`. Mission ROM offset
is `vram - 0x7FFFF400`. `0x80100F90` is past both menu and
cinematic VRAM ends.

Control check, from the repo root:

```
scratch/agent/.venv-splat/bin/python - <<'PY'
import pathlib
rom = pathlib.Path("rogue_squadron.z64").read_bytes()
def word(vram):
    off = vram - 0x7FFFF400
    return int.from_bytes(rom[off:off+4], "big")
for va in (0x800F9F94, 0x800EED50, 0x800EC564, 0x8007BE50, 0x80100F84, 0x80100F90):
    print(hex(va), hex(word(va)))
print("delay", hex(word(0x80100F94)))
PY
```

Expected: every listed jal is `0xc000726` and the delay is `0`.
Any other value invalidates the scan.

Name every original assignment of `$a0` from the function entry
through this jal, every caller, and every callee `jal rs_free`.
The delay does not supply `$a0`, so the reaching writer is the
load or something earlier. Do not treat the symbol label as a
caller. Do not copy s4499's slot-+8 writer onto slot +0xC; prove
the store that this jal loads.

Hypotheses:
- H-NextClassComplete: every path that reaches the jal passes
  one allocator return, freed once, or no path reaches the jal.
  No guard.
- H-NextClassGap: a reached path passes a non-allocator value,
  or a pointer already freed, with the writer named. Only then
  is a guard in scope, and it needs an ORIGIN line.
- H-NextClassUnevaluable: more than one pointer identity can
  reach `$a0`, or a possible indirect entry cannot be accepted
  or rejected.

Discriminator: the assignments, callers, and callee frees above.
Write
`docs/M3-S4500-FREE-PLAYER-AUX-BUFFERS-SECOND-RS-FREE-AUDIT.md`.
The outcome that selects Complete is one allocator return freed
once, or no path. The outcome that selects Gap is a named
non-allocator or already-freed writer on a reached path. Any
other split is Unevaluable. An uncleared slot is not a Gap unless
a caller actually reaches a second free of that same pointer.
