#!/usr/bin/env python3
"""s7960 gate, class DR (host data-root split). Before s7960 saves/, the stored ROM, mods/, mod_config/ and mods.json were
resolved against the LAUNCH folder while settings.txt (exe path), controls.json and audio_device.txt (SDL_GetBasePath) were
next to the executable, so a launch from another folder (Finder -> $HOME, repo root) applied the settings but found no ROM or
save and littered mods/ + mod_config/ there. CONTROL: the old always-cwd rule must misroute >=1 case. FIX:
rs64_pick_data_root (src/main/rs64_data_root.h) routes every case. CENSUS: main.cpp registers the picked root (not the raw
cwd) as the config path, and the ROM import loop uses that root; every other owner-state reader is exe-relative.
E2E evidence (not re-run here): scratch/s7960/e2e.zsh, old binary from an empty folder romfail=1 + litter, new boots."""
import os, re, subprocess, sys, tempfile
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
exe = os.path.join(tempfile.mkdtemp(prefix="s7960_"), "t")
b = subprocess.run(["c++", "-std=c++17", "-I", "src/main", "tools/s7960_dr_test.cpp", "-o", exe], cwd=root, capture_output=True, text=True)
if b.returncode: print(b.stderr[-2000:]); print("VERDICT OPEN (build)"); sys.exit(1)
o = subprocess.run([exe], capture_output=True, text=True).stdout
a = re.search(r"DR old_bad=(\d+) new_bad=(\d+) cases=(\d+)", o)
if not a: print(o); print("VERDICT OPEN (output)"); sys.exit(1)
src = open(os.path.join(root, "src/main/main.cpp")).read()
m = re.search(r"rs64_pick_data_root\(rs_cwd,.*?\n\s*rs_cwd = root;\s*(?:rs64_data_root_str\(\) = root\.string\(\);[^\n]*\s*)?\}\s*recomp::register_config_path\(rs_cwd\);", src, re.S)
rom = re.search(r"std::filesystem::path p = rs_cwd / name;", src)
regs = len(re.findall(r"register_config_path\(", src))
st = open(os.path.join(root, "src/main/rs64_settings.cpp")).read()
# s7972: controls.json / audio_device.txt now try the data root first (SDL_GetBasePath only as a fallback before main sets it)
others = "_NSGetExecutablePath" in st and src.count('SDL_GetBasePath(); std::string path = base ? std::string(base) + "controls.json"') == 1 \
    and re.search(r'audio_route_file_path\(\) \{\s*if \(!rs64_owner_file_old_rule\(\) && !rs64_data_root_str\(\)\.empty\(\)\)[^\n]*\n\s*char\* base = SDL_GetBasePath\(\);', src) is not None
census = bool(m) and bool(rom) and regs == 1 and others
ctl = int(a[1]) > 0; fix = int(a[2]) == 0 and int(a[3]) >= 7
print(f"CONTROL old_bad={a[1]} {'PASS' if ctl else 'FAIL'}")
print(f"FIX new_bad={a[2]} cases={a[3]} {'PASS' if fix else 'FAIL'}")
print(f"CENSUS picked_root_registered={bool(m)} rom_import_uses_root={bool(rom)} register_calls={regs} exe_relative_readers={others} {'PASS' if census else 'FAIL'}")
ok = ctl and fix and census
print("VERDICT", "CLOSED" if ok else "OPEN"); sys.exit(0 if ok else 1)
