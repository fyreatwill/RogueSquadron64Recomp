// ROGUESQ s7960 class DR (data-root split). Before s7960 the data root (saves/, the stored ROM, mods/, mod_config/,
// mods.json) was the LAUNCH folder, while settings.txt, controls.json and audio_device.txt were read next to the
// executable. Launched from any other folder (Finder double-click -> cwd = $HOME, or `build/RogueSquadron64Recomp`
// from the repo root) the owner's settings applied but the ROM and save were not found, and mods/ + mod_config/ were
// created in that folder. Rule: keep the launch folder when it holds game data (every existing recipe: `cd build`,
// private harness dirs), else use the executable's folder (as invoked, NOT realpath'd, so a symlinked private game
// dir stays private). ROGUESQ_DATA_ROOT=cwd restores the old launch-folder rule.
#pragma once
#include <filesystem>
#include <string>
#include <system_error>

inline bool rs64_dir_has_game_data(const std::filesystem::path& dir) {
    static const char* names[] = { "rs64.n64.us.1.0.z64", "saves", "rogue_squadron.z64", "rogue squadron.z64",
                                   "RogueSquadron.z64", "rs64.z64" };
    if (dir.empty()) return false;
    for (const char* n : names) {
        std::error_code ec;
        if (std::filesystem::exists(dir / n, ec) && !ec) return true;
    }
    return false;
}

// Returns the data root and sets *why to "cwd-data", "exe-dir", "cwd-forced" or "cwd-noexe".
inline std::filesystem::path rs64_pick_data_root(const std::filesystem::path& cwd, const std::filesystem::path& exe_dir,
                                                 const char* mode, const char** why) {
    if (mode && std::string(mode) == "cwd") { *why = "cwd-forced"; return cwd; }
    if (rs64_dir_has_game_data(cwd)) { *why = "cwd-data"; return cwd; }
    if (exe_dir.empty()) { *why = "cwd-noexe"; return cwd; }
    *why = "exe-dir"; return exe_dir;
}
