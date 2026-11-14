# NEXT (s7355): idiom-class audit - class AF, async-signal-unsafe calls inside signal handlers
HYPOTHESIS-ID: host-signal-handler-safety
Context: s7354 closed class AE with a ThreadSanitizer build (tools/build_tsan.sh, build_tsan/; report grouper
tools/s7354_tsan_report.py; Mach-semaphore blind-spot control tools/s7354_sem_ctl.cpp). One default-on race fixed (VI state
flip outside message_mutex in ultramodern events.cpp) + sample_rate made atomic. Reuse build_tsan for any later race question:
`env TSAN_OPTIONS="log_path=$PWD/scratch/<dir>/tsan halt_on_error=0" BUILD=$PWD/build_tsan WIDE_ROUTE=1 ...` with
ROGUESQ_S7354_RACE_CTL=1 as the same-run positive control. tools/build_tsan.sh now re-runs `cmake -S . -B build` at the end
(configuring a second build dir drops build/'s spirv-cross rules).
Idiom (class AF): a function installed with sigaction/signal (SIGSEGV/SIGBUS/SIGILL/SIGABRT/SIGUSR*, 7 install sites, all in
src/main/main.cpp) calling something not on the POSIX async-signal-safe list: malloc/new, fprintf/printf/std::string, locking a
std::mutex, dladdr/backtrace_symbols, std::getenv after setenv, C++ iostream. Hazard: a crash taken while the faulting thread holds
the malloc or stdio lock deadlocks the handler (a crash turns into a hang with no report: G5c freeze / VI-stall lookalike).
Hypotheses: H-safe (handlers only touch atomics / write(2) / pre-formatted buffers), H-diag (unsafe calls only in env-gated
diagnostic handlers), H-unsafe (the default-on crash reporter calls fprintf/malloc: fix with a write(2) + preformatted buffer path,
or a dedicated reporter thread fed through a pipe).
Method: new tools/s7355_sighandler_census.py: (1) list every sigaction/signal install and its handler; (2) call graph within
main.cpp + 1 cross-file level from each handler; (3) flag each call against the POSIX async-signal-safe list (write, _exit,
sigaction, raise, clock_gettime, ...; atomics allowed). Classes SAFE / D / G / B / ?.
Controls: planted handler calling fprintf ('?'), write(2) twin (SAFE), gated twin (G).
Second line: a standalone control that takes SIGSEGV while another thread holds the stdio lock (flockfile(stderr)) and shows
an fprintf-based handler hangs while a write(2) handler returns. Then, for any B fix, 260 s dd8 smoke:
`env SECS=260 zsh scratch/s7326/run.zsh s7355_dd8 ''`.
Exit: PORTING-STATE s7355, CURRENT-TRUTH item 27t -> closed/fixed, commit.
