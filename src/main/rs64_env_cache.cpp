// s7066 hot-getenv audit: process-wide lock-free cache for ROGUESQ_* environment lookups.
//
// Why: the port carries ~2,800 getenv() sites (RecompiledFuncs patches, src/, lib/ ultramodern and
// RT64). tools/s7066_getenv_census.py classifies ~110 generated and ~500 host sites as per-call, and the
// s7065 host samples show libsystem getenv (-> __findenv_locked, the environ lock shared by every
// thread) under streamTerrainGridCellsByDistance, osRecvMesg, queue_samples, setupCameraMatrices and
// RT64 addFramebuffer every second of play. Converting the sites one by one would touch hundreds of
// lines across fixup scripts and lib/; instead this file defines getenv/setenv/unsetenv/putenv in the
// executable image, so the static linker binds every reference in our objects and static libraries here
// (dylibs such as SDL keep libSystem's). Non-ROGUESQ_ names pass straight through to libSystem.
//
// Semantics: identical to getenv for ROGUESQ_* names. Values (including "unset") are cached per name and
// invalidated wholesale by any setenv/unsetenv/putenv made through this image (main()'s policy setenv
// calls). Readers take no lock. ROGUESQ_ENV_CACHE=0 disables the cache (every call goes to libSystem).
#include <atomic>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <dlfcn.h>
#include <pthread.h>

namespace {
using getenv_fn = char* (*)(const char*);
using setenv_fn = int (*)(const char*, const char*, int);
using unsetenv_fn = int (*)(const char*);
using putenv_fn = int (*)(char*);

constexpr unsigned kSlots = 4096;  // power of two; ~1,600 distinct ROGUESQ_ names exist in the tree
struct Slot {
    std::atomic<const char*> key;
    std::atomic<char*> val;
    std::atomic<uint32_t> gen;
};
Slot g_slots[kSlots];                 // constant-initialised (zero): safe for static-init-time callers
std::atomic<uint32_t> g_gen{1};
std::atomic<int> g_mode{-1};          // -1 unknown, 0 off, 1 on
std::atomic<getenv_fn> g_real_getenv{nullptr};
pthread_mutex_t g_mu = PTHREAD_MUTEX_INITIALIZER;

template <typename F> F real(const char* sym) { return reinterpret_cast<F>(dlsym(RTLD_NEXT, sym)); }

char* real_getenv(const char* name) {
    getenv_fn f = g_real_getenv.load(std::memory_order_acquire);
    if (!f) { f = real<getenv_fn>("getenv"); g_real_getenv.store(f, std::memory_order_release); }
    return f(name);
}

inline uint32_t hash_name(const char* s) {
    uint32_t h = 2166136261u;
    for (; *s; ++s) { h ^= (uint8_t)*s; h *= 16777619u; }
    return h;
}

int mode() {
    int m = g_mode.load(std::memory_order_acquire);
    if (m < 0) {
        const char* e = real_getenv("ROGUESQ_ENV_CACHE");
        m = (e && e[0] == '0') ? 0 : 1;
        g_mode.store(m, std::memory_order_release);
        std::fprintf(stderr, "[s7066] env-cache %s\n", m ? "on" : "off (ROGUESQ_ENV_CACHE=0)");
    }
    return m;
}

void invalidate() { g_gen.fetch_add(1, std::memory_order_acq_rel); }
}  // namespace

extern "C" char* getenv(const char* name) {
    if (!name || std::strncmp(name, "ROGUESQ_", 8) != 0 || !mode()) return real_getenv(name);
    const uint32_t h = hash_name(name);
    const uint32_t cur = g_gen.load(std::memory_order_acquire);
    for (unsigned i = 0; i < kSlots; ++i) {
        Slot& s = g_slots[(h + i) & (kSlots - 1)];
        const char* k = s.key.load(std::memory_order_acquire);
        if (!k) break;
        if (std::strcmp(k, name) == 0) {
            if (s.gen.load(std::memory_order_acquire) == cur) return s.val.load(std::memory_order_acquire);
            break;
        }
    }
    // Miss (first lookup of this name, or invalidated by setenv): fill under the writer lock.
    pthread_mutex_lock(&g_mu);
    const uint32_t g = g_gen.load(std::memory_order_acquire);
    char* v = real_getenv(name);
    for (unsigned i = 0; i < kSlots; ++i) {
        Slot& s = g_slots[(h + i) & (kSlots - 1)];
        const char* k = s.key.load(std::memory_order_acquire);
        if (!k) {
            s.val.store(v, std::memory_order_release);
            s.gen.store(g, std::memory_order_release);
            s.key.store(strdup(name), std::memory_order_release);
            break;
        }
        if (std::strcmp(k, name) == 0) {
            s.val.store(v, std::memory_order_release);
            s.gen.store(g, std::memory_order_release);
            break;
        }
    }  // table full: simply uncached
    pthread_mutex_unlock(&g_mu);
    return v;
}

extern "C" int setenv(const char* name, const char* value, int overwrite) {
    static setenv_fn f = real<setenv_fn>("setenv");
    pthread_mutex_lock(&g_mu);
    const int r = f(name, value, overwrite);
    invalidate();
    pthread_mutex_unlock(&g_mu);
    return r;
}

extern "C" int unsetenv(const char* name) {
    static unsetenv_fn f = real<unsetenv_fn>("unsetenv");
    pthread_mutex_lock(&g_mu);
    const int r = f(name);
    invalidate();
    pthread_mutex_unlock(&g_mu);
    return r;
}

extern "C" int putenv(char* str) {
    static putenv_fn f = real<putenv_fn>("putenv");
    pthread_mutex_lock(&g_mu);
    const int r = f(str);
    invalidate();
    pthread_mutex_unlock(&g_mu);
    return r;
}
