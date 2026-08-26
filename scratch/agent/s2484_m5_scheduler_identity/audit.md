# s2484 — scheduler event-payload/task identity capture

Date: 2026-08-26

## Ground-truth gate

The required retail-oracle attempt ran first with a whole-RDRAM write positive
control and scheduler watches. It failed at startup with
`[oracle] DebugSetCallbacks failed` because the installed Homebrew core is not
the required debugger build. No retail zero or null was interpreted.

## Port capture

The Debug build succeeded. One phase-gated eleven-Start image-arm capture ran
with the qualified LLE route, the target SP lifecycle and image-stage controls,
and `ROGUESQ_LOG_M5_SCHEDULER_ID=1`. It reached hangar
`width=512 origin=0x6AB400`.

Positive controls in that same run were live: target SP guest-receive rows
used queue `0x8011A420`/message `0x80128C70`, and 893 target image-stage rows
were recorded. The scheduler identity control fired for the target phase and
the bounded identity capture produced 256 rows.

The corrected probe is at generated PC `0x80019D28`, immediately after
`lw $v0, 0x4($a0)`, so the event pointer and payload are sampled before the
subsequent `getTimeLow32` call can overwrite `$v0`. Target rows were stable:

| event pointer | event +4 payload | task pointer passed onward |
|---|---|---|
| `0x80128CE0` (one earlier `0x80112AE0`) | `0x800377C8` | `0x800377C8` |

Same-run image-stage ABI rows carried changing task `data_ptr` values in the
`0x8017xxxx` range, including `0x80171E70` and `0x80173CB0`; none equals
`0x800377C8`. The helper's host-struct cast printed endian-invalid fields, so
its decoded `type/data_size/output` values are discarded.

## Verdict

`H-LaterTaskHandoff` selected at the captured `OSTask.data_ptr` join: the
scheduler payload/task pointer is a stable `0x800377C8`, distinct from the
image-stage task data pointers observed in the same run. This rules out an
image-task identity equality at that boundary. It does not identify the
descriptor layout or later slot/voice/PCM/output consumer. No scheduler
behavior, remap, guard, or audio contract changed.

Evidence is two-source for route validity (SP queue lifecycle plus image-stage
rows), with the identity comparison single-source from this port capture;
retail attribution remains unavailable until a debugger core is installed.
