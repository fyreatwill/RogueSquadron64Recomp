# NEXT (s7814)
HYPOTHESIS-ID: generated-c-include-resolution
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers in docs/OWNER-REVIEW-QUEUE.md, new
SOAK-RESULTS lines. Any crash/stall or owner report outranks the unit. G6c and all G5 items wait on the owner only.
Why: s7813 found s7812's helper census scanned recomp.h only, while CMake force-includes include/rsp_dpc_macros.h into
RecompiledFuncs (MEM_WU, RS64_DIV32, RS64_TRUNC_W_*, fprintf macro). The class: a header the generated C really compiles against
that no census scans, or a census reading a different copy than the compiler (include/fbld/recomp.h also defines MEM_WU; the
fbld/spwm dirs are BEFORE-include in separate build dirs only).
Unit: ask the compiler, not the CMake text. For the main build (build/) and each optional build dir that exists (fbld, spwm,
asan), take the real compile command of one RecompiledFuncs file + RecompiledPatches + one factor5_ucode file from
compile_commands.json (or `make VERBOSE=1 -n`), run it with `-M` (or -H) to list every resolved header, and table each header:
SCANNED (named by a census tool: s7812 recomp.h, s7813 rsp_dpc_macros.h, ...), SYSTEM (SDK), or UNSCANNED -> list its
function-like macros / static inlines with live call counts in the generated C; live + no evidence = OPEN.
Hypotheses: H-covered (every resolved project header with live helpers is scanned), H-shadow (a census reads a header the main build
does not resolve, or two same-named headers resolve differently between builds), H-unscanned (>=1 live helper in a header no census
reads -> write its row/differential).
Controls: planted -include of a scratch header with a live-named macro -> UNSCANNED/OPEN; a census path pointed at a non-resolved copy
-> SHADOW; drop rsp_dpc_macros.h from the scanned list -> its 6 live helpers read OPEN.
Tools to reuse: tools/s7813_callee_census.py (helpers(), strip(), FHDR rows), tools/s7812_recomp_h_census.py.
