# NEXT (s7548)
HYPOTHESIS-ID: class-gh-port-static-guest-ptrs

Class GG CLOSED s7547 (tools/s7547_gg_census.py rc 0, controls 6/6): ultramodern/librecomp retain only static guest objects
(heap base 0x80154690) or the fb carve. Residual = the port's own host code: src/main (main.cpp, upstream_compat.cpp,
rt64_render_context.cpp, ~27.5k lines) has statics/atomics that capture a guest address in one hook and use it later
(e.g. s_pending_task_data_ptr / s_pending_task_ucode_data, g_rs64_pcm_task_data_ptr, g_rs64_m5_descriptor_yield_ptr,
g_rs64_m5_clear_object, g_flz_fault_slot, g_s7501_base, root_base/prev_array_base/slot_tbl captures, s6893_base).

Work unit: static census tools/s7548_gh_census.py (--controls), offline.
- Enumerate every namespace-scope or function-static variable in src/main/*.cpp whose type is uint32_t/int32_t/gpr/PTR/atomic
  of those and that is ASSIGNED from a guest-derived value (ctx->rN, rdram_be32/MEM_W load, task->t.* field) — regex + a
  short assignment scan. Exclude const/constexpr literals (classify H-const).
- For each, find its USES: dereference into rdram (TO_PTR/MEM_*/rdram_be32/rdram + x) vs print/compare only.
- Classify H-const (literal guard/diag address), H-diag (print/compare only, or env-gated off by default), H-refresh (re-read
  from guest state on every use, the stored copy is only a cache key), H-inflight (task pointer valid for the task duration;
  class GA), H-static-target (captured value always < 0x80154690 or in the carve, prove from the guest writer), OPEN (default-on
  path dereferences a captured heap pointer later without re-validation).
- Controls: planted static capture + later TO_PTR deref of a heap value -> OPEN; deleted rule -> UNCLASSIFIED; real tree rc 0.
Hypotheses: H-diag-only (every capture outside GA is diagnostic/default-off), H-refresh (default-on ones re-read per use),
H-stale (a default-on capture is dereferenced after the guest may have freed it -> fix: re-read or validate, =0 knob).
Runtime witness only if a row is OPEN: log the captured value + the guest heap block state at deref time on L1/L4/L12.
OWNER SAVE RULE: never clear ROGUESQ_NO_SAVE_WRITE; never touch build/saves. Never flip a default without the owner.
