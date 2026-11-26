// s7959 class RD (host readers of owner-state files): a reader must treat an empty or corrupt file as ABSENT, not as a
// value. audio_device.txt is always written as "<name>\n" (F9, rs64_write_file_atomic); before s7958 a kill mid-write
// left it empty, and the reader turned "" into the "default" route (system output) instead of the built-in default.
// rs64_audio_pref_from_text: first line of the file text, UTF-8 BOM dropped, trimmed. Returns false (= treat as no file)
// when that is empty or holds a control byte (NUL fill from a sparse/zeroed file, binary junk).
#pragma once
#include <string>

inline bool rs64_audio_pref_from_text(const std::string& raw, std::string* out) {
    std::string v = raw;
    if (v.size() >= 3 && (unsigned char)v[0] == 0xEF && (unsigned char)v[1] == 0xBB && (unsigned char)v[2] == 0xBF) v.erase(0, 3);
    const size_t nl = v.find_first_of("\r\n");
    if (nl != std::string::npos) v.resize(nl);
    while (!v.empty() && (v.back() == ' ' || v.back() == '\t')) v.pop_back();
    size_t i = 0;
    while (i < v.size() && (v[i] == ' ' || v[i] == '\t')) ++i;
    v = v.substr(i);
    if (v.empty()) return false;
    for (unsigned char c : v) if (c < 0x20 || c == 0x7F) return false;
    *out = v;
    return true;
}
