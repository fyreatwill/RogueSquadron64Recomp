#!/usr/bin/env python3
"""s7972 class NS (data volume full while the game runs: the non-save writers) + the owner-file path split it exposed.
tools/s7972_ns_e2e.zsh runs the game from a 160 MB APFS image (an external volume, so the s7969 relocation re-execs from
~/Library/Caches) in arms ctl (not full) / run (filled to ENOSPC 3 s in, before the F6 panel Save at poll 1200) / boot
(full before launch, ROM only as a candidate) / boot2 (relaunch on the same full image), with phases old (pre-fix exe),
mut (ROGUESQ_S7972_BASEPATH=1) and new.
Finding: controls.json and audio_device.txt resolved via SDL_GetBasePath = the CACHED copy's folder, so a game folder on
an external drive had its controls.json and audio_device.txt ignored (built-in defaults) and F6/F9 saves went to the cache.
Checks: STATIC (both paths consult rs64_data_root_str before SDL_GetBasePath, main records the root, settings.txt honours
ROGUESQ_S7969_EXE_DIR, rs64_bind_save uses rs64_write_file_atomic = temp removed on failure), UNIT (rs64_exe_dir_or and
the atomic writer on an unwritable dir, compiled), E2E (new: ctl+run read both owner files from the game folder, run's
Save fails cleanly with the old controls.json and save intact, 0 temps, 0 crash; old and mut: 0/0 = the bug reproduces),
CONTROL (scorer rejects a planted new summary with ctl_in_game=0)."""
import os, re, subprocess, sys, tempfile
# zst-ok: reads only scratch/s7972/<phase>_summary.txt (raw, small) and source files
root = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip()
ok_all = True
def say(tag, body, ok):
    global ok_all
    ok_all &= ok; print(f"{tag} {body} {'PASS' if ok else 'FAIL'}")
def rd(p):
    try: return open(os.path.join(root, p), encoding="latin-1").read()
    except OSError: return ""
m = rd("src/main/main.cpp"); st = rd("src/main/rs64_settings.cpp")
def body(src, sig):
    i = src.find(sig); return src[i:src.find("\n}", i)] if i >= 0 else ""
bp, ap, bs = body(m, "std::string rs64_bind_path() {"), body(m, "static std::string audio_route_file_path() {"), body(m, "bool rs64_bind_save(std::string* msg) {")
def first(b, a, c): return a in b and c in b and b.index(a) < b.index(c)
chk = {"bind_path": first(bp, "rs64_data_root_str()", "SDL_GetBasePath"),
       "audio_path": first(ap, "rs64_data_root_str()", "SDL_GetBasePath"),
       "root_set": "rs64_data_root_str() = root.string();" in m,
       "settings_exe_dir": "rs64_exe_dir_or(exe_dir)" in st,
       "bind_save_atomic": "rs64_write_file_atomic(path, text" in bs and "fopen(" not in bs}
say("STATIC", " ".join(f"{k}={int(v)}" for k, v in chk.items()), all(chk.values()))
td = tempfile.mkdtemp(prefix="s7972_"); cpp = os.path.join(td, "t.cpp"); exe = os.path.join(td, "t")
open(cpp, "w").write(r'''
#include "rs64_data_root.h"
#include "rs64_atomic_write.h"
#include <cstdio>
#include <sys/stat.h>
int main(int, char** v) {
    unsetenv("ROGUESQ_S7969_EXE_DIR"); unsetenv("ROGUESQ_S7972_BASEPATH");
    int a = rs64_exe_dir_or("/run/dir") == "/run/dir";
    setenv("ROGUESQ_S7969_EXE_DIR", "/game/dir", 1); int b = rs64_exe_dir_or("/run/dir") == "/game/dir";
    setenv("ROGUESQ_S7972_BASEPATH", "1", 1); int c = rs64_exe_dir_or("/run/dir") == "/run/dir" && rs64_owner_file_old_rule();
    unsetenv("ROGUESQ_S7972_BASEPATH");
    std::string d = v[1], f = d + "/controls.json"; FILE* o = fopen(f.c_str(), "w"); fputs("OLD", o); fclose(o);
    chmod(d.c_str(), 0555); std::string e; int w = rs64_write_file_atomic(f, "NEW", &e); chmod(d.c_str(), 0755);
    char buf[8] = {0}; o = fopen(f.c_str(), "r"); fread(buf, 1, 7, o); fclose(o);
    int kept = std::string(buf) == "OLD", ok2 = rs64_write_file_atomic(f, "NEW2", &e);
    printf("env_unset=%d relocated=%d mutant=%d ro_write_fails=%d old_kept=%d write_ok=%d\n", a, b, c, !w, kept, ok2);
    return !(a && b && c && !w && kept && ok2);
}''')
os.makedirs(os.path.join(td, "d"))
b = subprocess.run(["c++", "-std=c++17", "-I", os.path.join(root, "src/main"), "-o", exe, cpp], capture_output=True, text=True)
r = subprocess.run([exe, os.path.join(td, "d")], capture_output=True, text=True) if not b.returncode else None
say("UNIT", (r.stdout.strip() if r else "build failed: " + b.stderr[:200]), bool(r) and r.returncode == 0)
S = "scratch/s7972"
def score(s, phase):
    want = 1 if phase == "new" else 0
    arms = {a: re.search(rf"^{phase} {a}: (.*)$", s, re.M) for a in ("ctl", "run", "boot", "boot2")}
    if not all(arms.values()) or f"{phase} VERDICT PASS" not in s or f"{phase} new_crash_reports=0" not in s: return False, "missing"
    f = {a: dict(re.findall(r"(\w+)=(\S+)", x.group(1))) for a, x in arms.items()}
    ok = all(f[a]["crashlines"] == "0" and f[a]["alive"] == "alive" and f[a]["temps"] == "0" and f[a]["s_size"] == "512" for a in f)
    ok &= all(f[a]["ctl_in_game"] == str(want) and f[a]["audio_in_game"] == str(want) for a in ("ctl", "run"))
    c0, c1 = f["run"]["c_sha"].split("->"); ok &= c0 == c1 and f["run"]["s_sha"].split("->")[0] == f["run"]["s_sha"].split("->")[1]
    if phase == "new": ok &= f["run"]["controls"] == "[SAVE_FAILED]" and f["ctl"]["c_sha"].split("->")[0] != f["ctl"]["c_sha"].split("->")[1]
    return ok, f"ctl_in_game={f['ctl']['ctl_in_game']}/{f['run']['ctl_in_game']} audio_in_game={f['ctl']['audio_in_game']}/{f['run']['audio_in_game']} run_controls={f['run']['controls']}"
res = {}
for ph in ("old", "mut", "new"):
    s = rd(f"{S}/{ph}_summary.txt"); ok, bd = score(s, ph); res[ph] = s
    say("E2E" if ph == "new" else f"REPRO-{ph}", bd, ok)
planted = re.sub(r"^(new ctl: .*?)ctl_in_game=1", r"\1ctl_in_game=0", res["new"], count=1, flags=re.M)
pok, _ = score(planted, "new")
say("CONTROL", f"planted_rejected={int(not pok)} (real summary present: {int(bool(res['new']))})", bool(res["new"]) and not pok)
print("VERDICT", "CLOSED" if ok_all else "OPEN"); sys.exit(0 if ok_all else 1)
