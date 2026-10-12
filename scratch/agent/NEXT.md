# Next work unit

HYPOTHESIS-ID: m5-audio-destub

Audit M5 Step 7 status-03 service reaping as one complete class. Do not force
clear status and do not change the wait yet. The current candidate writer is
`serviceVoicePoolFrame` (`0x8009B5A8`); the status-03 producer is
`stopVoiceSlotSynced`, and the target status table is `D_80154620`.

Competing hypotheses:

- H-status-writer: `serviceVoicePoolFrame` enters during hangar status-03,
  writes the zero transition, and the shutdown/drain returns normally.
- H-status-unreached: the worker or its indirect dispatch is never entered in
  the covered route; the spin is downstream of a missing producer trigger.
- H-status-source: the worker enters but the status-zero writer is another
  named path or receives a different slot/table address, so the current
  candidate attribution is wrong.
- H-status-legitimate: status 03 is a real persistent state for some slots and
  the observed wait is not itself a port defect; any zero write must be tied to
  the exact slot and caller before changing behavior.

Discriminating measurement: one fresh build with entry, status-03 producer,
every status writer, exact slot/table address, worker exit, shutdown call-3
entry/return, task/SP completion, slot transitions, PCM, VI, and whole-RDRAM
controls. In hangar phase 5, worker-entry -> exact status-03 zero store ->
call-3 return selects H-status-writer; no worker entry with live status-03
producer selects H-status-unreached; a different exact writer/address selects
H-status-source; persistent status 03 with no legitimate zero contract selects
H-status-legitimate. A missing row is invalid unless the route and positive
controls fire.

Before building, inspect the existing Step 7 anchors:

    rg -n -C 8 'status-03|serviceVoicePoolFrame|ROGUESQ_A14' docs/M5-AUDIO-PLAN.md tools/fixup_game_funcs_vendored.py

Build and run the established phase-gated route, adding the full status/writer
table to the existing batch. Use SIGKILL for all cleanup:

    cmake --build build -j8
    zsh scratch/agent/run_s4117_m5_status03_silent.sh

Require title `0x00790400`, hangar `0x006AB400`, the whole-RDRAM positive
control, and a same-phase status-03 writer/worker/call-3 join before selecting
an explanation. If the old recipe is route-invalid, repair the route in this
iteration rather than interpreting status-03 nulls.
