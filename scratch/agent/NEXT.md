# NEXT work unit (s2180) — consume s2179 =1 soak; classify abort NaN or add f2

HYPOTHESIS-ID: m5-a1-cinematic-split

## Work unit

s2179 selected `H-PortNoNaNThisPair` on a completing
same-build pair: extract `$a1+0x20` and first-cross
`$a2+8`/f10 were 0 NaN / 0 Inf, `w_mem==w_fpr`, both
arms title+hangar. Abort class missed. Do not conclude
port-finite. Soak
`scratch/agent/soak_queue/s2179_image_vec3_word.sh`
is queued (`=1`, `LOG_ALL=1`, 180s).

Read the new `scratch/agent/SOAK-RESULTS.md` line and
the soak log. Discriminate with the already-landed
`[vec3-word]` rows — no rebuild unless the soak is
another completing 0-NaN run.

Do not S32-address, NULL-skip, re-flip default-on,
skip/allow the lwc / transform / extract jal,
disable `NAN_CHECK`, or add a wait/slot guard.

## Competing hypotheses and discriminator

IEEE single: NaN iff `(w & 0x7F800000)==0x7F800000 && (w & 0x007FFFFF)!=0`.
Join on 640 cinematic (`0x00696100`/`0x00696600`).
Positive control: `[vec3-word-ctl]` at that VI.

- `H-PortExtractAlreadyNaN`: soak aborts (or SIGBUS)
  and extract `w_a1p20` is NaN before orthonormalize.
- `H-PortOrthonormalizeMakesNaN`: extract finite;
  first-cross `w_a2p8` / f10 is NaN.
- `H-PortF10NotMemWord`: first-cross MEM_W($a2,8)
  finite but f10.u32l is NaN.
- `H-PortF2OrLaterCheck`: soak SIGABRTs in
  `vec3Cross` with 0 NaN on extract and f10 (the
  aborting line is `NAN_CHECK(f2); NAN_CHECK(f10)`).
  Then one rebuild: log f2 at `0x80019550`
  `MEM_W($a1,4)` plus later `NAN_CHECK` operands
  in `vec3Cross` before each assert.
- `H-PortNoNaNThisPair` again: soak title+hangar,
  0 NaN. Still do not conclude port-finite; take
  the f2 rebuild this iteration (abort class still
  unobserved with this instrument).

## Exact commands

No build unless the soak is completing/0-NaN.

1. Read the new SOAK-RESULTS line and
   `scratch/s73_post_a_scene/s2179_image_vec3_word/run.log`
   via grep (never cat): `[vec3-word-ctl]`,
   `nan_mem=1`/`nan_fpr=1`, last extract / first=1,
   `[CRASH]`/`Assertion failed`/`[phase]` 1024/512.
2. Table to `scratch/agent/s2180_vec3_word_soak.txt`.
3. Only if 0 NaN and no abort: add f2 + later
   `NAN_CHECK` operands in `fixup_game_funcs.py`
   and the generated C, one rebuild, one `=1` 90s
   run (plus `=0` concurrent).
