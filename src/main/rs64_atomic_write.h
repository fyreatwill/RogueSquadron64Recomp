// s7958 class FW (host file writers): owner-state files must never be left empty or partial.
// Opening the target for "w" truncates it first, so a quit/SIGKILL/full disk between it and fclose left an empty file that
// the next run reads as a real value (audio_device.txt empty -> "default" route, not the owner's choice).
// Write a sibling temp, check every step, fsync, then rename over the target (atomic on POSIX): the target is
// always either the old or the new complete text. Returns false (and leaves the old file) on any failure.
#pragma once
#include <cerrno>
#include <cstdio>
#include <cstring>
#include <string>
#include <cstdlib>
#include <unistd.h>

// s7966 class DI: two instances on one data root shared "<file>.tmp" and could truncate each other's temp mid-write.
// The temp carries the pid (ROGUESQ_S7966_SHARED_TEMP=1 = old shared name, gate mutant).
inline std::string rs64_private_tmp_path(const std::string& path) {
    std::string t = path + ".tmp";
    if (!std::getenv("ROGUESQ_S7966_SHARED_TEMP")) t += "." + std::to_string((long)getpid());
    return t;
}

inline bool rs64_write_file_atomic(const std::string& path, const std::string& text, std::string* err = nullptr) {
    const std::string tmp = rs64_private_tmp_path(path);
    FILE* f = std::fopen(tmp.c_str(), "wb");
    if (!f) { if (err) *err = std::string("open ") + tmp + ": " + std::strerror(errno); return false; }
    bool ok = std::fwrite(text.data(), 1, text.size(), f) == text.size();
    ok = (std::fflush(f) == 0) && ok;
    ok = ok && ::fsync(::fileno(f)) == 0;
    ok = (std::fclose(f) == 0) && ok;
    if (ok && std::rename(tmp.c_str(), path.c_str()) == 0) return true;
    if (err) *err = std::string("write ") + path + ": " + std::strerror(errno);
    std::remove(tmp.c_str());
    return false;
}
