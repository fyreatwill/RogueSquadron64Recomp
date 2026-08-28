# Session 3043 — VI commit to route-prepare ordering audit

## Scope and discriminator

This was a bounded static audit, with no build or run. The discriminator was
the complete writer/publication/consumer table: if a committed-VI writer was
missing, that would select a host edge for ground-truth-backed work; if the
publication was misordered, it would select the exact publication edge; if a
consumer cleared or selected the wrong identity, it would select that edge.
Otherwise the VI-640 route failure remains unexplained by this boundary.

## Writer-to-consumer table

| Edge | Code path | Data and ordering | Consumer / consequence |
|---|---|---|---|
| VI request writer | `osViSetMode_recomp` in `src/main/upstream_compat.cpp:386-448` | Decodes the guest `OSViMode`, then calls runtime `osViSetMode`. Runtime locks `message_mutex` and writes `events_context.vi.get_next_state()->mode`, `mode_guest`, and `control`. | The next retrace/update consumes the queued mode. This is a request, not a committed-register write. |
| Framebuffer request writer | `osViSwapBuffer_recomp` in `src/main/upstream_compat.cpp:217-350` | Calls runtime `osViSwapBuffer`, which under `message_mutex` writes `get_next_state()->framebuffer`. | The next retrace/update consumes the queued framebuffer. |
| Diagnostic commit publication | `osViSetMode_recomp` calls `rs64_m5_vi_commit_handoff` immediately after `osViSetMode` returns. | `g_m5_vi_commit` publishes a sequence, caller, requested width, and the *current* `VI_WIDTH_REG`/`VI_ORIGIN_REG`; the release store is `latest_sequence`. The actual next-state mode has not yet been committed to the VI registers. | This snapshot is used only by `rs64_m5_route_prepare_handoff` for logging. It is not read by route preparation or audio dispatch. Therefore the label `vi-commit` is temporally early for the actual VI commit, but this cannot cause `accepted=0`. |
| Actual VI commit writer | `ultramodern::renderer::events_context.vi.update_vi` in `lib/N64ModernRuntime/ultramodern/src/events.cpp:404-456` | On the VI update/retrace thread, selects the next state and field, computes physical framebuffer plus field origin, then writes `VI_ORIGIN_REG`, `VI_WIDTH_REG`, timing, scale, and status. `rs64_vi_boundary_log("commit", ...)` follows those writes. | `rs64_vi_committed_width()` and `rs64_vi_committed_origin()` observe these registers. This is the only actual committed-VI writer found. |
| Route-prepare reader | `rs64_audio_route_prepare` in `src/main/main.cpp:1358-1425` | Clears thread-local `g_rs64_audio_identity`, reads `rs64_vi_committed_width/origin`, and accepts only `(1024,0x790400)` or `(512,0x6AB400)`. | Called by `musyx_stub_probe` and `factor5_ucode_b_probe`; on accepted target phases it creates the route identity used by task/audio probes. It does not read `g_m5_vi_commit`. |
| Audio return fallback | `rs64_log_audio_return` in `src/main/main.cpp:2085-2104` | If no identity exists, calls route preparation again before recording the RSP exit. | Same live-register predicate; no commit snapshot or sequence dependency. |
| Route transition logger | `rs64_m5_route_prepare_handoff` in `src/main/upstream_compat.cpp:490-525` | Reads the latest diagnostic snapshot and compares its width/origin key with the route-preparation arguments. | Logging only. A key mismatch would identify request/commit telemetry skew, not alter route selection. |

## Caller and order metadata

The companion symbol map identifies `initVideoSubsystem` (`0x8001A098`),
`initVideoBootWrapper` (`0x80018468`), `advanceVideoFrame` (`0x8001818C`),
`swapBufferWithViMode` (`0x8001BA9C`), `viRetraceHandlerThread`
(`0x80019868`), `submitGfxFrame` (`0x8000C07C`), and
`bufferArbiterProducerMark` (`0x8001BCE4`). Their documented roles separate
next-state request production from retrace-thread register commitment. The
generated host route does not insert an additional VI commit writer or
consume the diagnostic sequence. No caller/order edge was found that could
make route preparation use the snapshot instead of the live registers.

## Decision

The audit confirms a diagnostic publication ordering mismatch: the
`g_m5_vi_commit` record is created at the request edge, before the actual
retrace-thread commit. This is a telemetry naming/order defect, not a route
selection defect, because the route consumer uses the live VI registers and
the snapshot has no control-flow or data-flow edge into it.

The actual route boundary remains `VI 640 / origin 0x0066A500` with
`accepted=0`; this audit neither explains nor repairs it. No mitigation or
behavior change is justified. A future run should investigate the distinct
audio-task publication/consumer edge, retaining the positive route controls.
