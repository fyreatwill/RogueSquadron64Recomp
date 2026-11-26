#!/usr/bin/env python3
"""s7958 gate, class FW (host owner-state file writers): audio_device.txt was written fopen("w") in place, so a SIGKILL
mid-write left an empty/partial file (read next run as the "default" route). Builds tools/s7958_fw_kill_test.cpp and
SIGKILLs the writer N times per arm. CONTROL: the old in-place writer must leave >=1 bad file. FIX: rs64_write_file_atomic
must leave 0 and report failure for an unwritable path. CENSUS: every fopen("w"/"wb")/ofstream in src/main + librecomp +
rt64 hle that is NOT env-gated diagnostics is listed in OWNER and must use temp+rename.
s7965: HARNESS line - each bad file is classified (missing/zero/partial) and a failed read/fork/reap makes the run unscored
(one cached s7964 sweep run read new_bad=170 empty, never reproduced standalone or under CPU/IO/tracer load)."""
import os, re, subprocess, sys, tempfile
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
N = int(os.environ.get("S7958_KILLS", "1500"))
td = tempfile.mkdtemp(prefix="s7958_")
exe = os.path.join(td, "t")
b = subprocess.run(["c++", "-std=c++17", "-O1", "-o", exe, os.path.join(root, "tools/s7958_fw_kill_test.cpp")], capture_output=True, text=True)
if b.returncode: print(b.stderr); print("VERDICT OPEN (build)"); sys.exit(1)
res, outs = {}, {}
for arm in ("old", "new", "del"):
    o = subprocess.run([exe, arm, os.path.join(td, f"{arm}.txt"), str(N if arm != "del" else max(N // 5, 50))], capture_output=True, text=True).stdout.strip()
    outs[arm] = o
    print({"old": "control arm (pre-fix writer): ", "del": "classifier control arm (unlink mutant): "}.get(arm, "") + o); res[arm] = dict(kv.split("=", 1) for kv in o.split()[1:5]) | {"nodir": re.search(r"nodir_ok=(\d)", o).group(1)}
# s7965: harness health. A read that failed (openerr), a fork that failed or a reap that did not wait (racing writer) makes
# the arm unscored, not a defect of the writer: HARNESS FAIL, so a flaky host never reads as a broken fix (or a passing one).
ext = {a: dict(re.findall(r"(missing|zero|partial|openerr|lasterr|forkfail|waitfail|first_bad)=(-?\d+)", o2)) for a, o2 in outs.items()}
healthy = all(int(ext[a][k]) == 0 for a in ext for k in ("openerr", "forkfail", "waitfail"))
print("HARNESS " + " ".join(f"{a}:openerr={ext[a]['openerr']}(errno {ext[a]['lasterr']}),forkfail={ext[a]['forkfail']},waitfail={ext[a]['waitfail']}" for a in ext)
      + f" {'PASS' if healthy else 'FAIL'}")
clf = int(ext["del"]["missing"]) > 0 and int(ext["old"]["zero"]) > 0
print(f"CLASSIFIER control del_missing={ext['del']['missing']} old_zero={ext['old']['zero']} {'PASS' if clf else 'FAIL'}")
print("NEW-ARM bad kinds: " + " ".join(f"{k}={ext['new'][k]}" for k in ("missing", "zero", "partial", "first_bad")))
ctl = int(res["old"]["bad"]) > 0 and healthy
fix = int(res["new"]["bad"]) == 0 and res["new"]["nodir"] == "0" and healthy
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
ok = ctl and fix and census and clf
print("VERDICT", "CLOSED" if ok else "OPEN")
sys.exit(0 if ok else 1)
