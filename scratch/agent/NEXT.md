# NEXT work unit (s2173) — port store/load of heap object word0

HYPOTHESIS-ID: m5-a1-cinematic-split

## Work unit

s2172 selected `H-RetailHeap0NeverZero`: retail writer of
phys `0x25A580` is `walkMeshdef0List` `0x80057100`
`sw $v0, 0($s7)` after `rs_malloc`, `$v0` from
`hobObjectListItems`+4. First-slot word0 is `0x800CA748`,
consumed at `0x800A87A0`/`0x800A87A8`. Port `=1` SIGBUS
at 87A8 with `$v0=0` is not a retail live zero.

Ask whether the port's constructor store matches and
whether `0x800A87A0` reloads it, same pattern as s2167
for `+0x50`. One instrument, one build, concurrent
`=1`/`=0` arms.

Do not S32-address, NULL-skip, re-flip default-on,
skip/allow `matchKeywordWithPriority` or the lwc, add a
wait/slot guard, or log `$t0`.

## Competing hypotheses and discriminator

- `H-PortStoreMatchesRetail`: both arms store KSEG0
  (first-slot dest `0x8025A580` value `0x800CA748`) at
  `0x80057100` and `0x800A87A0` reloads it (mismatch=0).
  Then `=1` `$v0=0` is a later clobber or a different
  slot, not a missing constructor.
- `H-PortStoreMissing`: no `0x80057100` store on `=1`
  (or dest never `0x8025A580`).
- `H-PortStoresZero`: `0x80057100` stores 0 at dest
  `0x8025A580`.
- `H-PortStoreOkLoadZero`: store is KSEG0, but `0x800A87A0`
  loads 0 from that dest (clobber of heap+0 between
  constructor and consume).
- `H-CoverageFailure`: missing `[cutscene-a2-50-ctl]` /
  new heap0 ctl at 640/`0x00696100`, or zero stores on
  both arms.

Positive controls (both arms, same log): ctl at
width=640 origin=`0x00696100`; store57100 n>=1; 87A0
n>=1. Always-log dest phys `0x25A580` and 87A8 when
`$v0==0` (s2171 every-50 missed the zero).

## Exact commands

Extend `../N64Recomp/fixup_game_funcs.py` (s2167 helper
is static in `funcs_27.c`; add a `funcs_12.c` probe at
`0x80057100` plus a post-load probe at `0x800A87A0`).
Always-log dest `0x25A580` and 87A8 `$v0==0`. Then:

    cmake --build build --target RogueSquadron64Recomp

    env GAME_EXTRA_ENV="ROGUESQ_SPIN_YIELD=1 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_CUTSCENE_A2_50=1" \
      zsh scratch/s73_post_a_scene/run_mission_keys.sh s2173_on 30 12

    env GAME_EXTRA_ENV="ROGUESQ_SPIN_YIELD=1 ROGUESQ_AUDIO_UCODE=0 ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_CUTSCENE_A2_50=1" \
      zsh scratch/s73_post_a_scene/run_mission_keys.sh s2173_off 30 12

Same-build concurrent 90s SIGKILL. Table to
`scratch/agent/s2173_heap0_store_ab.txt`.
