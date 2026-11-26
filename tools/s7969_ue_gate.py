#!/usr/bin/env python3
"""s7969 class UE (the volume holding the game goes away mid-run: USB stick pulled, force eject). Measured by
tools/s7969_ue_e2e.zsh (256 MB APFS + ExFAT images, `hdiutil detach -force` at 10 s, save tick plant 1.5 s):
- exe on the vanished volume: every thread faults at one code address (KERN_MEMORY_ERROR, code pages cannot be paged in,
  the SIGBUS handler is paged-out code too) -> livelock at ~660% CPU, no crash report, quit never completes. mlock of the
  segments does not help (__TEXT -> EPERM). Fix (src/main/rs64_ue.h): an exe on a volume other than the system/home
  volume copies itself to ~/Library/Caches/RogueSquadron64Recomp and execve()s the copy (same pid), passing the original
  folder in ROGUESQ_S7969_EXE_DIR for the data root. Mutant ROGUESQ_S7969_RELOC=0 must still livelock.
- saves/ on the vanished volume: every later save printed the full "Failed to write" report (14 reports / 20 s). Fix
  (pi.cpp update_save_file): one report + one [s7969-ue] line per failure streak, a "back" line when a save succeeds
  again; quit asks Retry / Quit without saving when the file is behind (main.cpp rs64_s7969_quit_check). Mutant
  ROGUESQ_S7969_UE=0 must report every failure.
Checks: STATIC source shape (each fix present and env-gated), E2E summary (12 arms PASS incl. both mutants and the
return/retry recovery arms), and a CONTROL that the E2E scorer rejects a summary with one arm planted FAIL."""
import os, re, subprocess, sys
root = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip()
ok_all = True
def say(tag, body, ok):
    global ok_all
    ok_all &= ok; print(f"{tag} {body} {'PASS' if ok else 'FAIL'}")
rd = lambda p: open(os.path.join(root, p)).read()
pi, ue, mn = rd("lib/N64ModernRuntime/librecomp/src/pi.cpp"), rd("src/main/rs64_ue.h"), rd("src/main/main.cpp")
hp = rd("lib/N64ModernRuntime/ultramodern/include/ultramodern/ultramodern.hpp")
st = {
    "streak": 'getenv("ROGUESQ_S7969_UE")' in pi and "ue_off || ue_streak == 0" in pi and "save folder back after" in pi,
    "behind": "bool ultramodern::save_file_behind()" in pi and "bool save_file_behind();" in hp,
    "reloc": 'getenv("ROGUESQ_S7969_RELOC")' in ue and "execve(dst.c_str(), argv" in ue and 'setenv("ROGUESQ_S7969_EXE_DIR"' in ue
             and "_dyld_get_image_name(i)" in ue,
    "main_calls": "rs64_s7969_relocate(argv);" in mn and "rs64_s7969_quit_check();" in mn and 'getenv("ROGUESQ_S7969_EXE_DIR")' in mn,
    "plant_off_default": 'getenv("ROGUESQ_S7969_SAVE_TICK_MS")' in pi,
}
# relocate must run before any thread starts: first statement of main()
m = re.search(r"int main\(int argc, char\* argv\[\]\) \{\n#ifdef __APPLE__\n    rs64_s7969_relocate\(argv\);", mn)
st["reloc_first"] = m is not None
say("STATIC", " ".join(f"{k}={int(v)}" for k, v in st.items()), all(st.values()))
NEED = ["APFS_whole_keep", "APFS_whole_pull", "APFS_data_keep", "APFS_data_pull", "ExFAT_whole_keep", "ExFAT_whole_pull",
        "ExFAT_whole_mutant", "ExFAT_data_keep", "ExFAT_data_pull", "ExFAT_data_mutant", "ExFAT_data_return", "ExFAT_data_retry"]
def score(s):
    got = [a for a in NEED if re.search(rf"^new {a} PASS$", s, re.M)]
    wm = re.search(r"^new ExFAT_whole_mutant: .*hup_exit_ms=hung", s, re.M) is not None
    wp = len(re.findall(r"^new \w+_whole_pull: alive=alive .*hup_exit_ms=\d+ .*ue_gone=1 .*wired=1", s, re.M))
    dm = re.search(r"^new ExFAT_data_mutant: .*failed_lines_after=(\d+)", s, re.M)
    dp = [int(x) for x in re.findall(r"^new \w+_data_pull: .*failed_lines_after=(\d+)", s, re.M)]
    ok = (len(got) == len(NEED) and wm and wp == 2 and dm is not None and int(dm.group(1)) >= 6 and len(dp) == 2
          and max(dp) <= 2 and "new VERDICT PASS" in s and "new new_crash_reports=0" in s)
    return ok, f"arms={len(got)}/{len(NEED)} whole_mutant_hung={int(wm)} whole_pull_quit_ok={wp}/2 " \
               f"data_mutant_failed_lines={dm.group(1) if dm else '-'} data_pull_failed_lines={dp}"
sf = os.path.join(root, "scratch/s7969/new_summary.txt"); s = open(sf).read() if os.path.exists(sf) else ""
ok, body = score(s); say("E2E", body, ok)
planted = re.sub(r"^new ExFAT_data_retry PASS$", "new ExFAT_data_retry FAIL", s, count=1, flags=re.M)
pok, _ = score(planted); say("CONTROL", f"planted_fail_rejected={int(not pok)} (needs a real summary: {int(bool(s))})", bool(s) and not pok)
print("VERDICT", "CLOSED" if ok_all else "OPEN"); sys.exit(0 if ok_all else 1)
