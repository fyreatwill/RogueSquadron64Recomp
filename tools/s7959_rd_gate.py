#!/usr/bin/env python3
"""s7959 gate, class RD (host READERS of owner-state files given an empty/short/corrupt file). Builds
tools/s7959_rd_test.cpp against the real reader headers. CONTROL: the pre-s7959 audio_device.txt reader (fgets+trim,
inlined in the harness) must misroute >=1 planted file (empty -> system "default" route). FIX: rs64_audio_pref_from_text
must route all 10 cases as wanted (empty/NUL/junk = absent -> built-in default). CONTROLS: a remapped controls.json must
load (positive control) and every byte prefix / NUL fill / empty must be rejected to defaults (0 trusted wrong).
CENSUS: main.cpp audio_route_load_pref goes through rs64_audio_pref_from_text; pi.cpp keeps the s7429 short-file .bak
fallback. A full-length zero-filled save is erased EEPROM: the game's own checksum owns it, not a host reader."""
import os, re, subprocess, sys, tempfile
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
exe = os.path.join(tempfile.mkdtemp(prefix="s7959_"), "t")
b = subprocess.run(["c++", "-std=c++17", "-I", "src/main", "-I", "lib/rt64/src/contrib", "-I", "/opt/homebrew/include",
                    "tools/s7959_rd_test.cpp", "-L/opt/homebrew/lib", "-lSDL2", "-o", exe], cwd=root, capture_output=True, text=True)
if b.returncode: print(b.stderr[-2000:]); print("VERDICT OPEN (build)"); sys.exit(1)
o = subprocess.run([exe], capture_output=True, text=True).stdout
a = re.search(r"AUDIO old_bad=(\d+) new_bad=(\d+) cases=(\d+)", o); c = re.search(r"CONTROLS full_remap_loaded=(\d) partial_files=(\d+) trusted_wrong=(\d+)", o)
if not (a and c): print(o); print("VERDICT OPEN (output)"); sys.exit(1)
ctl = int(a[1]) > 0; fix = int(a[2]) == 0 and int(a[3]) >= 10
ctr = c[1] == "1" and int(c[2]) > 100 and c[3] == "0"
src = open(os.path.join(root, "src/main/main.cpp")).read()
m = re.search(r"static void audio_route_load_pref\(\)\s*\{(.*?)\n\}", src, re.S)
pi = open(os.path.join(root, "lib/N64ModernRuntime/librecomp/src/pi.cpp")).read()
census = bool(m) and "rs64_audio_pref_from_text(" in m.group(1) and "fgets(" not in m.group(1) and "loaded the complete .bak instead" in pi
print(f"CONTROL old_bad={a[1]} PASS" if ctl else f"CONTROL old_bad={a[1]} FAIL")
print(f"FIX new_bad={a[2]} cases={a[3]} {'PASS' if fix else 'FAIL'}")
print(f"CONTROLS remap_loaded={c[1]} partial={c[2]} trusted_wrong={c[3]} {'PASS' if ctr else 'FAIL'}")
print(f"CENSUS audio_reader_guarded={bool(census)} {'PASS' if census else 'FAIL'}")
ok = ctl and fix and ctr and census
print("VERDICT", "CLOSED" if ok else "OPEN"); sys.exit(0 if ok else 1)
