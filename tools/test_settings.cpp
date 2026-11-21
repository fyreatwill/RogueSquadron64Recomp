// s7663: unit test for src/main/rs64_settings.cpp line parsing.
// c++ -std=c++17 tools/test_settings.cpp src/main/rs64_settings.cpp -o /tmp/test_settings && /tmp/test_settings
#include <cstdio>
#include <cstring>
#include <cstdlib>
extern "C" int rs64_settings_parse_line(const char*, char*, size_t, char*, size_t);
extern "C" int rs64_settings_resolve_value(const char*, const char*, const char*, char*, size_t);
int main() {
    struct T { const char* in; int kind; const char* n; const char* v; } t[] = {
        {"", 0, "", ""}, {"   # comment", 0, "", ""}, {"ROGUESQ_FPS60=1", 1, "ROGUESQ_FPS60", "1"},
        {"  ROGUESQ_ASPECT = 16:9 \r", 1, "ROGUESQ_ASPECT", "16:9"}, {"export ROGUESQ_DRAW_DISTANCE=\"4\"", 1, "ROGUESQ_DRAW_DISTANCE", "4"},
        {"env ROGUESQ_FULLSCREEN='1'", 1, "ROGUESQ_FULLSCREEN", "1"}, {"preset=tv", 2, "preset", "tv"},
        {"ROGUESQ_PRESET=ultrawide", 2, "ROGUESQ_PRESET", "ultrawide"},
        {"DYLD_INSERT_LIBRARIES=/x.dylib", -1, "", ""}, {"PATH=/tmp", -1, "", ""}, {"ROGUESQ_=1", -1, "", ""},
        {"ROGUESQ_fps60=1", -1, "", ""}, {"ROGUESQ_SETTINGS=/x", -1, "", ""}, {"ROGUESQ_SETTINGS_APPLIED=1", -1, "", ""},
        {"ROGUESQ_FPS60", -1, "", ""},
        {"ROGUESQ_ASPECT=", 3, "ROGUESQ_ASPECT", ""}, {"ROGUESQ_OSMEM_MB = \"\"", 3, "ROGUESQ_OSMEM_MB", ""}, {"preset=", 3, "preset", ""},  // s7729: empty = unset
        {"DYLD_INSERT_LIBRARIES=", -1, "", ""},
    };
    int fail = 0;
    for (const auto& c : t) {
        char n[256] = "", v[1024] = "";
        const int k = rs64_settings_parse_line(c.in, n, sizeof n, v, sizeof v);
        const bool ok = k == c.kind && (k <= 0 || (!std::strcmp(n, c.n) && !std::strcmp(v, c.v)));
        if (!ok) { fail++; std::printf("FAIL '%s' -> %d '%s' '%s'\n", c.in, k, n, v); }
    }
    // s7667: relative ROGUESQ_CONTROLS resolves beside the settings file; other names and absolute paths are untouched.
    setenv("HOME", "/Users/o", 1);
    struct R { const char* f; const char* n; const char* v; const char* want; } r[] = {
        {"/a/b/settings.txt", "ROGUESQ_CONTROLS", "c.json", "/a/b/c.json"},
        {"/a/b/settings.txt", "ROGUESQ_CONTROLS", "sub/c.json", "/a/b/sub/c.json"},
        {"/a/b/settings.txt", "ROGUESQ_CONTROLS", "/abs/c.json", "/abs/c.json"},
        {"/a/b/settings.txt", "ROGUESQ_CONTROLS", "~/c.json", "/Users/o/c.json"},
        {"rel.txt", "ROGUESQ_CONTROLS", "c.json", "c.json"},
        {"x/rel.txt", "ROGUESQ_CONTROLS", "c.json", "x/c.json"},
        {"/a/b/settings.txt", "ROGUESQ_DRAW_DISTANCE", "4", "4"},
        {"/a/b/settings.txt", "ROGUESQ_ASPECT", "16:9", "16:9"},
    };
    for (const auto& c : r) {
        char o[1300] = "";
        if (rs64_settings_resolve_value(c.f, c.n, c.v, o, sizeof o) != 0 || std::strcmp(o, c.want)) { fail++; std::printf("FAIL resolve %s %s=%s -> '%s'\n", c.f, c.n, c.v, o); }
    }
    std::printf("%s %d cases, %d fail\n", fail ? "FAIL" : "PASS", (int)(sizeof t / sizeof t[0] + sizeof r / sizeof r[0]), fail);
    return fail != 0;
}
