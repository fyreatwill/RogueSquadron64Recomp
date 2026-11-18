# NEXT (s7607)
HYPOTHESIS-ID: exception-unwind-census

Class HC closed s7606 (tools/s7606_hc_census.py, 8 sites 0 open, controls 7/7, witness 9/9).
Next idiom class UW: C++ exceptions that unwind THROUGH generated C frames. ultramodern::thread_terminated is thrown from
host stubs (osDestroyThread/osStopThread of self, wait_for_resumed, ...) called from recompiled C, and caught at the thread
roots (_thread_func, wait_for_game_started). Enumerate: (1) every `throw` of thread_terminated (grep lib/N64ModernRuntime src);
(2) every try/catch root; (3) every host frame between a throw and its root that holds a lock, a std::unique_lock, a
heap allocation without RAII, or a static state flag (s7392/s7394-style guards) that the unwind would skip; (4) build flags of
the RecompiledFuncs / factor5_ucode / src TUs: any -fno-exceptions, -fno-unwind-tables, -fno-asynchronous-unwind-tables, or
C TUs compiled without unwind info on arm64 (Darwin default emits it: verify with `otool -l` / `objdump --unwind-info`
on one funcs_N.c.o: every function must have a compact-unwind entry).
Contract per throw path: unwind reaches a catch, every skipped host frame is RAII-clean or explicitly restored.
Verdicts: ok, ok-gated, BAD. Hypotheses: H-clean, H-bad-gated, H-bad-live (a default-path throw skips a lock/flag release).
Tool tools/s7607_uw_census.py --controls: (1) plant a throw site with no reaching catch root -> OPEN; (2) plant a
mutex.lock() (non-RAII) on a throw path -> OPEN; (3) plant -fno-exceptions on the funcs target in a CMake copy -> OPEN;
(4) drop a row -> OPEN.
Second source: a witness that links one real generated funcs_N.c.o-style C frame (compile a tiny C function calling a host
callback that throws) and checks the catch fires with -fexceptions off for the C TU (Darwin unwind tables) — and a control
TU built with -fno-asynchronous-unwind-tables -fno-unwind-tables that must terminate().
Never touch build/saves; never clear ROGUESQ_NO_SAVE_WRITE.
