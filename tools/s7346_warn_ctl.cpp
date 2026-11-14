#include <cstdarg>
#include <cstdio>
#include <cwchar>
#include <string>
#include <exception>
static std::string fmt_old(const char *msg, ...) {
    std::string s; va_list va1, va2; va_start(va1, msg); va_copy(va2, va1);
    int reqSize = vsnprintf(nullptr, 0, msg, va1);
    s.resize(reqSize);
    if (reqSize > 0) vsnprintf(s.data(), reqSize, msg, va2);
    va_end(va1); va_end(va2); return s;
}
static std::string fmt_new(const char *msg, ...) {
    std::string s; va_list va1, va2; va_start(va1, msg); va_copy(va2, va1);
    int reqSize = vsnprintf(nullptr, 0, msg, va1);
    if (reqSize < 0) reqSize = 0;
    s.resize(size_t(reqSize));
    if (reqSize > 0) vsnprintf(s.data(), size_t(reqSize) + 1, msg, va2);
    va_end(va1); va_end(va2); return s;
}
int main() {
    int fails = 0;
    int probe = snprintf(nullptr, 0, "%lc", (wint_t)0xD800);
    printf("probe vsnprintf(%%lc 0xD800) = %d (must be < 0 for the control)\n", probe);
    try { auto s = fmt_old("%lc", (wint_t)0xD800); printf("old: no throw len=%zu\n", s.size()); }
    catch (const std::exception &e) { printf("old: THREW %s (defect reproduced)\n", e.what()); fails |= 1; }
    try { auto s = fmt_new("%lc", (wint_t)0xD800); printf("new: ok len=%zu\n", s.size()); }
    catch (const std::exception &e) { printf("new: THREW %s\n", e.what()); fails |= 2; }
    auto a = fmt_old("tile %d", 42), b = fmt_new("tile %d", 42);
    printf("normal: old='%s' new='%s'\n", a.c_str(), b.c_str());
    bool pass = probe < 0 && (fails == 1) && b == "tile 42";
    printf("[s7346] warn control %s\n", pass ? "PASS" : "FAIL");
    return pass ? 0 : 1;
}
