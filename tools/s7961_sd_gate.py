#!/usr/bin/env python3
"""s7961 class SD (settings-dir split, residue of s7960 DR). The default settings.txt was read from realpath(exe)'s folder
while saves/ROM/mods follow rs64_pick_data_root (launch folder with game data, else exe folder AS INVOKED). A symlinked
private game dir therefore kept its own save but applied build/settings.txt (e2e tools/s7961_sd_e2e.zsh: old symlink_pg
file=build/settings.txt, planted pg/settings.txt ignored; new reads pg/settings.txt, dir=cwd-data).
CONTROL: the pre-fix source (commit a6af9af8b) builds the default from exe_path() (realpath) -> split.
FIX: the current source builds it from settings_default_dir() -> rs64_pick_data_root with a lexically_normal exe dir.
MUTANT: re-planting the old default line in a copy of the current source must be caught."""
import os, re, subprocess, sys
root = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip()
P = "src/main/rs64_settings.cpp"
def bad(src):
    """1 when the default settings.txt path does not follow the data-root rule."""
    d = re.search(r"else if \(!files_off\)\s*(\{[^\n]*\}|[^\n]*;)", src)
    if not d: return 1
    line = d[1]
    if "exe.rfind('/')" in line or "exe.substr" in line: return 1
    if "settings_default_dir(" not in line: return 1
    f = re.search(r"std::string settings_default_dir\(const char\*\* why\) \{(.*?)\n\}", src, re.S)
    if not f: return 1
    body = f[1]
    return 0 if ("rs64_pick_data_root(" in body and "lexically_normal()" in body and "realpath" not in body) else 1
old = subprocess.check_output(["git", "show", f"a6af9af8b:{P}"], cwd=root, text=True)
new = open(os.path.join(root, P)).read()
mut = re.sub(r"else if \(!files_off\) file = settings_default_dir\(&dir_why\) \+ \"/settings.txt\";",
             "else if (!files_off) { const size_t sl = exe.rfind('/'); file = exe.substr(0, sl) + \"/settings.txt\"; }", new)
ob, nb, mb = bad(old), bad(new), bad(mut)
inc = '#include "rs64_data_root.h"' in new and "dir=%s" in new
print(f"CONTROL old_bad={ob} {'PASS' if ob == 1 else 'FAIL'}")
print(f"FIX new_bad={nb} {'PASS' if nb == 0 else 'FAIL'}")
print(f"MUTANT replanted_bad={mb} changed={mut != new} {'PASS' if mb == 1 and mut != new else 'FAIL'}")
print(f"CENSUS shared_rule_header={inc} {'PASS' if inc else 'FAIL'}")
ok = ob == 1 and nb == 0 and mb == 1 and mut != new and inc
print("VERDICT", "CLOSED" if ok else "OPEN"); sys.exit(0 if ok else 1)
