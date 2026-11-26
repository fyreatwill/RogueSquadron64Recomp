// ROGUESQ s7964 class RO (unwritable game folder: chmod a-w, a read-only disk image, a folder the user does not own).
// Measured (tools/s7964_ro_e2e.zsh): the game boots fine there (mods/ + mod_config/ failures were already reported by
// s7595), but every game save then fails in librecomp update_save_file, which only prints a generic stderr line per
// attempt -- launched from Finder nobody sees it, so mission progress is lost silently (H-silent). F6 controls.json save
// already reports "SAVE FAILED" in the panel. Fix: probe the save folder once at boot (create + unlink a probe file)
// and, when it is not writable, say so: a one-line [s7964-ro] report, plus one modal dialog before the game starts
// when saving is actually on (ROGUESQ_NO_SAVE_WRITE unset; ROGUESQ_RO_DIALOG=0 keeps the line and drops the dialog).
#pragma once
#include <cerrno>
#include <cstring>
#include <fcntl.h>
#include <filesystem>
#include <string>
#include <system_error>
#include <unistd.h>

// Returns true when a file can be created in `dir` (or, when `dir` does not exist yet, in its parent, where
// librecomp would create it). On false, *why is the strerror text and *where the folder that refused.
inline bool rs64_dir_writable(const std::filesystem::path& dir, std::string* why, std::filesystem::path* where) {
    std::error_code ec;
    std::filesystem::path d = dir;
    if (!std::filesystem::is_directory(d, ec)) d = dir.parent_path();
    if (d.empty()) d = ".";
    *where = d;
    const std::string probe = d.string() + "/.rs64_write_probe." + std::to_string((int)getpid());  // string join, not path::operator/
    const int fd = ::open(probe.c_str(), O_WRONLY | O_CREAT | O_EXCL, 0600);
    if (fd < 0) { *why = std::strerror(errno); return false; }
    ::close(fd);
    ::unlink(probe.c_str());
    return true;
}
