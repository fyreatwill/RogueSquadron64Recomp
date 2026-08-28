# Session 3044 — M5 audio-task publication-to-consumer audit

## Scope

This is a bounded static audit of the task handoff requested by `NEXT.md`.
No build, runtime probe, or behavior change was justified by the source
evidence. The audit is single-source for the host scheduling path; the retail
libultra entry points are present as assembly includes in the companion tree,
but their bodies are not available as C source there.

## Complete handoff table

| Edge | Location | Observed contract |
|---|---|---|
| Game submits SP task | `src/main/upstream_compat.cpp:1334-1403` | The project override receives the guest `OSTask*` in `ctx->r4`, records it with `rs64_set_pending_task_guest_ptr(..., release)`, then calls `ultramodern::submit_rsp_task(rdram, ctx->r4)`. The release store is diagnostic publication only; the queue is the actual task handoff. |
| Guest pointer diagnostic publication | `src/main/main.cpp:804-815` | `s_pending_task_guest_ptr` is an atomic `uint32_t`; the submitter uses release and the diagnostic consumer uses acquire. It publishes only the guest address, not a copied descriptor. |
| Queue selection | `lib/N64ModernRuntime/ultramodern/src/events.cpp:1011-1025` | `submit_rsp_task` reads `task->t.type`. `M_GFXTASK` is copied into the renderer action queue; every other type, including `M_AUDTASK`, is enqueued as the original `OSTask*` on `sp_task_queue`. |
| First queue consumer | `events.cpp:682-694` | `task_thread_func` blocks on `sp_task_queue`, receives the pointer, caches `task->t.type`, then calls `ultramodern::rsp::run_task(PASS_RDRAM task)`. No intermediate task-field rewrite or arm selection occurs. |
| RSP dispatch | `lib/N64ModernRuntime/librecomp/src/rsp.cpp:967-1017` | `run_task` calls the host callback `get_rsp_microcode(task)` before DMEM staging. The callback and the task consumer are on the same SP task thread. `run_task` then copies the descriptor to DMEM and DMAs `ucode_data`; the existing `rs64_dmem_lock` provides ordering against the shared-DMEM gfx runner. |
| Audio pending descriptor | `src/main/main.cpp:3069-3108` | `get_rsp_microcode` handles `M_AUDTASK` by assigning the consumer-thread-local `s_pending_audio_task = task`, caching `data_ptr`/`data_size`, publishing the PCM task data pointer with a relaxed store, and selecting `factor5_ucode_b_probe` unless `ROGUESQ_AUDIO_UCODE=0`. |
| First selected-arm consumer | `src/main/main.cpp:2116-2122` | `factor5_ucode_b_probe` calls `rs64_audio_route_prepare("factor5_ucode_b")`, then `rs64_m5_task_handoff(s_pending_audio_task)`, then executes the Factor 5 image arm. The silent arm has the same ordering at `2108-2113`. |
| Handoff observation | `src/main/main.cpp:1430-1468` | The observer reads the thread-local descriptor and the diagnostic guest pointer with acquire. It reports `task_ptr`, `data_ptr`, and `data_size`, but does not alter task data or route selection. |
| Completion signal | `events.cpp:694-730` | After `run_task` returns, the SP task thread emits the SP completion message. Failure exits through the existing runtime path; successful audio tasks call `sp_complete`. |
| Scheduler/descriptor side channel | `src/main/main.cpp:1471-1530`, `1541-1649` | The optional scheduler and descriptor breadcrumbs use release/acquire atomics for payload/yield diagnostics. They are not consumed by `get_rsp_microcode` or by either audio arm, so they cannot currently explain route selection. |

## Competing hypotheses and result

- **H-TaskPublicationMissing:** not selected by this audit. The host submit
  override always forwards the received task pointer, and the non-GFX queue
  explicitly accepts `M_AUDTASK`.
- **H-TaskPublicationStale:** not selected in the host path. The queue is a
  producer/consumer synchronization boundary, and the diagnostic pointer has
  release/acquire ordering. A remaining concern is lifetime/reuse of the
  guest RDRAM descriptor because the queue carries a pointer rather than a
  copy; this audit cannot prove whether retail code mutates that descriptor
  before consumption.
- **H-TaskConsumerWrong:** not selected. The first consumer reads the same
  queued pointer, dispatches by its type, and the audio arm reads the same
  descriptor after `get_rsp_microcode` records it.
- **H-StaticInsufficient:** selected for this static scope. No missing writer,
  wrong queue, missing ordering edge, or wrong arm field boundary was found.

The discriminator therefore remains unresolved at the route boundary: the
source path is present, but it does not establish that the guest task
descriptor is immutable between submission and SP-thread consumption. That is
the only concrete handoff concern left by this audit, and it needs independent
retail or same-build temporal evidence before any change.

