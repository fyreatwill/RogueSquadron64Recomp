# NEXT (s7429)
HYPOTHESIS-ID: save-flush-on-quit

First fold new scratch/agent/SOAK-RESULTS.md lines, especially s7428_audio_route_arms (rc 0 = F9 gate verified two-arm;
2 = VOID again: then debug why winctl key no longer reaches the game, compare tools/agent/m6_mission_tmpl.sh.in, which runs
from build/; 3 = control failed).

Class CL (CURRENT-TRUTH Next steps item 1): save durability on quit. The owner quits with Cmd+Q / window close: SDL_QUIT ->
std::quick_exit in main.cpp poll_input (s5380). The save is written by librecomp's saving thread (pi.cpp update_save_file:
open_output_file_with_backup -> write -> finalize: temp + .bak + rename, s7357 class AH checks).
Hypotheses: H-durable (any quit point leaves either the old or the new complete save, never a truncated or missing one, and
the loader falls back to .bak) vs H-window (>=1 quit point between the game's EEPROM write and the file finalize loses the
write or leaves only a .bak / a truncated temp) vs H-stale (pending save_buffer changes still queued when quick_exit runs
are dropped: how long after the in-game "saved" is the file current?).
1. Offline: read pi.cpp saving thread + files.cpp finalize; list each state (temp written, .bak renamed, final renamed) and
   what the loader (open_input_file_with_backup) does from each. Measure the debounce from EEPROM write to file write.
2. Runtime in a COPY of the game folder (never build/saves; env -u ROGUESQ_NO_SAVE_WRITE only in the copy): force a save
   (the s5705 forced-route recipe pokes progression; or call the save path directly via a test env) and SIGKILL at offsets
   0..N ms after the EEPROM write; after each kill, restart and check the save file loads with the expected bytes.
   Positive control: a kill before the write must show the OLD save, a kill well after must show the NEW one.
Write tools/s7429_save_quit.py (+ a .sh for the arms). Exit 0 = H-durable, 1 = window found, 3 = control failed.
