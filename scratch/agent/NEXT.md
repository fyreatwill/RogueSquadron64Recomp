# NEXT: which fill stores the orientation return of 2

s5775 named the instruction. Do not re-disassemble `stepObjectOrientationTowardTarget`.
The return is stack byte sp+0x497. The only store of 2 is the `sb` at
`0x800FF6F0` in `funcs_43.c` (live tree
`../N64Recomp/RecompiledFuncs/funcs_43.c`, comment
`// 0x800FF6F0: sb          $t3, 0x497($sp)`). At that line `ctx->r11` is 2,
`ctx->r17` is still the record (`s1`), and `ctx->r12` is the dense index.
byte0 is `MEM_BU(ctx->r17, 0)`, byte1 is `MEM_BU(ctx->r17, 1)`.

byte0==1 means the record came from `sampleTerrainAtNpcPosition`. byte0==0
means it came from `findSegmentObjectSphereHit`, which only reaches the store
when the float at record+0x24 is not < 0.7. byte1 must be 0 or 5. Trace:
`docs/M6-S5775-ORIENT-RET2.md`.

The work unit is one log, one build, one death-route run. Do not full-regen.

- Add `tools/apply_s5775_orient_ret2.py` and hook it from
  `tools/fixup_game_funcs_vendored.py` the way `apply_s5774_debris_caller.py`
  is hooked (the `funcs_43.c` call and the replay list). Idempotent on its
  TAG. Apply it to the live `funcs_43.c` only, then
  `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build --target RogueSquadron64Recomp`.
- At the `0x800FF6F0` store, log every hit (cap 32):
  `[orient-ret] kind=ret2 byte0=%u byte1=%u f24=%g v=%u` plus
  `rs64_s5773_ord` / `rs64_s5773_ms`. `v` is `ctx->r11`. `f24` is the float
  at record+0x24. Gate on `ROGUESQ_LOG_MTM`.
- At `// 0x800FFA40: sb          $t0, 0x497($sp)` log
  `[orient-ret] kind=ret1` for the first 8 hits and then every 500th. That
  is the control: the return-1 store runs on ordinary frames. A run with
  zero `kind=ret1` lines is a null.

Run the s5774 level-select death recipe with a new tag. Copy
`scratch/agent/s5774_debris.sh` to `scratch/agent/s5775_ret2.sh`, set
`TAG=s5775_ret2`, keep `GODV=0`, `HOLD=420`, `MISSION_RE=62BD00`,
`ROGUESQ_LOG_MTM=1`, `ROGUESQ_NO_SAVE_WRITE=1`. Before launch, `ioreg` must
not show `"CGSSessionScreenIsLocked"=Yes`.

Require, in `scratch/agent/m6/s5775_ret2/run.log`: `[livesctl] mission`, a
lives 3->2 line, at least one `[debris-call] site=0x800B2EC4`, and at least
one `kind=ret1`.

- H-terrain: every `kind=ret2` line whose ord is the line before a
  `site=0x800B2EC4` debris-call has byte0=1 and byte1 in {0,5}. The death
  is the game's terrain-alignment snap.
- H-npc: those lines have byte0=0 and byte1 in {0,5}. The death is an NPC
  sphere hit. `f24` must be >= 0.7; a smaller value refutes the static gate.
- Both: ret2 lines of both byte0 values precede debris-calls. Report the
  counts. Do not pick one.
- Refute: a `site=0x800B2EC4` line with no preceding `kind=ret2`, or byte1
  outside {0,5}, or `v` not 2. The s5775 trace is wrong; do not add another
  field, re-read the store.

Do not rerun the s5774 debris census. Leave the spline jal `0x800B0D9C` parked.

HYPOTHESIS-ID: g1-orient-ret2
