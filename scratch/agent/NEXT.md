# NEXT: owner reports first; otherwise RDP forwarding coverage of the DPC bridge
HYPOTHESIS-ID: rdp-submit-coverage
Context: the RSP side is closed end to end (s7091 fixups, s7092 VU, s7093 scalar, s7094 DMA/cop0, s7095 DPC registers:
src/rsp/s7095_dpc_model.cpp shadow, 0 branch-relevant differences). Untested is the next layer: does src/rsp/dpc_bridge.cpp
rsp_dpc_submit_impl (high-water mark s_submit_last_end, wrap flush ROGUESQ_DPC_WRAP_FLUSH, deferral rs64_dpc_defer_*,
s7027 bump fast path, prewrap) forward to RT64 exactly the bytes hardware would consume, i.e. the union of [CURRENT, END)
per END write, each once and in order?
Hypotheses: H-fwd-exact (forwarded byte stream == hardware consumption stream) vs H-fwd-drop (some ranges never reach RT64,
e.g. at ring wraps or task boundaries: a candidate for G5b terrain drops) vs H-fwd-dup (ranges forwarded twice: a candidate
for duplicated draws or cost) vs H-fwd-order (all bytes, wrong order across a wrap).
Unit (ONE instrument, ONE run):
1. Extend s7095_dpc_model.cpp: on each shadow END write, append the hardware-consumed range [cur, END) to a per-task list;
   in rs64_dpc_record_submit (dpc_bridge.cpp ~5929) append the forwarded range; at task end (rs64_s7095_task) compare the
   two lists as byte sets and as sequences: count missing bytes, duplicated bytes, out-of-order ranges, per task, with the
   first 8 examples (task, range, wrap flag).
2. Positive control in the self-test (drop one range, duplicate one range, swap two ranges: each must be flagged), plus a
   same-run mutant arm ROGUESQ_S7095_DPC=ctl that skips forwarding one range per 1000 tasks in the comparison only.
3. Run scratch/s7095/run.zsh (L6 dd1 4:3) and then the same at dd4 16:9 (owner recipe, ring wraps more often) back to back.
Outcomes: 0/0/0 at both = H-fwd-exact (close the bridge); missing>0 = H-fwd-drop, name the code path (wrap/defer/fast path)
and fix it; dup>0 = H-fwd-dup; order>0 = H-fwd-order.
