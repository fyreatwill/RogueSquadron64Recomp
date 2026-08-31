# Session 3370 — port status-03 worker contract

## Capture

The initial direct wrapper was route-invalid: it logged only the title phase
and used stale marker names. The fixed run used `tools/probe.sh`, the known
s3364 key schedule, the Factor 5 image arm, and the existing route/task/PCM
probes. It reached title VI `1024 @ 0x00790400` and hangar VI
`512 @ 0x006AB400`; the wrapper stopped after 90 seconds from the phase gate.

Positive controls in the fixed run were 81 audio-task dispatch rows, 2,715
audio ABI rows, 99 source and 99 consumer PCM rows, 4,096 audio-event rows,
and both target phase transitions. There were no crash or abort markers.

## Results

The existing service probe reported, in hangar phase 5:

| Row | Count | Status values |
|---|---:|---|
| `s2020-svc edge=entry` | 4,268 | `00`: 466; `01`: 14; `02`: 618; `03`: 5 |
| `s2020-svc edge=exit` | 4,269 | `00`: 466; `01`: 13; `02`: 618; `03`: 5 |
| exact status-zero store row | 0 | marker not present in this build |

The status-03 entries and exits are therefore real target-phase worker
activity, but this run did not instrument the exact store at `0x8009B7EC`.
The slot-event stream was live, but its observed `slot-sb` rows represented
status `02`, not the missing status-03 zero store.

## Interpretation

Within the planned table this selects `H-PortStatus03Gate`: the named worker
sees status `03` and returns, but no clear is observed. This is a qualified
runtime result, not proof that the store is absent, because the exact-store
marker was unavailable. The run also confirms the image-arm route and rules
out route invalidity, absent audio/task activity, and a crash before hangar.
The static status audit in `s3249` identifies `0x8009B7EC` as the legitimate
worker clear, so no wait or slot behavior change is authorized. A future
probe must add the exact store marker and use the same route.

Evidence: `scratch/agent/s3370_m5_status03_worker_contract/image/run.log`.
