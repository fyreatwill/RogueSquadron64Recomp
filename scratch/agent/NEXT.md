# Reproduce the VI-640 stall under load, then read the swap-ack log

HYPOTHESIS-ID: vi640-postswap-ack-queue

s4799: mqdiag does not exist; the installed instrument is ROGUESQ_LOG_SWAP_ACK_WAIT=1
(enter/pre-recv/post-recv). 5/5 low-load (5-8) runs left VI 640 at ~48-50 s; no
stall, so no discrimination. Hypotheses: H1 ack never produced (frozen after last
pre-recv, no post-recv), H2 produced but not delivered (same log; need the
queue-side view), H3 intentional drop, H4 delivered but flag 0x8011A8C8 never
clears (repeating enter/pre/post cycles in the log).

Unit: run `zsh scratch/agent/soak_queue/done/s4799_swapack_gated.sh` (copy back
to soak_queue or run directly from repo root, no `timeout` on macOS) while 4+
busy loops (`yes >/dev/null`) push load >= 11; keep stalled runs. Compare
run*_pre.log vs run*_post.log swap-ack line counts: frozen -> H1/H2, growing ->
H4. A run that never stalls is route-invalid. Do not change runtime behavior.
