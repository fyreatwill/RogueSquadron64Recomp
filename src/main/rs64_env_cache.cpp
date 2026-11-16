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

// s7427 class CJ: ROGUESQ_S7427_ENVTRACE=1 records every ROGUESQ_* getenv made before main() finishes its env policy
// (rs64_s7427_policy_done()), keyed by name + caller return address, so tools/s7427_env_policy_order.py --trace can name every
// reader that sees a PRE-policy value. Constant-initialised: safe from static constructors. Off = one relaxed load per getenv.
struct TraceRow { const char* name; uintptr_t ra; uint32_t n; int phase; };
constexpr unsigned kTrace = 1024;
TraceRow g_trace[kTrace];
unsigned g_trace_n = 0;
std::atomic<int> g_trace_mode{-1};    // -1 unknown, 0 off, 1 on, 2 done
std::atomic<int> g_trace_phase{0};    // 0 before main()'s policy, 1 inside it (rs64_s7427_policy_begin)
pthread_mutex_t g_trace_mu = PTHREAD_MUTEX_INITIALIZER;

void trace(const char* name, void* ra) {
    int m = g_trace_mode.load(std::memory_order_relaxed);
    if (m == 0 || m == 2) return;
    if (m < 0) {
        const char* e = real_getenv("ROGUESQ_S7427_ENVTRACE");
        m = (e && e[0] == '1') ? 1 : 0;
        int exp = -1; g_trace_mode.compare_exchange_strong(exp, m);
        m = g_trace_mode.load();
        if (m != 1) return;
    }
    pthread_mutex_lock(&g_trace_mu);
    const int ph = g_trace_phase.load();
    unsigned i = 0;
    for (; i < g_trace_n; ++i)
        if (g_trace[i].ra == (uintptr_t)ra && g_trace[i].phase == ph && std::strcmp(g_trace[i].name, name) == 0) { g_trace[i].n++; break; }
    if (i == g_trace_n && g_trace_n < kTrace) g_trace[g_trace_n++] = TraceRow{strdup(name), (uintptr_t)ra, 1, ph};
    pthread_mutex_unlock(&g_trace_mu);
}
}  // namespace

#include <mach-o/dyld.h>
extern "C" void rs64_s7427_policy_begin() { g_trace_phase.store(1); }
extern "C" void rs64_s7427_policy_done() {
    if (g_trace_mode.load() != 1) { g_trace_mode.store(2); return; }
    pthread_mutex_lock(&g_trace_mu);
    g_trace_mode.store(2);
    const intptr_t slide = _dyld_get_image_vmaddr_slide(0);
    for (unsigned i = 0; i < g_trace_n; ++i)
        std::fprintf(stderr, "[s7427] %s name=%s n=%u ra=0x%llx\n", g_trace[i].phase ? "in" : "pre", g_trace[i].name, g_trace[i].n,
                     (unsigned long long)(g_trace[i].ra - (uintptr_t)slide - 0x100000000ull));
    std::fprintf(stderr, "[s7427] policy-done rows=%u%s\n", g_trace_n, g_trace_n >= kTrace ? " (FULL)" : "");
    pthread_mutex_unlock(&g_trace_mu);
}

extern "C" __attribute__((noinline)) char* getenv(const char* name) {
    if (name && std::strncmp(name, "ROGUESQ_", 8) == 0 && g_trace_mode.load(std::memory_order_relaxed) != 2)
        trace(name, __builtin_return_address(0));
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
