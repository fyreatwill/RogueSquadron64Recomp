// ROGUESQ s7966 class DI (two instances on one data root). Measured offline (tools/s7966_di/harness.cpp): two writers
// on one save path tore the shared .temp (fixed in librecomp files.cpp with per-pid temps), and even with private temps
// the last writer silently wins, so a second copy's save erases the first copy's progress (H-clobber). The first
// instance takes an exclusive flock on <data root>/saves/.rs64_instance.lock for its whole life (the kernel drops it on
// exit or SIGKILL, so a crash never leaves a stale lock); a later instance on the same data root sees it busy.
// ROGUESQ_S7966_NO_LOCK=1 skips the lock (gate mutant).
#pragma once
#include <cerrno>
#include <cstdlib>
#include <cstring>
#include <fcntl.h>
#include <filesystem>
#include <string>
#include <sys/file.h>
#include <system_error>
#include <unistd.h>

// Returns 1 = this process holds the lock, 0 = another process holds it, -1 = could not create/lock (read-only folder,
// skipped by env): treated as "no information", the caller carries on as before.
inline int rs64_instance_lock(const std::filesystem::path& saves_dir, std::string* why) {
    if (std::getenv("ROGUESQ_S7966_NO_LOCK")) { *why = "ROGUESQ_S7966_NO_LOCK"; return -1; }
    std::error_code ec;
    std::filesystem::create_directories(saves_dir, ec);
    const std::string p = saves_dir.string() + "/.rs64_instance.lock";
    const int fd = ::open(p.c_str(), O_RDWR | O_CREAT | O_CLOEXEC, 0644);
    if (fd < 0) { *why = p + ": " + std::strerror(errno); return -1; }
    if (::flock(fd, LOCK_EX | LOCK_NB) == 0) { *why = p; return 1; }  // fd intentionally kept open for the process life
    const int e = errno;
    ::close(fd);
    *why = p + ": " + std::strerror(e);
    return e == EWOULDBLOCK ? 0 : -1;
}
