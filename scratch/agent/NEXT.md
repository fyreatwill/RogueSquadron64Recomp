# NEXT work unit (s1221)

HYPOTHESIS-ID: retail-entry-capability

The s1220 paired target set `gGameSettings+0x21` via physical
`0x130B60:0x00010000`. The write fired at VI 1, both arms passed the
whole-RDRAM control, and callback plus VI-poll traces stayed at width
320/origin `0x006dd280` for 75 seconds. The cinematic sub-state target did not
change retail entry.

Work unit: smoke-test the next justified state-changing RAM target at the
retail 320 boundary: `gGameSettings+0x22`, documented as the mission
sub-state, virtual `0x80130B62`, physical byte `0x130B62`. Use the oracle's
aligned debugger write `0x130B60:0x00000100` to set only byte +0x22 to 1.

Competing hypotheses and discriminator:
- H1: the mission sub-state target changes the retail state path and reaches a
  later VI width/origin phase.
- H2: the target is not state-changing, or the run remains at width 320/origin
  `0x006dd280`.
- H3: the target write disrupts the whole-RDRAM, PIF, or VI controls, making
  the result unevaluable.

Discriminator: a later VI width/origin only in the target arm selects H1;
width 320 in both arms selects H2; a failed positive control in the target arm
selects H3. The `[debug-write]` marker must fire at VI width 320; absence
invalidates the target arm rather than selecting H2.

Required in the same run: paired undriven/control and target-write arms,
both with whole-RDRAM watch, VI callback/poll traces, and PIF trace. Do not
arm M4 watches unless a later VI phase is reached.

Exact command shape (use the DEBUGGER=1 core path):
```
tools/oracle/build/rs64_oracle --oracle-debugger 1 \
  --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/rogue_squadron.z64 \
  --secs 75 --debug-write 0x130B60:0x00000100 \
  --watch-write 0x0:0x800000 --hit-cap 10000 --vi-trace --vi-poll --pif-trace
```

Control arm: identical command minus `--debug-write`, run concurrently.
