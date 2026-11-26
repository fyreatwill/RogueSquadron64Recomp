// ROGUESQ s7962 class PS (owner folder paths). The two host shell commands (crash-handler `nm -n '<exe>'`, stall
// `sample ... -file '<dir>/...'`) wrapped a path in bare single quotes, so a folder name with an apostrophe
// ("William's Games") ended the quote early: nm got a wrong path and the crash symbol table loaded 0 symbols
// (measured s7962: copied exe under .../William's Games/... -> "[symtab] loaded 0"; plain dir -> 29057).
// Spaces, non-ASCII and a 307-char path were already fine. Quote for POSIX sh: ' -> '\''.
#pragma once
#include <string>

inline std::string rs64_shell_quote(const std::string& s) {
    std::string q = "'";
    for (char c : s) { if (c == '\'') q += "'\\''"; else q += c; }
    q += "'";
    return q;
}
