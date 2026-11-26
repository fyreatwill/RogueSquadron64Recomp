#!/usr/bin/env python3
"""s7967 class CS (game folder inside iCloud Drive / a synced folder). Measured s7967 with tools/s7967_cs/harness.cpp on
real `brctl evict`ed files: online, a dataless save (512 B) or ROM-sized file (16 MB) reads in full through
open_input_file_with_backup in ~1 s (payload ok, no errno), materialised 0 ms; 20 save cycles over an evicted save 0 fails,
no temp left behind. The offline case (placeholder cannot be downloaded) is NOT measured on hardware (needs the network
off); it is simulated in read_save_file by ROGUESQ_S7967_SIM_OFFLINE=1. e2e tools/s7967_cs_e2e.zsh: with the guard OFF
(ROGUESQ_S7967_CS=0) the game rewrote the cloud save from a zeroed buffer within 25 s (the hazard); with the guard on the
session sets ROGUESQ_NO_SAVE_WRITE=1 and the cloud save stays byte-identical.
Checks: harness builds + reads a local control file; STATIC (placeholder probe before the read, sim after both read
branches, no-save flip in the unreadable branch, guard-off switch); STATIC_MUTANT (the same check on pi.cpp with the
setenv removed must fail); E2E summary scratch/s7967/fix_summary.txt 5/5 arms."""
import os, re, subprocess, tempfile, shutil
root = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip()
L = os.path.join(root, "lib/N64ModernRuntime/librecomp")
ok_all = True
def say(tag, body, ok):
    global ok_all
    ok_all &= ok; print(f"{tag} {body} {'PASS' if ok else 'FAIL'}")
t = tempfile.mkdtemp(prefix="s7967g")
try:
    h = f"{t}/h"
    subprocess.check_call(["clang++", "-std=c++20", "-O1", f"-I{L}/include/librecomp", f'-DFILES_CPP="{L}/src/files.cpp"',
                           os.path.join(root, "tools/s7967_cs/harness.cpp"), "-o", h])
    w = subprocess.run([h, "write", f"{t}/s.bin", "512", "aa", "3"], capture_output=True, text=True).stdout.strip()
    r = subprocess.run([h, "read", f"{t}/s.bin", "512", "aa"], capture_output=True, text=True).stdout.strip()
    say("HARNESS", f"[{w}] [{r}]", "fails=0" in w and "before=local" in r and "payload=ok" in r)
finally:
    shutil.rmtree(t, ignore_errors=True)
def static(pi):
    rd = pi[pi.find("void read_save_file()"):pi.find("void ultramodern::init_saving")]
    probe = rd.find("is_cloud_placeholder(save_file_path)"); opn = rd.find("open_input_file_with_backup(save_file_path")
    sim = rd.find("ROGUESQ_S7967_SIM_OFFLINE"); els = rd.find("// Otherwise clear the save file to all zeroes.")
    flip = rd.find('setenv("ROGUESQ_NO_SAVE_WRITE", "1", 1)')
    return 0 <= probe < opn < els < sim < flip and 'getenv("ROGUESQ_S7967_CS")' in rd and "SF_DATALESS" in open(os.path.join(L, "src/files.cpp")).read()
pi = open(os.path.join(L, "src/pi.cpp")).read()
say("STATIC", f"probe<open<else<sim<noSaveFlip={int(static(pi))}", static(pi))
mut = pi.replace('setenv("ROGUESQ_NO_SAVE_WRITE", "1", 1);', "")
say("STATIC_MUTANT", f"no_setenv_caught={int(not static(mut))}", not static(mut))
sf = os.path.join(root, "scratch/s7967/fix_summary.txt"); s = open(sf).read() if os.path.exists(sf) else ""
arms = {a: bool(re.search(rf"^fix {a} PASS", s, re.M)) for a in ("online", "offline", "mutant", "nosave", "local")}
haz = bool(re.search(r"^fix mutant PASS.*save=REWRITTEN", s, re.M)) and bool(re.search(r"^fix offline PASS.*save=same", s, re.M))
say("E2E", " ".join(f"{a}={int(v)}" for a, v in arms.items()) + f" hazard_shown={int(haz)}", all(arms.values()) and haz and "VERDICT PASS" in s)
print("VERDICT", "CLOSED" if ok_all else "OPEN"); raise SystemExit(0 if ok_all else 1)
