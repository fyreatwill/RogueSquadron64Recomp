# Session 2972 M5 Step 1 qualified-route baseline

The Debug target built successfully once. The first reused wrapper exited
before launching the arms; its oracle log nevertheless showed the expected
whole-RDRAM positive control and title/hangar transitions. A corrected wrapper
was run in the same iteration. It launched silent (`ROGUESQ_AUDIO_UCODE=0`)
and Factor 5 image (`=1`) from the same build.

| Measurement | Silent | Image |
|---|---:|---:|
| `M_AUDTASK` dispatch rows | 59 | 49 |
| phase width transitions | 4 | 4 |
| final target phase | 640 @ `0x0066A500` | 640 @ `0x0066A500` |
| title `1024 @ 0x00790400` | 0 | 0 |
| hangar `512 @ 0x006AB400` | 0 | 0 |
| task/DMEM/DMA/service/PCM rows | 0 | 0 |
| crash/abort markers | 0 | 0 |

The retail oracle control in `oracle-fixed.log` passed the whole-RDRAM
positive control (`10000` callbacks) and observed title and hangar VI origins.
Thus the retail route is independently live, but the port arms did not reach
the target phase in this capture. All downstream audio nulls are
pre-target and unevaluable.

This selects `H-port-route` for this work unit. It rules out neither audio
degeneracy nor an image contract gap. No behavior change or new port
instrumentation was added. The corrected wrapper is retained as the exact
recipe for the next route investigation.
