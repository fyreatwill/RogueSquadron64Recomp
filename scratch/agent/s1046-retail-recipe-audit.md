# s1046 retail hangar-recipe contract audit

This was a source/config audit only. No game run or freelist watch was used.

| Contract element | README claim | Current implementation/artifact | Result |
|---|---|---|---|
| Schedule | `6:start,11:start,...,56:start` (11 events) | README lines 100–101; s1045 logs contain 11 `sym=40` Start events at those times | Equivalent |
| Button name | `start` is the hangar-driving button | `rs64_oracle.c:g_keynames` maps `start` to 40, the SDL2 scancode used by the input plugin | Equivalent |
| Config label | Start appears as `key(13)` | s1045 configs contain `Start = "key(13)"`, but the source documents that the plugin compares incoming scancodes while config values are SDL1-era keysyms | Not a mismatch in this invocation |
| Physical pad word | Start must reach N64 Start | The source's verified mapping says scancode 40 produces `0x10000000`; s1045 PIF traces delivered all 11 Start words | Positive control passed |
| Hold duration | README omits a duration | Binary default is `g_hold_ms = 150`; director sends keydown at each scheduled time, waits 150 ms, then sends keyup | Current recipe is 150 ms pulses |
| Timing loop | Events occur at the listed seconds | `director` sleeps to each absolute scheduled time; 5 s spacing exceeds the 0.15 s hold | Equivalent |
| Phase observation | 512 at `0x6ab400/0x6ab800` is hangar | README distinguishes 512-origin hangar from attract; oracle reports VI width/origin through callback and poll traces | No mismatch found |

The binary help confirms that named `start` is accepted and that
`--hold-ms` defaults to 150. The s1045 `start_only` and `start_z` logs confirm
the same-build command path used scancode 40, not config key 13. Therefore the
documented recipe is reproducible by the current oracle binary/config at the
input-contract level. The repeated width-320 result selects `H-retail-state`
for the tested 120-second execution; it does not establish why the retail
state machine fails to reach the documented hangar phase.

