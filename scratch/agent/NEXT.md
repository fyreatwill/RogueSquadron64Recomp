# NEXT (s7962)
HYPOTHESIS-ID: post-preset-class-ladder
s7961 closed class SD (settings.txt now follows the s7960 data-root rule; gate S7961_SD, e2e tools/s7961_sd_e2e.zsh).
Do not redo FW (s7958), RD (s7959), DR (s7960), SD (s7961), EV (s7358/s7711/s7713), LC (s7953), CK (s7954), TF (s7955).
An src/ edit needs the FULL sweep (`python3 -u tools/s7651_gate_sweep.py --jobs 2`, ~28 min: run it in the background).
0. `python3 tools/crash_reports.py --since 2026-11-25`; fold new SOAK-RESULTS lines.
1. Ladder 3c, new host idiom-class audit PS (owner folder paths with spaces / non-ASCII / very long). Enumerate every
   std::string(path)+"/x", fopen(path.string()), u8string/c_str() conversion, snprintf into fixed char[] path buffers
   (PATH_MAX truncation) in src/main + lib/N64ModernRuntime/librecomp. Hypotheses: H-break (some reader fails or truncates:
   ROM import, saves, settings, controls, audio_device) vs H-moot (all std::filesystem, no fixed buffers below 1024).
   Discriminator: copy scratch/s7961/e2e.zsh, run from a private game dir named "Rogue Squadron ü/very long..." (>255-char
   total path) and check [s7960-root], [s7663], ROM found (no "[ROM] Place"), save read, controls loaded. Positive control:
   the same recipe from a plain ASCII dir. Commit a gate that census-lists every fixed-size path buffer.
