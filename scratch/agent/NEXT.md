# NEXT (s7965)
HYPOTHESIS-ID: post-preset-class-ladder
s7964 closed class RO (unwritable game folder: boot OK, saves lost silently -> boot probe + dialog, gate S7964_RO, e2e tools/s7964_ro_e2e.zsh).
Do not redo RO (s7964), AN (s7963), PS (s7962), SD (s7961), DR (s7960), RD (s7959), FW (s7958), CK (s7954), LC (s7953), TF (s7955), EV.
An src/ edit needs the FULL sweep (`python3 -u tools/s7651_gate_sweep.py --jobs 2`, ~28 min: run it in the background).
0. `python3 tools/crash_reports.py --since 2026-11-25`; fold new SOAK-RESULTS lines.
1. Ladder 3c, new host class DI (two instances at once). The owner can double-click the game twice (Finder, Dock, a second terminal).
   Both share <data root>/saves/rs64.n64.us.1.0.bin, its `.tmp`/`.bak` (librecomp files.cpp temp_suffix: same temp path for both
   writers), controls.json(.tmp), audio_device.txt, the audio device and any rs64_* diag file. Hypotheses: H-corrupt (two writers
   interleave on the shared temp path -> a torn or mixed save is renamed over the real one), H-clobber (no corruption, but the last
   writer silently wins and the other instance's progress is lost), H-moot (a lock or single-instance check already exists).
   Discriminator, offline first (no game run needed for the core question): a harness that drives librecomp's
   open_output_file_with_backup + finalize_output_file_with_backup from 2 processes x 2000 iterations on a scratch file with distinct
   payloads, counting finals that are neither payload A nor payload B (torn) -> H-corrupt if > 0. Positive control: the same harness
   with ROGUESQ_S7429_OLD_FINALIZE=1 (copy, known torn under kill, s7429). Then one live arm: two instances from one PRIVATE game copy
   (owner save copied, NO_SAVE_WRITE=1), 10 s, both boot? audio? Fix candidates: per-process temp name (pid suffix) and/or an flock
   single-instance guard on saves/ with a clear message. Gate S7965_DI with a mutant (shared temp name restored).
