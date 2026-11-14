// s7355 class AF ground truth: which calls in the default-on crash handler (src/main/main.cpp sigaction lambda) are
// actually async-signal-unsafe on THIS macOS libc. Each case runs in a forked child: the child takes the malloc zone
// lock (malloc_zone force_lock, the same lock a crash inside malloc/free leaves held), raises SIGSEGV, and the handler
// performs ONE candidate call, then write(2)s "OK" and _exit(0). Parent waits 3 s: OK = safe under a held malloc lock,
// HANG = deadlock (crash would become a silent freeze), DIED = handler itself crashed/aborted.
// Case "altstack": a deep recursion overflows the thread stack; with no sigaltstack the handler cannot run.
// Positive controls: "malloc" (must HANG/DIED) and "write" (must OK).
#include <malloc/malloc.h>
#include <execinfo.h>
#include <dlfcn.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/wait.h>
#include <pthread.h>
#include <string>
#include <mach/mach.h>
extern "C" void _malloc_fork_prepare(void);
static const char *g_case;
static volatile int g_sink;
static void handler(int sig, siginfo_t *, void *) {
    const char *c = g_case;
    if (!strcmp(c, "write")) { }
    else if (!strcmp(c, "malloc")) { g_sink = (int)(uintptr_t)malloc(64) + (int)(uintptr_t)malloc(2000) + (int)(uintptr_t)malloc(40000); }
    else if (!strcmp(c, "fprintf_int")) { fprintf(stderr, "[ctl] sig %d x=0x%016llx\n", sig, 0x1234ull); }
    else if (!strcmp(c, "fprintf_str")) { fprintf(stderr, "[ctl] %s %p\n", "Segmentation fault", (void *)&g_sink); }
    else if (!strcmp(c, "strsignal")) { g_sink = (int)strlen(strsignal(sig)); }
    else if (!strcmp(c, "backtrace")) { void *f[64]; g_sink = backtrace(f, 64); }
    else if (!strcmp(c, "backtrace_symbols_fd")) { void *f[64]; int n = backtrace(f, 64); backtrace_symbols_fd(f, n, 2); }
    else if (!strcmp(c, "dladdr")) { Dl_info d{}; g_sink = dladdr((void *)&handler, &d); }
    else if (!strcmp(c, "fflush")) { fflush(stderr); }
    else if (!strcmp(c, "string_cstr")) { static std::string s; g_sink = (int)strlen(s.c_str()); }
    else if (!strcmp(c, "pthread_stackaddr")) { g_sink = (int)(uintptr_t)pthread_get_stackaddr_np(pthread_self()); }
    else if (!strcmp(c, "altstack")) { }
    write(1, "OK\n", 3);
    _exit(0);
}
static int recurse(int n) { volatile char buf[4096]; buf[0] = (char)n; return recurse(n + 1) + buf[0]; }
static int run_case(const char *c, bool lock_malloc) {
    pid_t p = fork();
    if (p == 0) {
        g_case = c;
        struct sigaction sa {}; sa.sa_flags = SA_SIGINFO; sigemptyset(&sa.sa_mask); sa.sa_sigaction = handler;
        sigaction(SIGSEGV, &sa, nullptr); sigaction(SIGBUS, &sa, nullptr); sigaction(SIGABRT, &sa, nullptr);
        if (!strcmp(c, "altstack")) { recurse(0); _exit(9); }
        if (lock_malloc) { _malloc_fork_prepare(); }
        *(volatile int *)nullptr = 1;
        _exit(8);
    }
    for (int i = 0; i < 300; i++) {
        int st = 0; pid_t r = waitpid(p, &st, WNOHANG);
        if (r == p) return WIFEXITED(st) && WEXITSTATUS(st) == 0 ? 0 : 2;
        usleep(10000);
    }
    kill(p, SIGKILL); waitpid(p, nullptr, 0); return 1;
}
int main() {
    const char *cases[] = {"write", "malloc", "fprintf_int", "fprintf_str", "strsignal", "backtrace", "backtrace_symbols_fd",
                           "dladdr", "fflush", "string_cstr", "pthread_stackaddr", "altstack"};
    const char *v[] = {"OK", "HANG", "DIED"};
    for (const char *c : cases) {
        int a = run_case(c, false), b = strcmp(c, "altstack") ? run_case(c, true) : a;
        printf("CASE %-22s unlocked=%-4s malloc_locked=%s\n", c, v[a], v[b]);
        fflush(stdout);
    }
}
