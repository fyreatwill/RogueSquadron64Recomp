# NEXT work unit (s2167) — port store at spawnCutsceneObjectsFromList +0x50

HYPOTHESIS-ID: m5-a1-cinematic-split

## Work unit

s2166 selected `H-RetailWriterNamed`. Table:
`scratch/s73_post_a_scene/s2166_cutscene_a2_50_writer.txt`.

Retail ORIGIN of the pointer `cutsceneDispatchSlotsByFlag` loads at
`$a2+0x50` is `spawnCutsceneObjectsFromList` `0x800A8144`
`sw $v0, 0x50($v1)` after `jal walkMeshdef0List`. Sibling store
`0x800A80D4` (after `instantiateNamedMeshInstance`) did not hit
phys `0xC7B0C` this run. `rs_memset` `0x800078EC` covers the word
first (4 `sb`).

Ask whether the PORT's store is missing or stores 0 on the
image-arm cinematic path. Do not S32-address, NULL-skip, re-flip
default-on, or add a wait/slot guard.

## Competing hypotheses and discriminator

- `H-PortStoreMissing`: `spawnCutsceneObjectsFromList` entry fires
  (positive control) but neither `0x800A8144` nor `0x800A80D4`
  stores to dest `0x800C7B0C` (or any `$v1` in
  `0x800C7ABC..0x800CA5F0`) before the 640 `0x00696100` SIGBUS /
  60s cap.
- `H-PortStoresZeroOrWild`: a +0x50 store fires at a slot dest with
  `$v0` 0 or not KSEG0 RDRAM (`0x80000000..0x803FFFFF`).
- `H-PortStoreOkLoadBad`: a +0x50 store writes a KSEG0 heap pointer
  into `0x800C7B0C` (or the live `$a2+0x50`), but `0x800A879C` then
  loads 0 / non-KSEG0 / a different word than the last store.
- `H-CoverageFailure`: spawn entry never prints, no `[cutscene-a2-50-ctl]`,
  or the run never reaches VI 640 / `0x00696100`. Null store counts
  are unevaluable.

Positive control: first `spawnCutsceneObjectsFromList` entry must
print `[cutscene-a2-50-ctl]` on every arm that reaches cinematic.
Rate-limit store/load rows (first 20 + every 50); always log a
store whose dest phys is `0xC7B0C`.

Existing `rs64_probe_submit_gate_store` in `funcs_27.c` is NOT this
instrument — it only logs phys `0x11A89F`.

## Exact commands

Add env-gated rows in
`/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`
AND apply the same snippet to
`RecompiledFuncs/funcs_27.c` (fixup sentinel is already applied;
do not full-regen unless the sentinel is absent). Sites:

- `spawnCutsceneObjectsFromList` entry
- `0x800A80D4` `sw $v0, 0x50($v1)` — dest=`$v1+0x50`, value=`$v0`
- `0x800A8144` `sw $v0, 0x50($v1)` — dest, value
- `0x800A879C` `lw $v0, 0x50($a2)` — `$a2`, `MEM_W($a2,0x50)` (pre-load GPR is not the word)
- `0x800A87A8` `lwc1 0x44($v0)` — `$v0`

Env: `ROGUESQ_LOG_CUTSCENE_A2_50=1`. Rebuild once:

    DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer \
      cmake --build build --target RogueSquadron64Recomp

Then both arms in one iteration (same binary, concurrent):

    env ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
        ROGUESQ_AUDIO_UCODE=1 ROGUESQ_LOG_CUTSCENE_A2_50=1 ROGUESQ_LOG_ALL=1 \
        zsh scratch/s73_post_a_scene/run_mission_keys.sh s2167_on 30 12

    env ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
        ROGUESQ_AUDIO_UCODE=0 ROGUESQ_LOG_CUTSCENE_A2_50=1 ROGUESQ_LOG_ALL=1 \
        zsh scratch/s73_post_a_scene/run_mission_keys.sh s2167_off 30 12

Cap ~90s then SIGKILL. Cinematic SIGBUS is at ~7s; do not wait for
title. Compare store dest/value vs load `$a2`/word on each arm.

Do not flip `get_rsp_microcode`. Do not skip/allow/guard the load.
