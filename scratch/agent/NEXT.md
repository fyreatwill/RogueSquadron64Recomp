# Next work unit: qualify M5 Step 7 status-03 worker contract

HYPOTHESIS-ID: m5-step7-status03-worker

Competing hypotheses and discriminator written before the next build:

- H-worker-clears: the named `serviceVoicePoolFrame` worker enters during the
  hangar status-03 interval, stores zero to the status slot, and the existing
  drain/shutdown returns without the timeout hatch.
- H-other-writer: status-03 is cleared by another legitimate writer or a
  different service path; the named worker has no matching zeroing store.
- H-route-invalid: the arm misses the retail controls, hangar phase, or the
  status-03 interval, making writer absence unevaluable.

The single discriminating measurement is a complete status-03 writer table
from the current source/fixup inventory: worker entry PC, every status-03
zeroing store PC/value, drain/shutdown return, and timeout/force-idle path.
A matching worker-entry-to-zero-store-to-return chain selects H-worker-clears;
a complete inventory with no such chain but another named zeroing writer
selects H-other-writer; an unresolved/generated-only site selects
H-route-invalid until a phase-gated runtime arm exists.

Exact command: `rg -n "status.?03|0x03|serviceVoicePoolFrame|stopVoiceSlotSynced|force.?idle|timeout" src tools scratch/agent/s3370_m5_status03_worker_contract.md`.
Do not change the wait or force-clear until this table names the legitimate
writer and its value; then build both rollback/control arms together and run
the phase-gated validation with SIGKILL cleanup.
