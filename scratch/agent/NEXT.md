# NEXT work unit (s1220)

HYPOTHESIS-ID: retail-entry-capability

The s1219 `gGameSettings.unk20` target did not change the retail path: both
paired arms stayed at width 320/origin `0x006dd280`, with all controls valid.

What already exists and is validated (do not re-validate):
- The project's DEBUGGER=1 Mupen64Plus core + console frontend expose a
  working `pause`/`write`/`mem`/`run` path (Homebrew's core has `--debug`
  disabled and cannot be used for this).
- `tools/oracle/rs64_oracle.c` has `--debug-write VADDR:VALUE`, which performs
  one 32-bit write on the first VI callback whose width is 320. It was smoke
  tested with a harmless word at `0x80007FFC` (`0xDEADBEEF`), read back
  correctly before and after resume, with whole-RDRAM/PIF/VI controls passing
  in both arms. See PORTING-STATE.md s1217.

Work unit: smoke-test the next justified state-changing RAM target at the
retail 320 boundary: `gGameSettings+0x21`, symbol/documentation name
`gGameSettings.unk21` / cinematic sub-state, virtual `0x80130B61`, physical
byte `0x130B61`. Because the debugger writes one aligned 32-bit word, use
`0x130B60:0x00010000` to set +0x21 to 1 while clearing the other three bytes.
`docs/game-architecture.md` identifies this byte as the cinematic branch
tested by `mainGameLoop`, and `src/main/rt64_render_context.cpp` independently
labels the same address `gGameSettings+0x21 (cinematic sub-state)`.

Competing hypotheses and discriminator:
- H1: the justified target changes the retail state path and reaches a later
  VI width/origin phase (not width 320 / origin `0x006dd280`).
- H2: the target is not state-changing, or the run remains at width
  320/origin `0x006dd280`.
- H3: the target write disrupts the whole-RDRAM, PIF, or VI positive
  controls, making the result unevaluable.

Discriminator: a later VI width/origin ONLY in the target arm selects H1;
width 320 in both arms selects H2; a failed whole-RDRAM/PIF/VI control in the
target arm selects H3.

The write itself is also checked: `[debug-write]` must fire at VI width 320;
absence makes the target arm invalid rather than H2.

Required in the same run: paired undriven/control arm vs. the target-write
arm, both logging whole-RDRAM callback counts, PIF trace, and VI width/origin
records. Do not arm M4 target watches unless a later VI width/origin phase is
actually reached first.

Exact command shape:
```
tools/oracle/build/rs64_oracle --debug --rom rogue_squadron.z64 \
  --secs 75 --debug-write 0x130B60:0x00010000 \
  --watch-write 0x0:0x800000 --hit-cap 10000 --vi-trace --vi-poll --pif-trace
```
(Control arm: identical command minus `--debug-write`, run concurrently.)
