# s2479 — containing-task completion audit

## Scope

Static audit anchored by the s2478 image log. The question is what can
publish completion or hand off the task after the Factor 5 image arm reaches
`break_pc=0x1328`; no code, instrument, guard, or output mapping was changed.

## Completion/exit table

| Edge | Owner | Reachability after `0x1328` | Meaning |
|---|---|---|---|
| `L_1328`: write `SP_STATUS`, `return RspExitReason::Broke` | generated `build/factor5_ucode/factor5_ucode_b_recompiled.c` | terminal; no fall-through | The image arm exits normally after its two staged DMAs. |
| `DO_DMA_WRITE(r7)` in the image overlay body | generated `factor5_ucode_b` | before `L_1328` | The second image DMA is the last generated data-producing edge observed in this path. |
| `factor5_ucode_b_probe` → `rs64_log_audio_return` | host wrapper in `src/main/main.cpp` | runs after generated return | Records the image join completion witness; it is diagnostic bookkeeping, not game task completion. |
| `rs64_audio_join_image_complete` → `stage.complete_event` | host join reporter in `lib/N64ModernRuntime/librecomp/src/rsp.cpp` | runs after the wrapper return | Sets the diagnostic image-stage event. It explains `complete_event` in `[audtask-image-join]`, not SP status. |
| `run_task` returns `true` | runtime `librecomp/src/rsp.cpp` | after `RspExitReason::Broke` | The runtime accepts the generated exit; no guest completion field is written here. |
| `sp_complete()` from `task_thread_func` | runtime `ultramodern/src/events.cpp` | unconditional after successful `run_task` for queued audio tasks | Enqueues the registered SP event message to the game's queue. This is the containing-task completion publication. |
| `sp_complete()` in `gfx_thread_func` | runtime `ultramodern/src/events.cpp` | GFX action path only | Not reachable from the `M_AUDTASK` image arm because `submit_rsp_task` routes non-GFX tasks to `sp_task_queue`. |
| `dp_complete()` | runtime `ultramodern/src/events.cpp` | GFX path only | No audio-task edge; not a candidate for this completion. |

The generated source tree available in this workspace contains ten Factor 5
recompiled files. All have a normal boot/overlay `Broke` return and a DMA
helper, but only `factor5_ucode_b_recompiled.c` contains the image witness at
`L_1328`; no generated file contains a task-message publication or an output
PCM publication. The target arm's `L_1328` is terminal, so there is no hidden
generated continuation after it.

## Dynamic anchor

s2478's target rows show `stage=2` and `stage=3` DMAs, `break_pc=0x1328`, and
`exit=1`. The same rows have `complete=0` when no source/consumer PCM join is
found. That `complete` field is computed by `audio_join_report_locked` from
source/consumer matches; it is not the runtime SP event. Therefore the
missing image-log completion/output row cannot be interpreted as failure of
the runtime's containing-task completion publication.

## Result

The discriminator selects **H-ContainingTaskRuntime**: containing-task
completion is runtime-owned by the unconditional `task_thread_func` call to
`sp_complete()` after the generated image function returns. The generated
`0x1328` exit is a legitimate terminal image-task contract (**not** a
completion writer). This does not prove that the game consumes the SP message
or that the image output is semantically correct; those are the next dynamic
questions.

This is two-line evidence: the generated/runtime static table and the s2478
dynamic exit/join rows. No mitigation was added.
