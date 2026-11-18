# NEXT (s7593)
HYPOTHESIS-ID: exit-path-census

Class TH closed s7592 (64 sites, 0 open; resize/fullscreen flat at runtime, plant fired). Class EX = the quit path. s7592 found 37
"once" threads that are detached or static and never joined: they keep running while exit() runs static destructors and atexit
handlers (stderr-async restore, RT64 / ultramodern statics). The owner quits with Cmd+Q / window close; a crash or hang there is
invisible in soaks because every soak ends with SIGKILL.
Census (offline, one tool tools/s7593_ex_census.py --controls): every exit route (SDL_QUIT handling, recomp shutdown, std::exit /
_exit / quick_exit / abort calls, atexit / at_quick_exit registrations) and, for each once-detached thread from s7592, which statics it
touches after exit starts (globals with non-trivial destructors in the same TU). Classify: safe (exit uses _exit/quick_exit, or the
thread only touches trivially-destructible state) | race (thread can touch a destroyed static) | join-hang (joined thread waits on
a condition nothing signals after quit).
Hypotheses: H-clean (quit returns rc 0 promptly every time), H-race (a detached thread touches a destroyed static -> SIGSEGV/abort
at quit), H-hang (a join at shutdown never returns).
Runtime witness: N quits of a live L1 fullscreen game via a pushed SDL_QUIT (add a gated lever ROGUESQ_S7593_QUIT_AT=<s>, like
ROGUESQ_FS_TEST_TOGGLE_LIST_S in src/main/main.cpp), record exit rc, wall time to exit and any crash report
(~/Library/Logs/DiagnosticReports newer than the run). Plant: ROGUESQ_S7593_PLANT=1 starts a detached thread that touches a static
std::string in a loop (must produce a crash/abnormal rc at quit in some runs, or the instrument is blind). Quit at hangar, in mission,
and during a load. OWNER SAVE RULE: never clear ROGUESQ_NO_SAVE_WRITE; never touch build/saves.
