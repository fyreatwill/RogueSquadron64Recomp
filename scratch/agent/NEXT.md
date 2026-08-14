# NEXT work unit (s1100)

HYPOTHESIS-ID: submit-external-queue-wiring

Perform one batched, phase-scoped runtime trace of event registration and
completion targets. Before building, read `tools/oracle/README.md` and
`docs/F5-UCODE-REFERENCE.md`; use the existing phase-gated VI-1024 recipe and
include its positive controls. Instrument `osSetEventMesg` for SP/DP
registrations and bounded `sp_complete`/`dp_complete` target records in the
same build, then run one capture from `build/` with SIGKILL watchdog handling.
Do not change queue behavior.

Competing hypotheses:

* H-host-wired: SP registers `0x8011A818` and DP registers `0x8011A7E8`, and completion records target those same addresses.
* H-sp-unwired: SP registration or completion target is absent or differs from `0x8011A818`.
* H-dp-unwired: DP registration or completion target is absent or differs from `0x8011A7E8`.
* H-address-mismatch: both routes fire, but either registration/completion pair resolves to a different queue object.

Discriminator: produce a two-row SP/DP table containing guest queue address,
registration call and target, completion function and target, message/event
kind, and consumer. Positive controls must fire in the same run. Exact matching
registration and completion targets select H-host-wired; a missing/wrong SP
pair selects H-sp-unwired; a missing/wrong DP pair selects H-dp-unwired; a
firing pair with a different queue identity selects H-address-mismatch.

Exact commands:

```sh
sed -n '1,240p' tools/oracle/README.md
sed -n '1,240p' docs/F5-UCODE-REFERENCE.md
rg -n "osSetEventMesg|sp_complete|dp_complete|enqueue_external_message_src" src lib/N64ModernRuntime
cmake --build build --config Debug --target RogueSquadron64Recomp
env ROGUESQ_LOG_ALL=1 pwsh tools/run-stability.ps1 -Runs 1 -Timeout 300 -Tag s1100_submit_queue_wiring
```
