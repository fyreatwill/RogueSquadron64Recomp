# NEXT work unit (s2181) — log vec3Cross f2 + later NAN_CHECK operands

HYPOTHESIS-ID: m5-a1-cinematic-split

## Work unit

s2180 consumed the queued `=1` soak and selected
`H-FailingExtractFinite`: extract `$a1+0x20` and
first-cross `$a2+8`/f10 are 0 NaN / 0 Inf on a
failing cinematic (`w_mem==w_fpr`, ctl n=32 at
640/`0x00696100`). Crash was host SIGSEGV in
`NativeTarget::copyToRAM`, not `vec3Cross`
SIGABRT. Abort class still unobserved with this
instrument. Do not conclude port-finite.

Add f2 at `0x80019550` `MEM_W($a1,4)` plus the
later `NAN_CHECK` operands in `vec3Cross`
(`f4`/`f8`/`f0`/`f6`/`f12`/`f14`/`f16`/`f18`)
to the existing s2179 helper. One rebuild. Same-build
concurrent `=1`/`=0` 90s SIGKILL. Enqueue a `=1`
soak of the new binary.

Do not S32-address, NULL-skip, re-flip default-on,
skip/allow the lwc / transform / extract jal,
disable `NAN_CHECK`, add a wait/slot guard, or
land a copyToRAM / CIMG writeback guard.

## Competing hypotheses and discriminator

IEEE single: NaN iff `(w & 0x7F800000)==0x7F800000 && (w & 0x007FFFFF)!=0`.
Join on 640 cinematic (`0x00696100`/`0x00696600`).
Positive control: `[vec3-word-ctl]` at that VI, plus at
least one cinematic row for `site=f2` and each later
operand kind.

- `H-PortF2AlreadyNaN`: `=1` SIGABRTs in `vec3Cross`;
  f2 (`$a1+4`) is NaN; extract/f10 still finite.
- `H-PortLaterCheck`: extract/f10/f2 finite; a later
  `NAN_CHECK` operand (f4/f8/f0/f6 or a mul/sub
  product) is NaN at abort.
- `H-AssertNotLoggedNaN`: SIGABRT in `vec3Cross` with
  0 NaN on every logged operand (missed site or
  non-IEEE assert).
- `H-HostCopyToRamClass`: SIGSEGV in `copyToRAM` with
  0 NaN (reproduces s2180). Do not add a writeback
  guard; record as a 6th intermittent class.
- `H-PortNoNaNThisPair` again: both arms title+hangar,
  0 NaN. Still do not conclude port-finite; enqueue
  the `=1` soak.

## Exact commands

1. Extend `rs64_s2179_vec3_word` in
   `../N64Recomp/fixup_game_funcs.py` (and the
   generated `funcs_4.c`) with kind=2 f2 at
   `0x80019550` after `MEM_W($a1,4)`, and kinds
   for later `NAN_CHECK` pairs before each
   `NAN_CHECK` in `vec3Cross`. Always-log NaN/Inf.
   Keep extract/first-cross probes.
2. One cmake Debug rebuild.
3. Concurrent `=1` / `=0`, 90s SIGKILL, recipe
   `SPIN_YIELD=1 LLE_UNGATED=1 LLE_SOLO=1 LOG_ALL=1
   LOG_CUTSCENE_A2_50=1`, driver
   `scratch/s73_post_a_scene/run_mission_keys.sh 30 12`.
4. Table to `scratch/agent/s2181_vec3_f2.txt`.
5. Enqueue `scratch/agent/soak_queue/s2181_image_vec3_f2.sh`
   (`=1`, `LOG_ALL=1`, 180s).
