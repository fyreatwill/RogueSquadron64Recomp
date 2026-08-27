# s2656 M5 task producer census

The retail oracle passed the whole-RDRAM positive control with 1,030 hits and
reached title `1024 @ 0x00790400` and hangar `512 @ 0x006AB400`. Its phase-gated
type-2 rows used task pointer `0x80149470`; sampled `output_buff` and
`output_buff_size` were always zero.

The rebuilt port image and silent arms both reached title and hangar. The
producer-side `osSpTaskLoad` snapshots for task `0x80149470` were zero in both
arms and both phases:

| arm | data pointer | rows | output / size |
|---|---|---:|---|
| image | `0x80171CE0` | 86 | `0 / 0` |
| image | `0x80171E70` | 86 | `0 / 0` |
| image | `0x80173B20` | 82 | `0 / 0` |
| image | `0x80173CB0` | 85 | `0 / 0` |
| silent | `0x80171CE0` | 85 | `0 / 0` |
| silent | `0x80171E70` | 85 | `0 / 0` |
| silent | `0x80173B20` | 83 | `0 / 0` |
| silent | `0x80173CB0` | 87 | `0 / 0` |

Image task snapshots supplied a nonzero output contract, proving the port
snapshot/ABI path is live. Static enumeration found no direct generated
`M_AUDTASK`, `output_buff`, or `output_buff_size` references and no fixed task
field stores; the scheduler passes the received task pointer through. This
selects `H-ProducerNeverSetsOutput` only for the direct-store class, refutes
task-pointer mismatch at dispatch, and leaves generic copy initialization open.

Artifacts: `oracle.log`, `image.log`, `silent.log`, and
`run_s2656_m5_task_producer.sh`.
