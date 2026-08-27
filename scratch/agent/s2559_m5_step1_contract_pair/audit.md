# s2559 M5 Step 1 contract checkpoint

The Debug target built successfully. The staged recipe passed the independent
retail whole-RDRAM positive control at 10,000 callbacks and observed title and
hangar phases. Silent and image arms both reached title and hangar and ended
by SIGKILL with zero crash or abort markers.

| arm | ABI rows | generated DMA ranges | DMEM change | image exit | PCM source/consumer |
|---|---:|---:|---:|---|---:|
| silent | 1472 | 0 | 0 | stub return | 94 / 94 |
| image | 1136 | 2328 | 1597 | `break_pc=0x1328`, `exit=1` | 88 / 88 |

The image execution controls are positive, but the image arm did not produce
a distinct downstream PCM edge. This selects `H-contract-gap` at the current
observable boundary and does not authorize dispatch promotion or any task,
output, gate, guard, or mitigation change. Full logs are in `driver.log` and
the arm/oracle log files in this directory.
