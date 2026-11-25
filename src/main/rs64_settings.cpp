// s7663: owner launch settings. Lets the owner start the game with a saved set of ROGUESQ_* options instead of a long
// `env ...` line: a settings.txt beside the executable, and/or a named preset.
//
//   ./RogueSquadron64Recomp --preset tv          (or ROGUESQ_PRESET=tv)
//   ./RogueSquadron64Recomp --settings my.txt    (or ROGUESQ_SETTINGS=/path/my.txt; ROGUESQ_SETTINGS=0 ignores every file)
//
// settings.txt: one ROGUESQ_NAME=value per line, '#' comments, blank lines ignored; a line `preset=<name>` picks a preset.
// Only ROGUESQ_* names are accepted (nothing else, e.g. no DYLD_*). Precedence: the real environment wins over the file,
// the file wins over the preset. No file and no preset = nothing changes (retail defaults stay the defaults).
//
// Many options are read by file-scope statics before main() runs, so setting them from main() would be too late for
// those readers. When anything is applied, the process re-executes itself (same pid, execv) with the new environment
// and ROGUESQ_SETTINGS_APPLIED=1, so every reader sees the values exactly as if they had been typed on the command line.
#include <cerrno>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <strings.h>
#include <fstream>
#include <string>
#include <utility>
#include <vector>
#include <unistd.h>
#if defined(__APPLE__)
#include <mach-o/dyld.h>
#endif

namespace {

struct Preset { const char* name; const char* what; std::vector<std::pair<const char*, const char*>> vars; };

// The owner's playtest recipe (ITERATION.md G5): FPS60, dd4, wide aspect, fullscreen. "window" is the 4:3 windowed one.
const std::vector<Preset>& presets() {
    static const std::vector<Preset> p = {
        {"retail", "nothing set: retail settings", {}},
        {"window", "4:3 window, 60 fps, draw distance 2",
            {{"ROGUESQ_FPS60", "1"}, {"ROGUESQ_DRAW_DISTANCE", "2"}}},
        {"tv", "16:9 fullscreen, 60 fps, draw distance 4",
            {{"ROGUESQ_FPS60", "1"}, {"ROGUESQ_DRAW_DISTANCE", "4"}, {"ROGUESQ_ASPECT", "16:9"}, {"ROGUESQ_FULLSCREEN", "1"}}},
        {"ultrawide", "21:9 fullscreen, 60 fps, draw distance 4",
            {{"ROGUESQ_FPS60", "1"}, {"ROGUESQ_DRAW_DISTANCE", "4"}, {"ROGUESQ_ASPECT", "21:9"}, {"ROGUESQ_FULLSCREEN", "1"}}},
    };
    return p;
}

std::string trim(const std::string& s) {
    size_t a = 0, b = s.size();
    while (a < b && (s[a] == ' ' || s[a] == '\t' || s[a] == '\r')) a++;
    while (b > a && (s[b - 1] == ' ' || s[b - 1] == '\t' || s[b - 1] == '\r' || s[b - 1] == '\n')) b--;
    return s.substr(a, b - a);
}

bool valid_name(const std::string& n) {
    if (n.compare(0, 8, "ROGUESQ_") != 0 || n.size() == 8) return false;
    for (char c : n) if (!((c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9') || c == '_')) return false;
    return n != "ROGUESQ_SETTINGS" && n != "ROGUESQ_SETTINGS_APPLIED" && n != "ROGUESQ_PRESET";
}

std::string exe_path(const char* argv0) {
#if defined(__APPLE__)
    char buf[4096]; uint32_t sz = sizeof(buf);
    if (_NSGetExecutablePath(buf, &sz) == 0) { char real[4096]; return realpath(buf, real) ? std::string(real) : std::string(buf); }
#endif
    return argv0 ? argv0 : "";
}

}  // namespace

// Returns normally when nothing needs applying (or on any failure); otherwise does not return (execv).
// Exposed for tools/test_settings.cpp: rs64_settings_plan() fills `out` without touching the environment.
extern "C" int rs64_settings_parse_line(const char* line, char* name, size_t name_sz, char* value, size_t value_sz) {
    // 0 = skip (blank/comment), 1 = ROGUESQ var, 2 = preset, 3 = empty value (left unset, s7729), -1 = rejected
    // s7955: a UTF-8 BOM (Windows Notepad, some editors) prefixed line 1 and rejected it, dropping the first setting.
    std::string raw = line ? line : "";
    if (raw.compare(0, 3, "\xEF\xBB\xBF") == 0) raw.erase(0, 3);
    const std::string l = trim(raw);
    if (l.empty() || l[0] == '#') return 0;
    const size_t eq = l.find('=');
    if (eq == std::string::npos) return -1;
    const std::string vraw = l.substr(eq + 1);  // untrimmed: `X= # c` is a comment, `X=#c` a value (sh rules)
    std::string n = trim(l.substr(0, eq)), v = trim(vraw);
    // s7955: shell-style trailing comment (`ROGUESQ_FPS60=1  # on`). Kept, "1  # on" read as 1 at atoi readers and as
    // not-"1" at strcmp readers of the same name (the s7729 split). A '#' starts a comment only after whitespace and
    // outside quotes, as in sh; `a#b` stays a value.
    if (!v.empty() && (v.front() == '"' || v.front() == '\'')) {
        const size_t close = v.find(v.front(), 1);
        if (close != std::string::npos) {
            const std::string rest = trim(v.substr(close + 1));
            if (rest.empty() || rest[0] == '#') v = v.substr(0, close + 1);
        }
    } else {
        for (size_t i = 1; i < vraw.size(); i++)
            if (vraw[i] == '#' && (vraw[i - 1] == ' ' || vraw[i - 1] == '\t')) { v = trim(vraw.substr(0, i)); break; }
    }
    if (v.size() >= 2 && ((v.front() == '"' && v.back() == '"') || (v.front() == '\'' && v.back() == '\''))) v = v.substr(1, v.size() - 2);
    if (n.compare(0, 4, "env ") == 0) n = trim(n.substr(4));
    if (n.compare(0, 7, "export ") == 0) n = trim(n.substr(7));
    const int kind = (n == "preset" || n == "ROGUESQ_PRESET") ? 2 : valid_name(n) ? 1 : -1;
    if (kind < 0 || n.size() + 1 > name_sz || v.size() + 1 > value_sz) return -1;
    std::memcpy(name, n.c_str(), n.size() + 1); std::memcpy(value, v.c_str(), v.size() + 1);
    // s7729: `NAME=` with no value is 3 = left unset. Applied as "", it read as ON at presence readers and OFF at `e && *e`
    // readers of the same name (truth census with "" as a value: ROGUESQ_ASPECT main.cpp:14498 vs fixup_factor5_ucode.py:228,
    // ROGUESQ_OSMEM_MB main.cpp:14381 vs 14860). Unset is the one reading every reader agrees on.
    if (v.empty()) return 3;
    return kind;
}

// s7667: a relative file path given in a settings file means "beside that settings file", not "beside wherever the game
// was started from" (measured s7667: `ROGUESQ_CONTROLS=c.json` in a --settings file loaded nothing and silently fell back
// to the default controls). Only path-valued names are touched; "~/" expands to $HOME. Returns the value to apply.
extern "C" int rs64_settings_resolve_value(const char* settings_file, const char* name, const char* value, char* out, size_t out_sz) {
    std::string v = value ? value : "";
    const std::string n = name ? name : "";
    const bool is_path = n == "ROGUESQ_CONTROLS";
    if (is_path && !v.empty()) {
        if (v.compare(0, 2, "~/") == 0) { const char* h = std::getenv("HOME"); if (h && *h) v = std::string(h) + v.substr(1); }
        else if (v[0] != '/' && settings_file && *settings_file) {
            const std::string f = settings_file; const size_t sl = f.rfind('/');
            if (sl != std::string::npos) v = f.substr(0, sl + 1) + v;
        }
    }
    if (v.size() + 1 > out_sz) return -1;
    std::memcpy(out, v.c_str(), v.size() + 1);
    return 0;
}

extern char** environ;
// s7730: an empty shell value (`ROGUESQ_X= ./game`) is unset for every reader. Left as "", presence readers took the opt-in
// branch and `e && *e` readers did not: ROGUESQ_ASPECT= gave the high-DPI opt-in window at 4:3, and ROGUESQ_OSMEM_MB= at
// dd>1 blocked the bundle's setenv(.., "12", 0) so the 12 MB / 0x81000000 spill layout (owner LEVEL=15 fix) was lost.
// Returns how many were removed; the caller re-execs so file-scope statics read before main() see them unset too.
// ROGUESQ_S7730_KEEP_EMPTY=1 = old behaviour (control arm).
static int rs64_s7730_strip_empty() {
    const char* ke = std::getenv("ROGUESQ_S7730_KEEP_EMPTY");
    if (ke && *ke == '1') return 0;
    // Rescan after each unsetenv (it edits environ in place); no container grows.
    int n = 0;
    for (char buf[256]; n < 4096; n++) {
        buf[0] = 0;
        for (char** e = environ; e && *e; e++) {
            const char* eq = std::strchr(*e, '=');
            if (eq && eq[1] == '\0' && std::strncmp(*e, "ROGUESQ_", 8) == 0 && (size_t)(eq - *e) < sizeof buf) {
                std::snprintf(buf, sizeof buf, "%.*s", (int)(eq - *e), *e); break;
            }
        }
        if (!buf[0]) break;
        unsetenv(buf);
        std::fprintf(stderr, "[s7730] %s= is empty: treated as unset\n", buf);
    }
    return n;
}

// s7731: on/off words. Every reader of a ROGUESQ_* switch tests digits (`*e != '0'`, `*e == '1'`, atoi), so a typed word read
// against intent: `=off`/`=false`/`=no` turned non-'0' opt-ins ON (FPS60, ASPECT, CULL_SPIKE stayed on) and `=on`/`=yes`/`=true`
// read OFF at `*e == '1'` readers (the QOS family) and `=true` picked s6919 mode 't' (tog3). Truth census s7731: no reader
// compares against these words, so mapping them (whole value, any case) to "0"/"1" changes nothing that reads digits.
// Returns "0", "1" or nullptr (not a word: value untouched).
extern "C" const char* rs64_settings_bool_word(const char* v) {
    if (!v) return nullptr;
    static const char* const off[] = {"off", "false", "no"};
    static const char* const on[] = {"on", "true", "yes"};
    for (const char* w : off) if (strcasecmp(v, w) == 0) return "0";
    for (const char* w : on) if (strcasecmp(v, w) == 0) return "1";
    return nullptr;
}

static bool rs64_s7731_keep_words() {
    const char* kw = std::getenv("ROGUESQ_S7731_KEEP_WORDS");
    return kw && *kw == '1';
}

// Names whose own reader gives a word's first letter a meaning of its own: left untouched. The truth census (s7731 letter
// scan) fails on any reader testing 'o'/'f'/'n'/'y' that is not listed here. (The 't' tog-mode letter is NOT kept: "true"
// selecting tog mode was the against-intent reading.)
static const char* const kKeepWords[] = {
    "ROGUESQ_DD_OFFMAPCULL_H",  // upstream_compat.cpp: h[0]=='o' = gate off, a number = margin ("0" = margin 0 = gate ON)
    "ROGUESQ_HUD_MARKCLS",      // apply_s6146b_hudpc.py: cl[0]=='x' / 'y' select a mark class (diag)
};

// Rewrite every ROGUESQ_*=<word> in environ to its digit. setenv(.., 1) edits environ in place; rescan after each, no container.
static int rs64_s7731_norm_words() {
    if (rs64_s7731_keep_words()) return 0;
    int n = 0;
    for (char buf[256]; n < 4096; n++) {
        buf[0] = 0;
        const char* d = nullptr;
        for (char** e = environ; e && *e; e++) {
            const char* eq = std::strchr(*e, '=');
            if (!eq || std::strncmp(*e, "ROGUESQ_", 8) != 0 || (size_t)(eq - *e) >= sizeof buf) continue;
            bool keep = false;
            for (const char* k : kKeepWords) keep |= std::strlen(k) == (size_t)(eq - *e) && std::strncmp(*e, k, eq - *e) == 0;
            if (keep) continue;
            d = rs64_settings_bool_word(eq + 1);
            if (d) { std::snprintf(buf, sizeof buf, "%.*s", (int)(eq - *e), *e); std::fprintf(stderr, "[s7731] %s=%s read as %s\n", buf, eq + 1, d); break; }
        }
        if (!buf[0] || !d) break;
        setenv(buf, d, 1);
    }
    return n;
}

// s7732: ROGUESQ_ASPECT is a value, not a switch. Its readers take presence as "opt in": main.cpp `(as && *as) || fullscreen`
// opens the high-DPI fitted window, and the ucode iteration cap (fixup_factor5_ucode.py) counts any value other than "4:3" as
// wide and lifts the cap 16384 -> 65536 at dd1. So ASPECT=0 / =off (s7731 maps off to "0") / =orig / any typo read as a
// partial opt-in while RT64 kept the retail aspect. Only auto, expand and W:H (both > 0) mean anything: any other value is
// unset (retail 4:3) with a log line. ROGUESQ_S7732_KEEP_ASPECT=1 = old behaviour (control arm).
extern "C" int rs64_settings_aspect_ok(const char* v) {
    if (!v) return 0;
    if (!strcasecmp(v, "auto") || !strcasecmp(v, "expand")) return 1;
    const char* c = std::strchr(v, ':');
    if (!c || c == v) return 0;
    char* end = nullptr;
    const double w = std::strtod(v, &end);
    if (end != c || !(w > 0.0)) return 0;
    const double h = std::strtod(c + 1, &end);
    return *end == '\0' && h > 0.0 && end != c + 1;
}

static int rs64_s7732_aspect() {
    const char* k = std::getenv("ROGUESQ_S7732_KEEP_ASPECT");
    if (k && *k == '1') return 0;
    const char* a = std::getenv("ROGUESQ_ASPECT");
    if (!a || rs64_settings_aspect_ok(a)) return 0;
    std::fprintf(stderr, "[s7732] ROGUESQ_ASPECT=%s is not an aspect (auto, expand or W:H): treated as unset (retail 4:3)\n", a);
    unsetenv("ROGUESQ_ASPECT");
    return 1;
}

extern "C" void rs64_settings_apply(int argc, char** argv) {
    int stripped = rs64_s7730_strip_empty() + rs64_s7731_norm_words();
    const char* done = std::getenv("ROGUESQ_SETTINGS_APPLIED");
    if (done && *done == '1') {
        const char* sum = std::getenv("ROGUESQ_SETTINGS_SUMMARY");
        std::fprintf(stderr, "[s7663] settings applied (re-exec): %s\n", sum ? sum : "?");
        return;
    }
    // Our own flags; everything else is passed through untouched.
    std::string preset, file_arg;
    std::vector<char*> keep; keep.push_back(argc > 0 ? argv[0] : (char*)"RogueSquadron64Recomp");
    for (int i = 1; i < argc; i++) {
        const std::string a = argv[i];
        if ((a == "--preset" || a == "--settings") && i + 1 < argc) { (a == "--preset" ? preset : file_arg) = argv[++i]; continue; }
        if (a.compare(0, 9, "--preset=") == 0) { preset = a.substr(9); continue; }
        if (a.compare(0, 11, "--settings=") == 0) { file_arg = a.substr(11); continue; }
        if (a == "--list-presets") {
            for (const auto& p : presets()) {
                std::fprintf(stderr, "  %-10s %s", p.name, p.what);
                for (const auto& v : p.vars) std::fprintf(stderr, " %s=%s", v.first, v.second);
                std::fprintf(stderr, "\n");
            }
            continue;
        }
        keep.push_back(argv[i]);
    }
    if (preset.empty()) { const char* e = std::getenv("ROGUESQ_PRESET"); if (e && *e) preset = e; }

    const std::string exe = exe_path(argc > 0 ? argv[0] : nullptr);
    std::string file;
    const char* se = std::getenv("ROGUESQ_SETTINGS");
    const bool files_off = se && std::strcmp(se, "0") == 0;
    if (!file_arg.empty()) file = file_arg;
    else if (se && *se && !files_off) file = se;
    else if (!files_off) { const size_t sl = exe.rfind('/'); file = (sl == std::string::npos ? std::string(".") : exe.substr(0, sl)) + "/settings.txt"; }

    std::vector<std::pair<std::string, std::string>> from_file;
    int rejected = 0;
    bool file_read = false;
    if (!file.empty()) {
        std::ifstream in(file);
        if (in) {
            file_read = true;
            std::string line; int ln = 0;
            while (std::getline(in, line)) {
                ln++;
                char n[256], v[1024];
                const int k = rs64_settings_parse_line(line.c_str(), n, sizeof n, v, sizeof v);
                if (k == 1) { char r[1300]; bool kw = rs64_s7731_keep_words(); for (const char* k : kKeepWords) kw |= std::strcmp(k, n) == 0; const char* bw = kw ? nullptr : rs64_settings_bool_word(v); from_file.emplace_back(n, bw ? bw : rs64_settings_resolve_value(file.c_str(), n, v, r, sizeof r) == 0 ? r : v); }
                else if (k == 2) { if (preset.empty()) preset = v; }
                else if (k == 3) std::fprintf(stderr, "[s7729] %s:%d %s= has no value: left unset (empty reads differ between readers)\n", file.c_str(), ln, n);
                else if (k < 0) { rejected++; std::fprintf(stderr, "[s7663] %s:%d ignored (only ROGUESQ_NAME=value or preset=name): %s\n", file.c_str(), ln, line.c_str()); }
            }
        } else if (!file_arg.empty() || (se && *se && !files_off)) {
            std::fprintf(stderr, "[s7663] settings file %s not readable (%s); continuing without it\n", file.c_str(), std::strerror(errno));
        }
    }

    const Preset* pp = nullptr;
    if (!preset.empty()) {
        for (const auto& p : presets()) if (preset == p.name) pp = &p;
        if (!pp) {
            std::fprintf(stderr, "[s7663] unknown preset '%s' (known:", preset.c_str());
            for (const auto& p : presets()) std::fprintf(stderr, " %s", p.name);
            std::fprintf(stderr, "); continuing without it\n");
        }
    }

    // Real environment > file > preset: setenv(..., 0) never overwrites, so apply in that precedence order.
    int set = 0, kept = 0;
    std::string summary;
    auto put = [&](const std::string& n, const std::string& v, const char* src) {
        if (std::getenv(n.c_str())) { kept++; return; }
        setenv(n.c_str(), v.c_str(), 0); set++;
        if (!summary.empty()) summary += ' ';
        summary += n + "=" + v + "(" + src + ")";
    };
    for (const auto& kv : from_file) put(kv.first, kv.second, "file");
    if (pp) for (const auto& v : pp->vars) put(v.first, v.second, "preset");
    if (rs64_s7732_aspect()) {  // after the file/preset: a settings-file ASPECT=0 is caught too
        stripped++;
        if (!summary.empty()) summary += " ROGUESQ_ASPECT(unset: not an aspect, s7732)";
    }

    std::fprintf(stderr, "[s7663] settings file=%s%s preset=%s set=%d kept_from_env=%d rejected=%d\n",
        file.empty() ? "(off)" : file.c_str(), file.empty() ? "" : (file_read ? "" : "(absent)"),
        pp ? pp->name : "(none)", set, kept, rejected);
    if (set == 0 && stripped == 0) return;  // nothing new in the environment: no re-exec needed
    // ROGUESQ_S7663_NOEXEC=1: control arm only (s7663): keep the setenv values but skip the re-exec, so pre-main statics miss them.
    { const char* ne = std::getenv("ROGUESQ_S7663_NOEXEC"); if (ne && *ne == '1') { std::fprintf(stderr, "[s7663] NOEXEC control: no re-exec\n"); return; } }

    if (summary.empty()) summary = "(none; " + std::to_string(stripped) + " empty value(s) unset (s7730) / on-off word(s) read as 0/1 (s7731) / non-aspect ASPECT unset (s7732))";
    setenv("ROGUESQ_SETTINGS_APPLIED", "1", 1);
    setenv("ROGUESQ_SETTINGS_SUMMARY", summary.c_str(), 1);
    std::fflush(stderr);
    keep.push_back(nullptr);
    execv(exe.c_str(), keep.data());
    std::fprintf(stderr, "[s7663] re-exec of %s failed (%s): options read before main() may be missing\n", exe.c_str(), std::strerror(errno));
}
