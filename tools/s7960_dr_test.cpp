// s7960 class DR unit harness for src/main/rs64_data_root.h (built by tools/s7960_dr_gate.py).
#include "rs64_data_root.h"
#include <cstdio>
#include <fstream>
#include <unistd.h>
namespace fs = std::filesystem;
static fs::path old_rule(const fs::path& cwd, const fs::path&, const char*, const char** why) { *why = "old"; return cwd; }
int main(int argc, char** argv) {
    fs::path t = fs::temp_directory_path() / ("s7960_" + std::to_string(::getpid()));
    fs::remove_all(t);
    fs::path exe = t / "game", empty = t / "away", saves_only = t / "s", rom_only = t / "r";
    for (auto& d : { exe, empty, saves_only, rom_only }) fs::create_directories(d);
    fs::create_directories(exe / "saves"); std::ofstream(exe / "rs64.n64.us.1.0.z64") << "x";
    fs::create_directories(saves_only / "saves"); std::ofstream(rom_only / "rogue_squadron.z64") << "x";
    struct C { fs::path cwd; fs::path exe; const char* mode; fs::path want; } cs[] = {
        { exe, exe, nullptr, exe },             // owner: cd build && ./RogueSquadron64Recomp
        { empty, exe, nullptr, exe },           // Finder / repo-root launch
        { saves_only, exe, nullptr, saves_only },  // private harness dir with its own saves/
        { rom_only, exe, nullptr, rom_only },   // fresh install, ROM in the launch folder
        { empty, exe, "cwd", empty },           // ROGUESQ_DATA_ROOT=cwd restores the old rule
        { empty, fs::path(), nullptr, empty },  // no exe path: keep cwd
        { empty, exe, "exe", exe },             // unknown mode = default rule
    };
    int n = 0, old_bad = 0, new_bad = 0;
    for (auto& c : cs) {
        const char* w = ""; ++n;
        if (rs64_pick_data_root(c.cwd, c.exe, c.mode, &w) != c.want) { ++new_bad; printf("NEW miss case %d (%s)\n", n, w); }
        if (old_rule(c.cwd, c.exe, c.mode, &w) != c.want) ++old_bad;
    }
    fs::remove_all(t);
    printf("DR old_bad=%d new_bad=%d cases=%d\n", old_bad, new_bad, n);
    (void)argc; (void)argv; return 0;
}
