#!/usr/bin/env python3
"""s7958 gate, class FW (host owner-state file writers): audio_device.txt was written fopen("w") in place, so a SIGKILL
mid-write left an empty/partial file (read next run as the "default" route). Builds tools/s7958_fw_kill_test.cpp and
SIGKILLs the writer N times per arm. CONTROL: the old in-place writer must leave >=1 bad file. FIX: rs64_write_file_atomic
must leave 0 and report failure for an unwritable path. CENSUS: every fopen("w"/"wb")/ofstream in src/main + librecomp +
rt64 hle that is NOT env-gated diagnostics is listed in OWNER and must use temp+rename."""
import os, re, subprocess, sys, tempfile
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
N = int(os.environ.get("S7958_KILLS", "1500"))
td = tempfile.mkdtemp(prefix="s7958_")
exe = os.path.join(td, "t")
b = subprocess.run(["c++", "-std=c++17", "-O1", "-o", exe, os.path.join(root, "tools/s7958_fw_kill_test.cpp")], capture_output=True, text=True)
if b.returncode: print(b.stderr); print("VERDICT OPEN (build)"); sys.exit(1)
res = {}
for arm in ("old", "new"):
    o = subprocess.run([exe, arm, os.path.join(td, f"{arm}.txt"), str(N)], capture_output=True, text=True).stdout.strip()
    print(("control arm (pre-fix writer): " if arm == "old" else "") + o); res[arm] = dict(kv.split("=", 1) for kv in o.split()[1:5]) | {"nodir": re.search(r"nodir_ok=(\d)", o).group(1)}
ctl = int(res["old"]["bad"]) > 0
fix = int(res["new"]["bad"]) == 0 and res["new"]["nodir"] == "0"
# Census of owner-state writers (s7958 classification; diagnostics are env-gated dumps/logs and excluded by name).
OWNER = {  # site -> how it writes
    "lib/N64ModernRuntime/librecomp/src/pi.cpp": "open_output_file_with_backup + finalize (s7429 temp+fsync+rename)",
    "lib/N64ModernRuntime/librecomp/src/mods.cpp": "open_output_file_with_backup + finalize (s7429)",
    "src/main/main.cpp:rs64_bind_save": "controls.json temp+rename (s7620)",
    "src/main/main.cpp:audio_route_apply_cycle": "audio_device.txt rs64_write_file_atomic (s7958)",
    "lib/rt64/src/hle/rt64_application.cpp:saveConfiguration": "dead: rt64_render_context.cpp sets useConfigurationFile=false",
}
src = open(os.path.join(root, "src/main/main.cpp")).read()
m = re.search(r"static void audio_route_apply_cycle\(\)\s*\{(.*?)\n\}", src, re.S)
inplace = m and re.search(r'fopen\(audio_route_file_path\(\)[^)]*"w', m.group(1))
census = bool(m) and not inplace and "rs64_write_file_atomic(audio_route_file_path()" in m.group(1)
rc = open(os.path.join(root, "src/main/rt64_render_context.cpp")).read()
census = census and "appConfig.useConfigurationFile = false" in rc
print(f"CONTROL old_bad={res['old']['bad']} (empty={res['old']['empty']}) {'PASS' if ctl else 'FAIL'}")
print(f"FIX new_bad={res['new']['bad']} nodir_reports_fail={res['new']['nodir']=='0'} {'PASS' if fix else 'FAIL'}")
print(f"CENSUS owner_writers={len(OWNER)} audio_atomic={bool(census)} {'PASS' if census else 'FAIL'}")
ok = ctl and fix and census
print("VERDICT", "CLOSED" if ok else "OPEN")
sys.exit(0 if ok else 1)
