# NEXT work unit (s2175) — hang after last first-slot 87A0

HYPOTHESIS-ID: m5-a1-cinematic-split

## Work unit

s2174 selected `H-StallWord0Intact`: failing `=1` 640-stall
keeps dest `0x8025A580` = `0x800CA748` (366/366, zero=0) and
stops guest cinematic probes at t=28.4 after last first-slot
`0x800A87A0`. Next insn is `0x800A87A8` `lwc1 0x44($v0)`
(would not print: n=5825 not %50, `$v0!=0`) then jal
`transformVec3ToNpcLocalWithScale` `0x8001DC34`.

Do not S32-address, NULL-skip, re-flip default-on, skip/allow
the lwc, add a wait/slot guard, or log `$t0`.

## Competing hypotheses and discriminator

- `H-NeverReached87A8`: last first-slot 87A0 has no following
  87A8 always-log. Hung at `0x800A87A4` or before the lwc.
- `H-HungInTransform`: 87A8 fires dest=`0x800CA748`, then
  jal `0x8001DC34` entry without matching return.
- `H-TransformReturnedDispatchHung`: transform returns; no
  `cutsceneDispatchSlotsByFlag` return after that 87A0.
- `H-DispatchReturned`: dispatch return after last 87A0
  (parent cinematic tick hung / idle).

If this run SIGBUS at 87A8 with `$v0=0` instead, that is
s2171 recurrence: first-slot word0 still intact (s2174)
so the null is a different slot/object. Record dest of the
preceding 87A0.

Positive controls: `[heap0-ctl]` at 640/`0x00696100`;
store57100 dest `0x8025A580` n>=1; load87a0 n>=1;
dispatch entry n>=1 at that VI.

## Exact commands

One build, one `=1` run. Extend the s2173 heap0 helper in
`../N64Recomp/fixup_game_funcs.py` (then regen-or-patch
funcs_27.c via the existing fixup) so ONE instrument always-logs
all of: 87A8 after n>=5000 or dest=`0x800CA748` or `$v0==0`;
`cutsceneDispatchSlotsByFlag` entry `0x800A8420` and return;
jal `0x8001DC34` entry/return at the `0x800A87C0` call site.
Rate-limit the new sites first 20 then every 50 except the
always-log predicates above.

    env GAME_EXTRA_ENV="ROGUESQ_SPIN_YIELD=1 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_CUTSCENE_A2_50=1" \
      zsh scratch/s73_post_a_scene/run_mission_keys.sh s2175_on 30 12

180s SIGKILL. Table to `scratch/agent/s2175_hang_after_87a0.txt`.
Enqueue a copy at `scratch/agent/soak_queue/s2175_image_hang.sh`
if the first run completes to title+hangar (intermittent miss).
