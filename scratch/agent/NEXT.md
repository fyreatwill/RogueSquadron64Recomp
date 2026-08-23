# NEXT work unit (s2182) — consume queued =1 soak of s2181 f2+later instrument

HYPOTHESIS-ID: m5-a1-cinematic-split

## Work unit

s2181 rebuilt the helper with f2 at `0x80019550`
`$a1+4` and later `NAN_CHECK` operands
(`f4`/`f8`/`f0`/`f6`/`f12`/`f14`/`f16`/`f18`).
Same-build completing `=1`/`=0` selected
`H-PortNoNaNF2OrLater`: ctl n=176 at
640/`0x00696100` (16 per site including
`site=f2`); 0 NaN / 0 Inf / `w_mem==w_fpr`;
both arms title+hangar. Abort class missed.
Do not conclude port-finite.

Consume the queued `=1` soak
`scratch/agent/soak_queue/s2181_image_vec3_f2.sh`
(180s SIGKILL, `LOG_ALL=1`). No rebuild.
Table to `scratch/agent/s2182_vec3_f2_soak.txt`.

Do not S32-address, NULL-skip, re-flip default-on,
skip/allow the lwc / transform / extract jal,
disable `NAN_CHECK`, add a wait/slot guard, or
land a copyToRAM / CIMG writeback guard.

## Competing hypotheses and discriminator

IEEE single: NaN iff `(w & 0x7F800000)==0x7F800000 && (w & 0x007FFFFF)!=0`.
Join on 640 cinematic (`0x00696100`/`0x00696600`).
Positive control: `[vec3-word-ctl]` at that VI, plus
at least one cinematic row for `site=f2` and each later
operand kind.

- `H-PortF2AlreadyNaN`: soak SIGABRTs in `vec3Cross`;
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
- `H-PortNoNaNThisPair` again: title+hangar, 0 NaN.
  Still do not conclude port-finite.

## Exact commands

1. No rebuild. Read SOAK-RESULTS for
   `s2181_image_vec3_f2` and the run log under
   `scratch/s73_post_a_scene/s2181_image_vec3_f2/`
   (or `scratch/agent/soak_results/`).
2. If the loop has not yet run the soak, do not
   babysit a repeat; leave it queued.
3. Classify: ctl present? per-site cinematic rows?
   NaN/Inf by site? crash class (SIGABRT/SIGBUS/
   copyToRAM/640-stall/title+hangar)?
4. Table to `scratch/agent/s2182_vec3_f2_soak.txt`.
