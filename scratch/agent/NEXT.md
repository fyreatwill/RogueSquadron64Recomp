# NEXT (s7374)
HYPOTHESIS-ID: lazy-static-init-audit

s7373 closed class AQ (tools/s7373_aq_gate_table.py: 68/72 unexecuted rows gated, 4 proven single-thread/input-only).

Work unit: idiom class AR, non-atomic lazy-init statics. Pattern: a function-local or file-scope plain (non-atomic,
non-const) static initialised to a sentinel and filled on first use, e.g.
  static int s_img = -1; ... if (s_img < 0) s_img = (getenv(...)) ? 1 : 0;        (rt64_render_context.cpp:1972)
  static int en = -1; if (en < 0) { ... getenv("ROGUESQ_G5A_WBLIVE") ... }          (upstream_compat.cpp:4746)
  static int s_log_callers = -1;                                                    (upstream_compat.cpp:1123)
`grep -rnE 'static int [A-Za-z_0-9]+ = -1;'` over src + librecomp + ultramodern + rt64 hle/render/gbi = 159 hits; also
cover `static bool x_init = false` / `static T* p = nullptr; if (!p) p = ...` / `static int m = -1; if (m < 0) m = ...`.
Steps (one census, one build):
 1. tools/s7374_lazy_static_census.py: enumerate every site (sentinel decl + the guarded write), skip std::atomic / const /
    magic-static lambdas / thread_local. Per site: the function, and the THREADS that can call it (reuse the s7366 / s7354
    thread-entry map: game thread, gfx/RT64 workload, present, upload, audio SDL callback, RSP task, pollers). --selftest
    with a planted single-thread, multi-thread, atomic and const site.
 2. Classify: SINGLE (one calling thread), MULTI-BENIGN-VALUE (idempotent value, but still UB), MULTI-PTR (pointer or
    multi-field state published without ordering = real defect), INIT-ONLY.
 3. Fix every MULTI-* site by converting to a `static const T x = [] { ... }();` magic static (same value, thread-safe),
    in fixup scripts if the site is generated code; lib/ edits -> ./submodule-patches/export.sh + commit.
 4. Gate: rebuild build/, item-11 censuses with --controls (s7090 fixup census if a fixup changed), a 260 s dd8 21:9 smoke,
    and the TSan arm (tools/build_tsan.sh) boot run: the planted ROGUESQ_S7354_RACE_CTL race must still report (control),
    and no AR site may appear in a report.
Hypotheses: H-few (<= 5 MULTI-PTR sites, the rest SINGLE/benign; convert all MULTI anyway), H-many (> 5 MULTI-PTR: one of
them may explain a rare unexplained default-path symptom; list them against the parked rare dd4/dd8 gfx SIGBUS).
Positive control for the census: the planted selftest sites classify exactly, and the known multi-thread site s_img
(submit_rdp_range runs on the DPC thread AND the gfx thread? verify) must come out MULTI-* or be shown single-thread.
