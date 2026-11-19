// s7619 G6b step 2: controls.json overrides for the binding table (rs64_bindings.h).
// Format (version 1; every key optional, missing file = built-in defaults):
//   {"version":1,
//    "buttons":{"A":["pad:a","key:Z"], "Z":["axis+:lefttrigger:16000","key:C"], "CL":[] , ...},
//    "stick":{"pad_x":"leftx","pad_y":"lefty","invert_y":true,
//             "up":["key:W"],"down":["key:S"],"left":["key:A"],"right":["key:D"]}}
// N64 button names: A B Z START DU DD DL DR L R CU CD CL CR (case-insensitive).
// Sources: "pad:<SDL controller button name>", "axis+:<axis>[:threshold]", "axis-:<axis>[:threshold]" (default 16000),
//          "key:<SDL scancode name>". A button listed in the file REPLACES that button's default list (an empty list
//          unbinds it); unlisted buttons keep their defaults. Any error -> the whole file is rejected, defaults kept.
// Uses SDL's name<->enum functions (link SDL2) and nlohmann json (lib/rt64/src/contrib/json/json.hpp).
#pragma once
#include <string>
#include <cstring>
#include <cstdlib>
#include <strings.h>
#include "json/json.hpp"
#include "rs64_bindings.h"
#if __has_include(<SDL2/SDL_keyboard.h>)
#include <SDL2/SDL_keyboard.h>
#else
#include <SDL_keyboard.h>
#endif

struct rs64_n64_name { const char* name; uint16_t mask; };
static const rs64_n64_name rs64_n64_names[] = {
    {"A", RS64_N64_A}, {"B", RS64_N64_B}, {"Z", RS64_N64_Z}, {"START", RS64_N64_START},
    {"DU", RS64_N64_DU}, {"DD", RS64_N64_DD}, {"DL", RS64_N64_DL}, {"DR", RS64_N64_DR},
    {"L", RS64_N64_L}, {"R", RS64_N64_R},
    {"CU", RS64_N64_CU}, {"CD", RS64_N64_CD}, {"CL", RS64_N64_CL}, {"CR", RS64_N64_CR},
};

inline bool rs64_bind_parse_source(const std::string& s, rs64_bind_source* out, std::string* err) {
    const size_t c = s.find(':');
    if (c == std::string::npos) { *err = "source '" + s + "' has no ':'"; return false; }
    const std::string kind = s.substr(0, c), rest = s.substr(c + 1);
    if (kind == "pad") {
        const SDL_GameControllerButton b = SDL_GameControllerGetButtonFromString(rest.c_str());
        if (b == SDL_CONTROLLER_BUTTON_INVALID) { *err = "unknown pad button '" + rest + "'"; return false; }
        *out = {RS64_SRC_PAD_BUTTON, (int)b, 0}; return true;
    }
    if (kind == "axis+" || kind == "axis-") {
        std::string name = rest; int thr = 16000;
        const size_t c2 = rest.find(':');
        if (c2 != std::string::npos) {
            name = rest.substr(0, c2);
            const std::string t = rest.substr(c2 + 1);
            char* end = nullptr; const long v = std::strtol(t.c_str(), &end, 10);
            if (t.empty() || *end || v < 0 || v > 32766) { *err = "bad threshold '" + t + "'"; return false; }
            thr = (int)v;
        }
        const SDL_GameControllerAxis a = SDL_GameControllerGetAxisFromString(name.c_str());
        if (a == SDL_CONTROLLER_AXIS_INVALID) { *err = "unknown axis '" + name + "'"; return false; }
        *out = {kind == "axis+" ? RS64_SRC_AXIS_POS : RS64_SRC_AXIS_NEG, (int)a, thr}; return true;
    }
    if (kind == "key") {
        const SDL_Scancode k = SDL_GetScancodeFromName(rest.c_str());
        if (k == SDL_SCANCODE_UNKNOWN) { *err = "unknown key '" + rest + "'"; return false; }
        *out = {RS64_SRC_KEY, (int)k, 0}; return true;
    }
    *err = "unknown source kind '" + kind + "'"; return false;
}

inline std::string rs64_bind_source_name(const rs64_bind_source& s) {
    switch (s.kind) {
    case RS64_SRC_PAD_BUTTON: { const char* n = SDL_GameControllerGetStringForButton((SDL_GameControllerButton)s.id); return std::string("pad:") + (n ? n : "?"); }
    case RS64_SRC_AXIS_POS:
    case RS64_SRC_AXIS_NEG: { const char* n = SDL_GameControllerGetStringForAxis((SDL_GameControllerAxis)s.id);
        return std::string(s.kind == RS64_SRC_AXIS_POS ? "axis+:" : "axis-:") + (n ? n : "?") + ":" + std::to_string(s.threshold); }
    case RS64_SRC_KEY: return std::string("key:") + SDL_GetScancodeName((SDL_Scancode)s.id);
    }
    return "?";
}

// Parse text into *out (starting from the built-in defaults). On any error returns false, *out = defaults, *err set.
inline bool rs64_bind_parse_json(const std::string& text, rs64_bind_table* out, std::string* err) {
    using nlohmann::json;
    *out = rs64_bind_defaults();
    rs64_bind_table t = rs64_bind_defaults();
    const json j = json::parse(text, nullptr, false);
    if (j.is_discarded()) { *err = "not valid JSON"; return false; }
    if (!j.is_object()) { *err = "not a JSON object"; return false; }
    if (j.contains("version") && !(j["version"].is_number_integer() && j["version"].get<int>() == 1)) { *err = "version must be 1"; return false; }
    for (auto it = j.begin(); it != j.end(); ++it)
        if (it.key() != "version" && it.key() != "buttons" && it.key() != "stick") { *err = "unknown key '" + it.key() + "'"; return false; }
    if (j.contains("buttons")) {
        const json& b = j["buttons"];
        if (!b.is_object()) { *err = "'buttons' must be an object"; return false; }
        for (auto it = b.begin(); it != b.end(); ++it) {
            uint16_t mask = 0;
            for (const auto& n : rs64_n64_names) if (!strcasecmp(n.name, it.key().c_str())) mask = n.mask;
            if (!mask) { *err = "unknown N64 button '" + it.key() + "'"; return false; }
            if (!it->is_array()) { *err = "buttons." + it.key() + " must be a list"; return false; }
            std::vector<rs64_button_bind> keep;
            for (const auto& e : t.buttons) if (e.n64_mask != mask) keep.push_back(e);
            for (const auto& s : *it) {
                if (!s.is_string()) { *err = "buttons." + it.key() + " entries must be strings"; return false; }
                rs64_bind_source src;
                if (!rs64_bind_parse_source(s.get<std::string>(), &src, err)) { *err = "buttons." + it.key() + ": " + *err; return false; }
                keep.push_back({mask, src});
            }
            t.buttons = keep;
        }
    }
    if (j.contains("stick")) {
        const json& s = j["stick"];
        if (!s.is_object()) { *err = "'stick' must be an object"; return false; }
        for (auto it = s.begin(); it != s.end(); ++it) {
            const std::string& k = it.key();
            if (k == "pad_x" || k == "pad_y") {
                if (!it->is_string()) { *err = "stick." + k + " must be a string"; return false; }
                const SDL_GameControllerAxis a = SDL_GameControllerGetAxisFromString(it->get<std::string>().c_str());
                if (a == SDL_CONTROLLER_AXIS_INVALID) { *err = "stick." + k + ": unknown axis"; return false; }
                (k == "pad_x" ? t.stick_axis_x : t.stick_axis_y) = (int)a;
            } else if (k == "invert_y") {
                if (!it->is_boolean()) { *err = "stick.invert_y must be true/false"; return false; }
                t.stick_invert_y = it->get<bool>();
            } else if (k == "up" || k == "down" || k == "left" || k == "right") {
                if (!it->is_array()) { *err = "stick." + k + " must be a list"; return false; }
                std::vector<int> v;
                for (const auto& e : *it) {
                    rs64_bind_source src;
                    if (!e.is_string() || !rs64_bind_parse_source(e.get<std::string>(), &src, err) || src.kind != RS64_SRC_KEY) {
                        *err = "stick." + k + ": entries must be key:<name>"; return false;
                    }
                    v.push_back(src.id);
                }
                (k == "up" ? t.key_up : k == "down" ? t.key_down : k == "left" ? t.key_left : t.key_right) = v;
            } else { *err = "unknown stick key '" + k + "'"; return false; }
        }
    }
    *out = t;
    return true;
}

// Full table -> JSON text (every button listed), for the F6 panel's save and for round-trip tests.
inline std::string rs64_bind_to_json(const rs64_bind_table& t) {
    using nlohmann::ordered_json;
    ordered_json j; j["version"] = 1;
    ordered_json b = ordered_json::object();
    for (const auto& n : rs64_n64_names) {
        ordered_json l = ordered_json::array();
        for (const auto& e : t.buttons) if (e.n64_mask == n.mask) l.push_back(rs64_bind_source_name(e.src));
        b[n.name] = l;
    }
    j["buttons"] = b;
    ordered_json s;
    const char* ax = SDL_GameControllerGetStringForAxis((SDL_GameControllerAxis)t.stick_axis_x);
    const char* ay = SDL_GameControllerGetStringForAxis((SDL_GameControllerAxis)t.stick_axis_y);
    s["pad_x"] = ax ? ax : "leftx"; s["pad_y"] = ay ? ay : "lefty"; s["invert_y"] = t.stick_invert_y;
    auto keys = [](const std::vector<int>& v) { ordered_json l = ordered_json::array();
        for (int k : v) l.push_back(std::string("key:") + SDL_GetScancodeName((SDL_Scancode)k)); return l; };
    s["up"] = keys(t.key_up); s["down"] = keys(t.key_down); s["left"] = keys(t.key_left); s["right"] = keys(t.key_right);
    j["stick"] = s;
    return j.dump(2) + "\n";
}
