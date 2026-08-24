# NEXT work unit (s2273) — key-on pointer-versus-branch discriminator

HYPOTHESIS-ID: m5-keyon-tuple-contract

## Work unit

Use the existing phase-keyed M5 key-on census in one qualified port run. Keep
the shipped behavior unchanged and enable the bounded transfer-tuple detail
arm. Compare the port rows against the already-established independent retail
table at every common `(origin,width,transfer-PC)` bucket. Do not change a
key-on return, divide guard, task field, slot gate, or default.

## Competing hypotheses and discriminating measurement

- **H-PointerOperands:** the branch/transfer signature overlaps retail, but
  the dynamic `$v0/$s1/$a0/$a2` pointer tuple sets do not. This selects a
  descriptor/voice-data contract difference.
- **H-BranchState:** the pointer tuple sets overlap after bucket alignment,
  but the entry/tail/guard/transfer-PC/slot branch signature differs. This
  selects a control-flow or branch-state difference without authorizing a
  control-flow change.
- **H-Both:** both pointer tuples and branch signatures are disjoint in the
  same common cells. This selects a combined contract boundary and requires a
  narrower writer/descriptor discriminator next.
- **H-CensusInvalid:** a positive route control is missing, a tuple bucket
  overflows, or no common target cell is populated. This rejects all null
  comparisons as coverage failure and sends the next step to census coverage.

The single discriminating table is
`(origin,width,transfer_pc,entry_path,tail_path,guard_path,slot_state,
v0,s1,a0,a2,port_present,retail_present,pointer_overlap,branch_overlap,
overflow,missing_func,b40_rows,route_state_rows,title,hangar,crash_pc,
last_guest_pc)`. A positive control is one `[missing-func]`, 14 B40 rows, 28
route-state rows, title `1024 @ 0x00790400`, and hangar
`512 @ 0x006AB400`. The measurement selects H-PointerOperands when branch
overlap is nonzero and pointer overlap is zero; H-BranchState when the reverse
holds; H-Both when both are zero with no overflow; otherwise H-CensusInvalid.

## Build

```sh
cmake --build build --config Debug --target RogueSquadron64Recomp -j2
```

## Run

```sh
env ROGUESQ_LOG_M5_KEYON_CENSUS=1 ROGUESQ_LOG_M5_KEYON_PORT_TUPLES=1 ROGUESQ_LOG_M5_B40_ROUTE=1 ROGUESQ_LOG_M5_ROUTE_STATE=1 ROGUESQ_LOG_AUDIO_RETURN=1 ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_THREAD_RESUME=0 ROGUESQ_M5_C88_VALUE=0 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh s2273_keyon_pointer_branch 30 12 > /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/s2273_keyon_pointer_branch_driver.log 2>&1
```

Read only the bounded key-on table/transfer rows and driver summary from
`scratch/s73_post_a_scene/s2273_keyon_pointer_branch/run.log`; retain the
positive controls and the full common-cell overlap table in the next ledger
entry. No mitigation or key-on behavior change follows from this run.
