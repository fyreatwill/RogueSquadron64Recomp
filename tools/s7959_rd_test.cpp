// s7959 class RD harness: feed planted owner-state file contents through the real readers and report what each yields.
// audio: old = the pre-s7959 fgets+trim reader (control, inlined verbatim), new = rs64_audio_pref_from_text.
// controls: every byte prefix + NUL fill + empty of a remapped controls.json through rs64_bind_parse_json.
#include <cstdio>
#include <string>
#include <vector>
#include "rs64_owner_text.h"
#include "rs64_bindings_json.h"
static std::string old_trim(std::string v) {
    while (!v.empty() && (v.back() == '\n' || v.back() == '\r' || v.back() == ' ' || v.back() == '\t')) v.pop_back();
    size_t i = 0; while (i < v.size() && (v[i] == ' ' || v[i] == '\t')) ++i; return v.substr(i);
}
// Returns the route the run would use: "BUILTIN" (no file / ignored), "DEFAULT" (system output) or the name.
static std::string route_old(const std::string& txt) {
    FILE* f = tmpfile(); fwrite(txt.data(), 1, txt.size(), f); rewind(f);
    char line[256] = {0}; std::string pref; if (fgets(line, sizeof line, f)) pref = old_trim(line); fclose(f);
    return pref.empty() || !strcasecmp(pref.c_str(), "default") ? "DEFAULT" : pref;
}
static std::string route_new(const std::string& txt) {
    std::string pref; if (!rs64_audio_pref_from_text(txt, &pref)) return "BUILTIN";
    return !strcasecmp(pref.c_str(), "default") ? "DEFAULT" : pref;
}
int main() {
    struct C { const char* name; std::string txt; const char* want; };
    const std::string full = "MacBook Pro Speakers\n";
    std::vector<C> cs = {
        {"empty", "", "BUILTIN"}, {"newline", "\n", "BUILTIN"}, {"spaces", "   \r\n", "BUILTIN"},
        {"nulfill", std::string(full.size(), '\0'), "BUILTIN"}, {"junk", "\x01\x02garbage\n", "BUILTIN"},
        {"full", full, "MacBook Pro Speakers"}, {"default", "default\n", "DEFAULT"}, {"crlf", "External Headphones\r\n", "External Headphones"},
        {"bom", "\xEF\xBB\xBFMacBook Pro Speakers\n", "MacBook Pro Speakers"}, {"nonl", "MacBook Pro Speakers", "MacBook Pro Speakers"},
    };
    int old_bad = 0, new_bad = 0;
    for (auto& c : cs) {
        const std::string o = route_old(c.txt), n = route_new(c.txt);
        old_bad += o != c.want; new_bad += n != c.want;
        printf("audio %-8s want=%-22s old=%-22s new=%s\n", c.name, c.want, o.c_str(), n.c_str());
    }
    // controls.json: remap A -> key:P (positive control: the full file must load the remap).
    rs64_bind_table t = rs64_bind_defaults();
    for (auto& e : t.buttons) if (e.n64_mask == 0x8000 && e.src.kind == RS64_SRC_KEY) e.src.id = SDL_SCANCODE_P;
    const std::string js = rs64_bind_to_json(t);
    rs64_bind_table got; std::string err;
    const bool full_ok = rs64_bind_parse_json(js, &got, &err) && rs64_bind_to_json(got) == js && js != rs64_bind_to_json(rs64_bind_defaults());
    const std::string defs = rs64_bind_to_json(rs64_bind_defaults());
    int prefixes = 0, prefix_trusted_wrong = 0;
    std::vector<std::string> bad = {std::string(js.size(), '\0'), ""};
    for (size_t k = 0; k < js.size(); ++k) bad.push_back(js.substr(0, k));
    for (auto& b : bad) {
        ++prefixes; rs64_bind_table r; std::string e;
        const bool ok = rs64_bind_parse_json(b, &r, &e);
        const std::string rj = rs64_bind_to_json(r);
        // A partial file must either be rejected with defaults in *out, or (whitespace-tail prefix) equal the full file.
        if (ok ? rj != js : rj != defs) ++prefix_trusted_wrong;
    }
    printf("AUDIO old_bad=%d new_bad=%d cases=%zu\n", old_bad, new_bad, cs.size());
    printf("CONTROLS full_remap_loaded=%d partial_files=%d trusted_wrong=%d\n", full_ok, prefixes, prefix_trusted_wrong);
    return 0;
}
