# NEXT (s7961)
HYPOTHESIS-ID: post-preset-class-ladder
s7960 closed class DR (data-root split): saves/ROM/mods now resolve to the launch folder only when it holds game data,
else the executable's folder (src/main/rs64_data_root.h, gate S7960_DR, e2e scratch/s7960/e2e.zsh). Do not redo FW (s7958),
RD (s7959), EV numeric env parses (s7358/s7711/s7713 already cover it), LC (s7953), CK (s7954), TF (s7955).
An src/ edit needs the FULL sweep (`python3 tools/s7651_gate_sweep.py --jobs 2`, >10 min: run it in the background).
0. `python3 tools/crash_reports.py --since 2026-11-25`; fold new SOAK-RESULTS lines.
1. Known residue of DR (small, decide first): settings.txt is found via realpath(exe) (src/main/rs64_settings.cpp exe_path),
   so a SYMLINKED private game dir (g3_port_capture.sh SAVE_FROM) still reads build/settings.txt, while saves/controls are
   private. H-leak (a harness run picks up the owner's settings.txt -> arms not retail) vs H-moot (runner/harness already sets
   ROGUESQ_SETTINGS=0 or build/ has no settings.txt). Discriminator: grep runner.sh / g3_port_capture.sh for ROGUESQ_SETTINGS
   and plant a build-dir-like settings.txt in a scratch game dir launched through a symlink; read [settings] log lines.
2. Otherwise ladder 3c: a NEW host idiom-class audit that commits a guard/proof. Candidate class PS (host paths with
   spaces / non-ASCII): owner folder names; every std::string(path) + "/x" / fopen(path.string()) / u8string conversion in
   src/main + librecomp. Discriminator: run the e2e from a game dir named "Rogue Squadron ü" (copy recipe from e2e.zsh).
