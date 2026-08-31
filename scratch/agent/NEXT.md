# NEXT work unit — independent retail status-03 worker contract

HYPOTHESIS-ID: m5-status03-worker-contract

Session 3367 completed the generated static census: no literal generated
indirect target resolves to the named service/child/accumulator consumers;
only register-loaded guest-state callback edges remain. Further static
enumeration is not discriminating. The next M5 unit must obtain independent
retail evidence for the status-03 reaping contract before any wait/slot edit.

Competing hypotheses:

- `H-RetailStatus03Reaped`: retail enters the worker, writes status zero, and
  the shutdown/drain returns through that worker contract.
- `H-RetailStatus03Gate`: retail enters the worker but a slot/status gate
  prevents the zeroing store on the watched route.
- `H-RetailStatus03OtherPath`: completion occurs through an un-watched worker
  or a different status table.

Discriminating measurement: one independent retail oracle capture with the
whole-RDRAM positive control, title/hangar route controls, status-03 entry
watch, all status-zero stores for the actual voice table, and previous-PC
attribution. Reaped requires worker entry → zeroing writer → shutdown/drain
return in the same target phase. Entry without zero selects the gate
hypothesis only if a status/slot gate row is also captured; zero hits with
the positive controls live selects the other-path hypothesis. Missing
whole-RDRAM or target-route control is invalid, not a null result.

Exact preparation:

```sh
rg -n 'status-03|status03|0x80154620|serviceVoicePoolFrame|zero' tools scratch/agent docs/M5-AUDIO-PLAN.md
sed -n '1,220p' tools/oracle/README.md
```

Use the existing retail-oracle driver and arm the whole-RDRAM control before
the bounded status/worker watches in the same run. Do not change behavior or
add a mitigation; if the oracle lacks the required watch surface, report the
missing capability rather than repeating the static census.
