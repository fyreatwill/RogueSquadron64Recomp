# NEXT work unit (s2229) — isolate the 8192-entry census early crash

HYPOTHESIS-ID: m5-audio-keyon-contract

## Work unit

Use the already-built 8192-entry binary to run three phase-gated arms in one
iteration: 8192 with tuple-row logging, 8192 with tuple capture disabled, and
the existing 2048 detail reference. This isolates the first run's early
`fillSampleStreamRange+8136` crash before attempting another parity claim.
Do not change generated game behavior, key-on returns, guards, defaults, task
fields, or audio dispatch.

Competing hypotheses and the single discriminator:

- H-TraceOverhead: only the 8192 detail arm loses the later phases; per-row
  transfer logging is the trigger, while 8192 quiet and 2048 detail reach the
  later buckets.
- H-CapFootprint: both 8192 arms fail before the later buckets while 2048
  detail reaches them; the enlarged capture storage changes execution or
  memory behavior.
- H-IntermittentFillRange: all three arms show the same crash/phase boundary,
  so this run does not tie the failure to the census cap.
- H-TupleParityReady: 8192 detail reaches all three buckets with zero
  overflow, permitting the planned retail-set comparison.

The discriminator is one table across all three arms: process outcome and
crash symbol, positive-control counts, and presence of phase-keyed rows at
`0x00696100:640`, `0x00790400:1024`, and `0x006AB400:512`. A later-bucket
survivor only in the 8192 quiet arm selects H-TraceOverhead; survival only in
the 2048 detail arm selects H-CapFootprint; identical early failure selects
H-IntermittentFillRange; all three buckets with zero overflow in 8192 detail
selects H-TupleParityReady and authorizes the retail-set comparison. A null
without the positive controls is invalid.

## Exact commands

Verify the built generated helper and the s2228 result:

~~~sh
rg -n -C 2 'tuples\[8\]\[8192\]|>= 8192ul|tuple_overflow' ../N64Recomp/fixup_game_funcs.py ../N64Recomp/RecompiledFuncs/funcs_24.c
grep -a -E '\[m5-keyon-table\]|\[CRASH\]' scratch/s73_post_a_scene/s2228_keyon_tuple_cap/run.log | tail -12
~~~

Run all arms from the repository root with the same positive-control recipe.
They use separate tags/logs and are phase-compared, not stopwatch-compared:

~~~sh
(
  env ROGUESQ_AUDIO_UCODE=1 ROGUESQ_M5_C88_VALUE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_M5_KEYON_CENSUS=1 ROGUESQ_LOG_M5_KEYON_PORT_TUPLES=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh s2229_8192_detail 30 12 > scratch/agent/s2229_8192_detail_driver.log 2>&1
) & p1=$!
(
  env ROGUESQ_AUDIO_UCODE=1 ROGUESQ_M5_C88_VALUE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_M5_KEYON_CENSUS=1 ROGUESQ_LOG_M5_KEYON_PORT_TUPLES=0 zsh scratch/s73_post_a_scene/run_mission_keys.sh s2229_8192_quiet 30 12 > scratch/agent/s2229_8192_quiet_driver.log 2>&1
) & p2=$!
(
  env ROGUESQ_AUDIO_UCODE=1 ROGUESQ_M5_C88_VALUE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_M5_KEYON_CENSUS=1 ROGUESQ_LOG_M5_KEYON_PORT_TUPLES=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh s2229_2048_detail 30 12 > scratch/agent/s2229_2048_detail_driver.log 2>&1
) & p3=$!
wait "$p1"; r1=$?
wait "$p2"; r2=$?
wait "$p3"; r3=$?
printf 'arm_rc detail8192=%s quiet8192=%s detail2048=%s\n' "$r1" "$r2" "$r3"
~~~

Use the resulting `[m5-keyon-table]` rows and phase-keyed transfer tuples only
after each arm's positive controls are present. Do not compare stopwatch
timestamps or promote the cap change into runtime behavior.
