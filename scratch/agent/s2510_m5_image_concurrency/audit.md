# s2510 — image concurrency control

The Debug target built successfully. One same-build driver launched three
qualified arms concurrently with identical phase-relative input and the
existing positive controls: single image, image plus silent, and silent
control. The watchdog SIGKILLed all arms after 120 seconds.

| arm | route evidence | image positive control | terminal result |
|---|---|---:|---|
| single image | reached 1024/0x790400 and 512/0x6AB400 | image-stage and DMA/join rows; 600 phase rows | alive at watchdog |
| image plus silent | remained at 640; never reached 1024 | 0 target rows | 36 crash rows; `cutsceneDispatchSlotsByFlag+10804`, `last-guest-pc=0x8000834c` |
| silent control | no 1024 target gate in this capture | not applicable | alive at watchdog |

The positive control fired for the single-image arm, so its target rows are
interpretable. The paired-image arm failed before its target control and the
paired-silent arm also failed to reach the target route; their target nulls are
not evidence about image-task behavior.

This supports `H-concurrent-resource` over
`H-image-renderer-resource` for the observed paired-image failure because the
single image arm reached the target without reproducing the renderer crash.
It does not distinguish shared renderer pressure from route/input or
startup-order divergence: the silent peer did not provide a target-phase
control in this run. No writer, mitigation, audio behavior, or output mapping
was changed.
