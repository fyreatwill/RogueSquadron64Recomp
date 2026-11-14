// s7359 class AJ: bounded snprintf append. `o += snprintf(b + o, cap - o, ...)` is unsafe once a write truncates: snprintf
// returns the UNtruncated length, o passes cap, and the next `cap - o` wraps to ~2^64 so the following call writes past b.
// rs64_apf returns the new offset clamped to cap - 1 (b stays NUL-terminated); a negative snprintf return leaves o unchanged.
// Byte-identical output to the old idiom whenever nothing truncates (tools/s7359_apf_ctl.cpp checks both properties).
#pragma once
#include <cstdarg>
#include <cstddef>
#include <cstdio>
__attribute__((format(printf, 4, 5)))
static inline int rs64_apf(char* b, size_t cap, int o, const char* fmt, ...) {
    if (cap == 0) return 0;
    if (o < 0) o = 0;
    if ((size_t)o >= cap - 1) { b[cap - 1] = 0; return (int)(cap - 1); }
    va_list ap; va_start(ap, fmt);
    const int r = std::vsnprintf(b + o, cap - (size_t)o, fmt, ap);
    va_end(ap);
    if (r < 0) { b[o] = 0; return o; }
    const size_t n = (size_t)o + (size_t)r;
    return n >= cap ? (int)(cap - 1) : (int)n;
}
