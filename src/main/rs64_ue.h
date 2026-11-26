// ROGUESQ s7969 class UE (the volume holding the game goes away mid-run: USB stick pulled, `diskutil eject -force`,
// a stick that sleeps). Measured (tools/s7969_ue_e2e.zsh, 256 MB APFS + ExFAT images, `hdiutil detach -force` at 10 s):
//  - exe on the vanished volume: every thread faults at one code address with KERN_MEMORY_ERROR (code pages can no
//    longer be paged in), the SIGBUS handler is itself paged-out code, so the process livelocks at ~660% CPU: no crash
//    report, no save flush, SIGHUP/Cmd-Q never completes. mlock() of the segments does NOT help: __TEXT refuses with
//    EPERM (code-signed text cannot be wired; the other segments wired, measured s7969). Fix: when the executable sits
//    on a volume other than the system or home volume, copy it once to ~/Library/Caches/RogueSquadron64Recomp and
//    execv() the copy (same pid, argv, cwd and fds), passing the original folder in ROGUESQ_S7969_EXE_DIR so the data
//    root (s7960) still resolves to the game folder. Skipped (runs in place) when another loaded image lives on the
//    same volume (a bundled dylib would not load from the copy). ROGUESQ_S7969_RELOC=0 off, =1 also on the internal
//    volume (test).
//  - only saves/ on it: see pi.cpp update_save_file (one report per failure streak) and rs64_s7969_quit_check.
#pragma once
#include <mach-o/dyld.h>
#include <mach-o/loader.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <chrono>
#include <climits>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cerrno>
#include <fcntl.h>
#include <unistd.h>
#include <string>
#include <filesystem>

#include <crt_externs.h>
static bool rs64_s7969_copy(const char* src, const std::string& dst) {
    const std::string tmp = dst + ".tmp." + std::to_string(getpid());
    const int in = open(src, O_RDONLY);
    if (in < 0) return false;
    const int out = open(tmp.c_str(), O_WRONLY | O_CREAT | O_TRUNC, 0755);
    if (out < 0) { close(in); return false; }
    static char buf[1 << 20]; bool ok = true; ssize_t n;
    while ((n = read(in, buf, sizeof buf)) > 0) {
        for (ssize_t o = 0; o < n;) { const ssize_t w = write(out, buf + o, n - o); if (w <= 0) { ok = false; break; } o += w; }
        if (!ok) break;
    }
    if (n < 0) ok = false;
    close(in);
    if (fsync(out) != 0) ok = false;
    if (close(out) != 0) ok = false;
    if (ok) ok = rename(tmp.c_str(), dst.c_str()) == 0;
    if (!ok) unlink(tmp.c_str());
    return ok;
}
static void rs64_s7969_relocate(char** argv) {
    if (const char* from = std::getenv("ROGUESQ_S7969_EXE_DIR")) {
        fprintf(stderr, "[s7969-ue] running a local copy of the game from %s (the original is on an external volume)\n", from);
        return;
    }
    const char* e = std::getenv("ROGUESQ_S7969_RELOC");
    const bool off = e && *e == '0', force = e && *e == '1';
    char raw[PATH_MAX]; uint32_t rsz = sizeof raw; char exe[PATH_MAX];
    if (_NSGetExecutablePath(raw, &rsz) != 0 || !realpath(raw, exe)) { fprintf(stderr, "[s7969-ue] reloc: no exe path\n"); return; }
    struct stat ex {}, hs {}, rs {};
    const char* home = std::getenv("HOME");
    if (stat(exe, &ex) != 0) { fprintf(stderr, "[s7969-ue] reloc: stat(exe) failed\n"); return; }
    const bool have_home = home && *home && stat(home, &hs) == 0, have_root = stat("/", &rs) == 0;
    const bool external = !((have_home && hs.st_dev == ex.st_dev) || (have_root && rs.st_dev == ex.st_dev));
    if (off || (!external && !force) || !have_home) {
        fprintf(stderr, "[s7969-ue] exe on %s volume: runs in place%s\n", external ? "external" : "internal",
                off ? " (ROGUESQ_S7969_RELOC=0)" : (!have_home ? " (no HOME)" : ""));
        return;
    }
    for (uint32_t i = 1; i < _dyld_image_count(); i++) { // image 0 is the executable
        const char* nm = _dyld_get_image_name(i); struct stat is {};
        if (nm && stat(nm, &is) == 0 && is.st_dev == ex.st_dev) {
            fprintf(stderr, "[s7969-ue] exe on external volume: runs in place (it also loads %s from there)\n", nm);
            return;
        }
    }
    namespace fs = std::filesystem; std::error_code ec;
    const fs::path base = fs::path(home) / "Library/Caches/RogueSquadron64Recomp";
    const std::string tag = "exe-" + std::to_string((long long)ex.st_size) + "-" + std::to_string((long long)ex.st_mtimespec.tv_sec);
    const fs::path dir = base / tag, dst = dir / fs::path(exe).filename();
    const auto t0 = std::chrono::steady_clock::now();
    struct stat ds {};
    bool cached = stat(dst.c_str(), &ds) == 0 && ds.st_size == ex.st_size;
    if (!cached) {
        fs::create_directories(dir, ec);
        if (fs::is_directory(base, ec)) // keep one copy: drop older builds' copies
            for (const auto& d : fs::directory_iterator(base, ec)) if (d.path().filename() != tag) fs::remove_all(d.path(), ec);
        if (!rs64_s7969_copy(exe, dst.string())) { fprintf(stderr, "[s7969-ue] exe on external volume: copy to %s failed, runs in place\n", dst.c_str()); return; }
    }
    const double ms = std::chrono::duration<double, std::milli>(std::chrono::steady_clock::now() - t0).count();
    const std::string from = fs::path(exe).parent_path().string();
    setenv("ROGUESQ_S7969_EXE_DIR", from.c_str(), 1);
    fprintf(stderr, "[s7969-ue] exe on external volume: re-exec from local copy %s (%s, %.0f ms)\n", dst.c_str(), cached ? "cached" : "copied", ms);
    fflush(stderr);
    execve(dst.c_str(), argv, *_NSGetEnviron());
    unsetenv("ROGUESQ_S7969_EXE_DIR");
    fprintf(stderr, "[s7969-ue] re-exec failed (errno %d), runs in place\n", errno);
}
