# s2509 — isolated image-arm pre-title failure

The Debug build completed before the capture. One run launched three arms with
the same phase-relative key recipe: a single image arm and a concurrent
image/silent pair. All processes were SIGKILLed by the watchdog after 120
seconds.

| arm | phase/route evidence | image-task control | terminal result |
|---|---|---:|---|
| single image | reached 1024/0x790400 and 512/0x6AB400 | 1,636 stage rows; phase-10 summary | no crash marker; watchdog kill |
| paired image | reached only the 640 route; no 1024 gate | 0 rows | watchdog kill |
| paired silent | reached 1024/0x790400 and 512/0x6AB400 | phase controls fired | watchdog kill |

No arm emitted `[CRASH]`, `[ABORT]`, `MetalFramebuffer`, access-violation,
missing-function, or `get_function(0)` markers. The single-image arm passed
the positive control and disproves the claim that an image arm by itself
reliably reproduces the earlier renderer failure in this capture window. The
paired silent arm proves the concurrent pair was not globally unable to reach
the target route. The paired image arm failed before its image-task positive
control, so its zero target rows are unevaluable.

This selects `H-concurrent-resource` over `H-image-renderer-resource` for the
observed route failure: the failure requires the concurrent pair in this run,
and the single image arm reaches the target. `H-route-input` is not fully
refuted because the paired image arm diverged before the target gate; no
renderer writer or mitigation is identified.
