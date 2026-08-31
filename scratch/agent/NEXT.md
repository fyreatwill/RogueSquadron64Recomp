# NEXT work unit — independent retail status-03 worker contract

HYPOTHESIS-ID: m5-status03-worker-contract

The SP task-pointer API class is now source-complete: both load and start
boundaries validate a complete `OSTask`. The next unit returns to M5 Step 7,
but requires independent retail evidence before changing the wait/slot path.

Competing hypotheses:

- `H-RetailStatus03Reaped`: retail enters the worker, writes status zero, and
  shutdown/drain returns through that worker contract.
- `H-RetailStatus03Gate`: retail enters the worker but a slot/status gate
  prevents the zeroing store on the watched route.
- `H-RetailStatus03OtherPath`: completion uses an un-watched worker or a
  different status table.

Discriminating measurement: one retail-oracle run with the whole-RDRAM
positive control, title/hangar route controls, status-03 worker entry, all
zeroing stores for the actual voice table, and previous-PC attribution.
Worker entry → zeroing writer → shutdown/drain return selects reaping; entry
without zero selects the gate only if a gate row also fires; zero hits with
controls live selects another path. Missing controls make the run invalid.

Preparation and run surface:

```sh
rg -n 'status-03|status03|0x80154620|serviceVoicePoolFrame|zero' tools scratch/agent docs/M5-AUDIO-PLAN.md
sed -n '1,220p' tools/oracle/README.md
```

Use the existing retail-oracle driver. Arm the whole-RDRAM control before the
bounded status/worker watches in the same run. Do not change behavior or add
a mitigation until the writer/value contract is captured.
