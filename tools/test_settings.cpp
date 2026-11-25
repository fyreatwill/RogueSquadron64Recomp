// s7663: unit test for src/main/rs64_settings.cpp line parsing.
// c++ -std=c++17 tools/test_settings.cpp src/main/rs64_settings.cpp -o /tmp/test_settings && /tmp/test_settings
#include <cstdio>
#include <cstring>
#include <cstdlib>
extern "C" int rs64_settings_parse_line(const char*, char*, size_t, char*, size_t);
extern "C" int rs64_settings_resolve_value(const char*, const char*, const char*, char*, size_t);
extern "C" const char* rs64_settings_bool_word(const char*);
extern "C" int rs64_settings_aspect_ok(const char*);
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
        // s7955: UTF-8 BOM on line 1, CRLF, and shell-style trailing comments.
        {"\xEF\xBB\xBFROGUESQ_FPS60=1", 1, "ROGUESQ_FPS60", "1"}, {"\xEF\xBB\xBFROGUESQ_FPS60=1\r", 1, "ROGUESQ_FPS60", "1"},
        {"\xEF\xBB\xBF# comment", 0, "", ""}, {"\xEF\xBB\xBF", 0, "", ""},
        {"ROGUESQ_DRAW_DISTANCE=4 # dd", 1, "ROGUESQ_DRAW_DISTANCE", "4"}, {"ROGUESQ_FPS60=1\t# on\r", 1, "ROGUESQ_FPS60", "1"},
        {"ROGUESQ_ASPECT=\"16:9\"  # wide", 1, "ROGUESQ_ASPECT", "16:9"}, {"ROGUESQ_CONTROLS='a #b.json' # c", 1, "ROGUESQ_CONTROLS", "a #b.json"},
        {"ROGUESQ_CONTROLS=a#b.json", 1, "ROGUESQ_CONTROLS", "a#b.json"}, {"ROGUESQ_ASPECT= # none", 3, "ROGUESQ_ASPECT", ""},
        {"ROGUESQ_ASPECT=\"16:9 # x\"", 1, "ROGUESQ_ASPECT", "16:9 # x"},
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
    // s7731: whole-value on/off words map to digits; anything else (modes, numbers, partial words) is untouched.
    struct W { const char* v; const char* want; } w[] = {
        {"off", "0"}, {"OFF", "0"}, {"false", "0"}, {"No", "0"}, {"on", "1"}, {"TRUE", "1"}, {"yes", "1"},
        {"0", nullptr}, {"1", nullptr}, {"2", nullptr}, {"t", nullptr}, {"tog3", nullptr}, {"auto", nullptr}, {"16:9", nullptr},
        {"alt", nullptr}, {"", nullptr}, {"onx", nullptr}, {" off", nullptr}, {"n", nullptr},
    };
    for (const auto& c : w) {
        const char* g = rs64_settings_bool_word(c.v);
        if ((g == nullptr) != (c.want == nullptr) || (g && std::strcmp(g, c.want))) { fail++; std::printf("FAIL bool_word '%s' -> %s\n", c.v, g ? g : "null"); }
    }
    // s7732: only auto, expand and W:H (both > 0) are aspects; anything else is unset at launch (retail 4:3).
    struct A { const char* v; int ok; } a[] = {
        {"auto", 1}, {"AUTO", 1}, {"expand", 1}, {"16:9", 1}, {"21:9", 1}, {"4:3", 1}, {"2.3333:1", 1}, {"1024:448", 1},
        {"0", 0}, {"1", 0}, {"orig", 0}, {"off", 0}, {"16x9", 0}, {"16:", 0}, {":9", 0}, {"0:9", 0}, {"16:0", 0},
        {"16:9x", 0}, {"-16:9", 0}, {"16:-9", 0}, {"", 0},
    };
    for (const auto& c : a) {
        const int g = rs64_settings_aspect_ok(c.v);
        if (g != c.ok) { fail++; std::printf("FAIL aspect_ok '%s' -> %d\n", c.v, g); }
    }
    std::printf("%s %d cases, %d fail\n", fail ? "FAIL" : "PASS", (int)(sizeof t / sizeof t[0] + sizeof r / sizeof r[0] + sizeof w / sizeof w[0] + sizeof a / sizeof a[0]), fail);
    return fail != 0;
}
