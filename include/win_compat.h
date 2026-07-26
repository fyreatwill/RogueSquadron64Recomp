#ifndef RS64_WIN_COMPAT_H
#define RS64_WIN_COMPAT_H

// POSIX stand-ins for the Win32 primitives the diagnostic code uses, so the
// probes keep working on macOS/Linux without per-site #ifdefs.
#ifndef _WIN32

#include <cstdint>
#include <chrono>
#include <execinfo.h>
#include <pthread.h>

typedef unsigned short USHORT;

static inline uint64_t GetTickCount64() {
    return (uint64_t)std::chrono::duration_cast<std::chrono::milliseconds>(
        std::chrono::steady_clock::now().time_since_epoch()).count();
}

static inline uint64_t GetCurrentThreadId() {
#ifdef __APPLE__
    uint64_t tid = 0;
    pthread_threadid_np(nullptr, &tid);
    return tid;
#else
    return (uint64_t)pthread_self();
#endif
}

static inline USHORT RtlCaptureStackBackTrace(unsigned skip, unsigned count, void** frames, void*) {
    int n = backtrace(frames, (int)count);
    (void)skip;
    return (USHORT)(n > 0 ? n : 0);
}

#endif // !_WIN32
#endif // RS64_WIN_COMPAT_H
