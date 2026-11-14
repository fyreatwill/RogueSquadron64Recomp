// s7356 class AG runtime arm: DYLD-interposed calloc that returns NULL for the first call whose immediate caller's
// symbol contains $S7356_FAIL_IN (e.g. "init_overlays"), so a host allocation failure can be forced at one named site.
// Positive control: S7356_FAIL_IN=__none__ must leave the game booting normally (interposer loaded: "[s7356i] armed").
// Build: clang -dynamiclib -O1 -o scratch/s7356/libfailalloc.dylib tools/s7356_failalloc.c
#include <dlfcn.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <stdio.h>
static int fired, in_hook; static const char *g_m;  // no TLS, no getenv in the hook: both recurse into malloc (first try exited rc 0 at once)
static int want(void *ra) {
    const char *m = g_m;
    if (!m || fired || in_hook) return 0;
    in_hook = 1; Dl_info d; int hit = 0;
    if (dladdr(ra, &d) && d.dli_sname && strstr(d.dli_sname, m)) hit = 1;
    in_hook = 0;
    if (hit) { fired = 1; char b[256]; int n = snprintf(b, sizeof b, "[s7356i] forcing NULL alloc in %s\n", d.dli_sname); write(2, b, n); }
    return hit;
}
static void *my_calloc(size_t n, size_t s) { if (want(__builtin_return_address(0))) return NULL; return calloc(n, s); }
__attribute__((constructor)) static void armed(void) { const char *m = g_m = getenv("S7356_FAIL_IN"); char b[200]; int n = snprintf(b, sizeof b, "[s7356i] armed fail_in=%s\n", m ? m : "(unset)"); write(2, b, n); }
__attribute__((used, section("__DATA,__interpose"))) static struct { void *r, *o; } interp[] = {
    {(void *)my_calloc, (void *)calloc}};
