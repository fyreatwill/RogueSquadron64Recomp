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
    // 0 = skip (blank/comment), 1 = ROGUESQ var, 2 = preset, -1 = rejected
    const std::string l = trim(line ? line : "");
    if (l.empty() || l[0] == '#') return 0;
    const size_t eq = l.find('=');
    if (eq == std::string::npos) return -1;
    std::string n = trim(l.substr(0, eq)), v = trim(l.substr(eq + 1));
    if (v.size() >= 2 && ((v.front() == '"' && v.back() == '"') || (v.front() == '\'' && v.back() == '\''))) v = v.substr(1, v.size() - 2);
    if (n.compare(0, 4, "env ") == 0) n = trim(n.substr(4));
    if (n.compare(0, 7, "export ") == 0) n = trim(n.substr(7));
    const int kind = (n == "preset" || n == "ROGUESQ_PRESET") ? 2 : valid_name(n) ? 1 : -1;
    if (kind < 0 || n.size() + 1 > name_sz || v.size() + 1 > value_sz) return -1;
    std::memcpy(name, n.c_str(), n.size() + 1); std::memcpy(value, v.c_str(), v.size() + 1);
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

extern "C" void rs64_settings_apply(int argc, char** argv) {
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
                if (k == 1) { char r[1300]; from_file.emplace_back(n, rs64_settings_resolve_value(file.c_str(), n, v, r, sizeof r) == 0 ? r : v); }
                else if (k == 2) { if (preset.empty()) preset = v; }
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

    std::fprintf(stderr, "[s7663] settings file=%s%s preset=%s set=%d kept_from_env=%d rejected=%d\n",
        file.empty() ? "(off)" : file.c_str(), file.empty() ? "" : (file_read ? "" : "(absent)"),
        pp ? pp->name : "(none)", set, kept, rejected);
    if (set == 0) return;  // nothing new in the environment: no re-exec needed
    // ROGUESQ_S7663_NOEXEC=1: control arm only (s7663): keep the setenv values but skip the re-exec, so pre-main statics miss them.
    { const char* ne = std::getenv("ROGUESQ_S7663_NOEXEC"); if (ne && *ne == '1') { std::fprintf(stderr, "[s7663] NOEXEC control: no re-exec\n"); return; } }

    setenv("ROGUESQ_SETTINGS_APPLIED", "1", 1);
    setenv("ROGUESQ_SETTINGS_SUMMARY", summary.c_str(), 1);
    std::fflush(stderr);
    keep.push_back(nullptr);
    execv(exe.c_str(), keep.data());
    std::fprintf(stderr, "[s7663] re-exec of %s failed (%s): options read before main() may be missing\n", exe.c_str(), std::strerror(errno));
}
