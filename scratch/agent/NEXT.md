# NEXT (s7964)
HYPOTHESIS-ID: post-preset-class-ladder
s7963 closed class AN (App Nap / hidden / SIGSTOP: H-moot, gate S7963_AN, e2e tools/s7963_an_e2e.zsh).
Do not redo AN (s7963), PS (s7962), SD (s7961), DR (s7960), RD (s7959), FW (s7958), CK (s7954), LC (s7953), TF (s7955), EV.
An src/ edit needs the FULL sweep (`python3 -u tools/s7651_gate_sweep.py --jobs 2`, ~28 min: run it in the background).
0. `python3 tools/crash_reports.py --since 2026-11-25`; fold new SOAK-RESULTS lines.
1. Ladder 3c, new host class RO (unwritable game folder). The owner may keep the game on a read-only volume (a mounted DMG, a
   locked folder, a folder they do not own). The game writes to its data root at boot and in play: mods/ + mod_config/ (s7960),
   rs64_*.log diag files, crash reports, controls.json save (F6), settings. Hypotheses: H-fatal (an fopen/mkdir failure aborts or
   crashes boot, or a nullptr FILE* is written to), H-silent (boots, but F6 save / crash reports silently vanish with no message),
   H-moot (every write site handles failure and reports it). Discriminator, one build, 3 arms, 10 s each, SIGKILL, owner save
   copied into a private dir (never build/saves): (a) writable private dir (control: boots, swaps>0, files created);
   (b) same dir after `chmod -R a-w` (save file included, NO_SAVE_WRITE=1 as always); (c) dir on a read-only DMG
   (`hdiutil create -srcfolder <dir> -format UDRO`, `hdiutil attach -readonly`; detach after). Per arm: boot reached (osViSwapBuffer
   count), exit/crash, stderr lines naming failed writes. Then grep-enumerate every fopen(...,"w"/"a")/mkdir/std::ofstream in
   src/main, librecomp, ultramodern and classify each: null-checked / unchecked. Fix unchecked ones; gate S7964_RO with a mutant.
