# s2511 M5 staggered image concurrency

The same-build driver waited for the single-image process to report
`vi_width=1024` before starting the paired image-plus-silent arms. All arms
used phase-relative input and the existing task/gate/image controls.

| arm | target gate | image-stage rows | image-DMA joins | first crash / end |
|---|---:|---:|---:|---|
| single-image | yes | 2,287 | 926 | `do_rom_read+572`, guest `0x80001B08` |
| pair-image | yes | 3,274 | 1,392 | `updateHangarBayScene+76424`, guest `0x800AC8C0` |
| pair-silent | yes | 0 | 0 | SIGKILL after capture; no crash marker |

The staggered pair reached the 1024 positive control and then reached the
512/hangar route, so the paired-image pre-target failure from s2509/s2510 is
not a persistent shared-resource failure under this startup order. This
supports `H-startup-order` for that pre-target symptom and refutes
`H-concurrent-resource` as its sufficient explanation. It does not explain
the later image-arm crashes: the single-image baseline also crashed after
its target route, at a different host/guest site. The image-stage and DMA
controls fired, but all observed image joins remained stage-only with zero
source/consumer identity; no writer or mitigation conclusion is authorized.
