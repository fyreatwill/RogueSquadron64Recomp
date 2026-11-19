// s7663: unit test for src/main/rs64_settings.cpp line parsing.
// c++ -std=c++17 tools/test_settings.cpp src/main/rs64_settings.cpp -o /tmp/test_settings && /tmp/test_settings
#include <cstdio>
#include <cstring>
extern "C" int rs64_settings_parse_line(const char*, char*, size_t, char*, size_t);
int main() {
    struct T { const char* in; int kind; const char* n; const char* v; } t[] = {
        {"", 0, "", ""}, {"   # comment", 0, "", ""}, {"ROGUESQ_FPS60=1", 1, "ROGUESQ_FPS60", "1"},
        {"  ROGUESQ_ASPECT = 16:9 \r", 1, "ROGUESQ_ASPECT", "16:9"}, {"export ROGUESQ_DRAW_DISTANCE=\"4\"", 1, "ROGUESQ_DRAW_DISTANCE", "4"},
        {"env ROGUESQ_FULLSCREEN='1'", 1, "ROGUESQ_FULLSCREEN", "1"}, {"preset=tv", 2, "preset", "tv"},
        {"ROGUESQ_PRESET=ultrawide", 2, "ROGUESQ_PRESET", "ultrawide"},
        {"DYLD_INSERT_LIBRARIES=/x.dylib", -1, "", ""}, {"PATH=/tmp", -1, "", ""}, {"ROGUESQ_=1", -1, "", ""},
        {"ROGUESQ_fps60=1", -1, "", ""}, {"ROGUESQ_SETTINGS=/x", -1, "", ""}, {"ROGUESQ_SETTINGS_APPLIED=1", -1, "", ""},
        {"ROGUESQ_FPS60", -1, "", ""},
    };
    int fail = 0;
    for (const auto& c : t) {
        char n[256] = "", v[1024] = "";
        const int k = rs64_settings_parse_line(c.in, n, sizeof n, v, sizeof v);
        const bool ok = k == c.kind && (k <= 0 || (!std::strcmp(n, c.n) && !std::strcmp(v, c.v)));
        if (!ok) { fail++; std::printf("FAIL '%s' -> %d '%s' '%s'\n", c.in, k, n, v); }
    }
    std::printf("%s %d cases, %d fail\n", fail ? "FAIL" : "PASS", (int)(sizeof t / sizeof t[0]), fail);
    return fail != 0;
}
