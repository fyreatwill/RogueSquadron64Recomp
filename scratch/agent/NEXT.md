# Next work unit: REVISIT retail-entry boundary (CURRENT-TRUTH Next steps #2 / M4 notes) with a genuinely new angle, or verify s5381 quick_exit
HYPOTHESIS-ID: generated-symbol-renaming-sweep
Sweep parked (only func_800E9AE0 remains, no semantic name). s5381 changed SDL_QUIT exit() -> quick_exit; verify opportunistically: next run that logs "[main] SDL_QUIT received" should show no SIGABRT/CRASH after it. Prefer a committed guard/tool change over more doc-only work (engineering-pivot counter).
