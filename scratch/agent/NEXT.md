# NEXT: is the terrain normal that returns 2 a real impact?

s5776 measured the fill. Do not re-log byte0, and do not re-disassemble
`stepObjectOrientationTowardTarget`. On the death route every
`site=0x800B2EC4` call was the next line after:

`[orient-ret] kind=ret2 byte0=1 byte1=5 v=2 idx=0 obj=0x80137DBC`

byte0=1 is the terrain sample. The spline jal `0x800B0D9C` stays parked.
Trace and the three rows: `docs/M6-S5775-ORIENT-RET2.md`.

At the `0x800FF6F0` store, on the byte0==1 path, `ctx->f22.fl` and
`ctx->f26.fl` are the degree angles from `0x800FF65C` and `0x800FF670`.
Nothing writes them before the store, and there is no jal in between.
`ctx->r17` is the record. `ctx->r8` is the object (a0 saved at sp+0x4F8).
Record+0x10 is the sampled vec3. Object+0x10 and object+0x1C are the two
vec3s the dots used. Do not name them forward or up.

The work unit is one log, one build, one death-route run. Do not full-regen.

- Add `tools/apply_s5776_orient_geom.py` and hook it from
  `tools/fixup_game_funcs_vendored.py` the way `apply_s5775_orient_ret2.py`
  is hooked (the `funcs_43.c` call and the replay list). New TAG, so it
  still applies on top of the s5775 calls. Idempotent. Apply it to the live
  `funcs_43.c` only, then
  `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build --target RogueSquadron64Recomp`.
- Insert the log in the existing `s5775_ret2` helper, or as a new call on
  the same `// 0x800FF6F0` line, only when `ctx->r8 == 0x80137DBC`. Cap 8.
  Gate on `ROGUESQ_LOG_MTM`.
- One line per hit:
  `[orient-geom] ord=%lu t=%lld f22=%g f26=%g rx=%g ry=%g rz=%g o10x=%g o10y=%g o10z=%g o1cx=%g o1cy=%g o1cz=%g px=%g py=%g pz=%g`
  plus `rs64_s5773_ord` / `rs64_s5773_ms`. `r*` is record+0x10/+0x14/+0x18.
  `o10*` is object+0x10. `o1c*` is object+0x1C. `p*` is object+4/+8/+12.
  Read them with `MEM_W` into a `uint32_t`/`float` union. Do not clobber
  `ctx->f22` or `ctx->f26`.
- Leave the s5775 ret1/ret2 logs in place. They are the control.

Run the s5775 recipe with a new tag. Copy `scratch/agent/s5775_ret2.sh` to
`scratch/agent/s5776_geom.sh`, set `TAG=s5776_geom`, keep `GODV=0`,
`HOLD=420`, `MISSION_RE=62BD00`, `ROGUESQ_LOG_MTM=1`,
`ROGUESQ_NO_SAVE_WRITE=1`. Before launch, `ioreg` must not show
`"CGSSessionScreenIsLocked"=Yes`.

Require, in `scratch/agent/m6/s5776_geom/run.log`: `[livesctl] mission`, a
lives 3->2 line, at least one `kind=ret1`, and one `[orient-geom]` line
whose ord is the line before each `site=0x800B2EC4`. A run with no
`kind=ret1`, or a `0x800B2EC4` line with no geom line in front of it, is a
null. Do not interpret it.

- H-legit: on every such geom line, `f22` and `f26` are finite and inside
  the gate (`abs(f22) < 15`, `f26 < 90`), and record+0x10 is finite,
  nonzero, and not equal to object+0x10 or object+0x1C. The ship is aligned
  with a distinct terrain normal. Close this thread as the game's own
  terrain crash. Next work unit is a real-input mission win, not another
  orientation log.
- H-copy: record+0x10 equals object+0x10 or object+0x1C. The sample echoed
  the ship. Next is a static read of `sampleTerrainAtNpcPosition`
  (`0x80068D5C`), not a guard.
- H-degen: record+0x10 is all zeros or any component is NaN. The test is
  not a real impact. Do not patch the store. Name the writer of that vec3.
- Void: `f22`/`f26` outside the 15/90 gate, or non-finite. The registers
  were not the angles. Re-read `0x800FF65C`..`0x800FF6F0`. Do not add a
  field.

Do not rerun the s5776 byte0 census.

HYPOTHESIS-ID: g1-terrain-snap-geom
