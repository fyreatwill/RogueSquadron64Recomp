# NEXT work unit (s2176) — classify hang after 87A0 on a failing =1

HYPOTHESIS-ID: m5-a1-cinematic-split

## Work unit

s2175 selected `H-CompletePathDispatchReturned` on a
completing `=1` run: last first-slot 87A0 n=14305 t=48.4
is followed by 87A8 dest=`0x800CA748`, transform
entry+return, and dispatch return, then title+hangar.
Hang location on a failing cinematic is still open.
Soak `s2175_image_hang` is queued (same always-log).

If SOAK-RESULTS has `s2175_image_hang`:
- rc!=0 and no VI 1024: classify hang location from
  `scratch/s73_post_a_scene/s2175_image_hang/run.log`
  (analysis-only, no rebuild).
- rc=0 title+hangar: another complete; do not enqueue
  the same recipe again. Next discriminator must be a
  new failing-run catcher or a guest-side split that
  appears before t=28 on stalls.

Do not S32-address, NULL-skip, re-flip default-on,
skip/allow the lwc or transform, add a wait/slot guard,
or log `$t0`.

## Competing hypotheses and discriminator

- `H-NeverReached87A8`: last first-slot 87A0 has no
  following 87A8 always-log.
- `H-HungInTransform`: 87A8 fires dest=`0x800CA748`,
  then jal `0x8001DC34` entry without matching return.
- `H-TransformReturnedDispatchHung`: transform returns;
  no `cutsceneDispatchSlotsByFlag` return after that 87A0.
- `H-DispatchReturned`: dispatch return after last 87A0
  (parent cinematic tick hung / idle). Completing s2175
  is this shape through title; a failing soak with this
  shape is a later hang.
- s2171 recurrence: SIGBUS at 87A8 with `$v0=0`. Record
  dest of the preceding 87A0.

Positive controls: `[heap0-ctl]` at 640/`0x00696100`
including dispatchEntry; store57100 dest `0x8025A580`
n>=1; load87a0 n>=1.

## Exact commands

No rebuild if the soak log exists. Table to
`scratch/agent/s2176_hang_after_87a0.txt`.

    grep -ac '\[heap0-ctl\].*width=640 origin=0x00696100' \
      scratch/s73_post_a_scene/s2175_image_hang/run.log
    grep -ac '\[heap0-ctl\].*site=dispatchEntry.*width=640 origin=0x00696100' \
      scratch/s73_post_a_scene/s2175_image_hang/run.log

If the soak did not run, launch the already-queued recipe
(do not rewrite it) and classify in this iteration.
