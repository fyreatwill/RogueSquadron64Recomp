# NEXT (s7594)
HYPOTHESIS-ID: signal-disposition-census

Class EX closed s7593 (62 exit rows, 0 open; quit now consumed on the main thread; ultramodern fatal exit drains async stderr).
Class SG = what the process does on the signals the owner can cause without Cmd+Q: closing the Terminal tab/window that launched
the game (SIGHUP to the foreground job), Ctrl+C (SIGINT), Ctrl+\ (SIGQUIT), `kill` (SIGTERM), and a dead stderr/stdout reader
(SIGPIPE: e.g. the game piped into `tee`/`less` that exits). SDL turns SIGINT/SIGTERM into SDL_QUIT (s7593 sigterm arms rc0, save
flush ran); SIGHUP/SIGPIPE/SIGQUIT have default dispositions unless something installs handlers -> process dies with no save flush.
Census (offline, tools/s7594_sg_census.py --controls): every signal()/sigaction()/SDL_HINT_NO_SIGNAL_HANDLERS/sigprocmask/pthread_sigmask
site in src/ + lib/ (incl. the s7355 crash handlers), per signal: handler, mask, which threads, and the resulting action.
Hypotheses: H-clean (every owner-reachable signal ends in save flush + rc0, or is harmless), H-silent (SIGHUP/SIGPIPE kill the game
with no flush and no log line), H-hang (a handler blocks, e.g. the async-stderr writer on a dead pipe -> game stalls).
Runtime witness (scratch/s7594/run.zsh, reuse scratch/s7593/run.zsh shape, one game at a time, L1 owner recipe): per signal
(HUP, PIPE via a reader that exits, INT, QUIT, TERM) record rc, exit wall ms, whether "[s7429-quit] save flush" printed, crash lines.
Positive controls: TERM (known rc0 + flush, s7593) and a plant ROGUESQ_S7594_PLANT=<sig> that installs SIG_DFL for TERM (must turn
the TERM arm into rc 143 with no flush). OWNER SAVE RULE: never clear ROGUESQ_NO_SAVE_WRITE; never touch build/saves.
