#!/usr/bin/env python3
"""s7964 class RO (unwritable game folder). e2e tools/s7964_ro_e2e.zsh (summaries scratch/s7964/{old,new}_summary.txt).
Measured: the game boots in a chmod a-w folder and on a read-only UDRO disk image (H-fatal refuted; mods/ + mod_config/ were
already reported by s7595), but every game save there fails in librecomp update_save_file with only a generic stderr line per
attempt (H-silent: progress lost unseen when launched from Finder). Fix: src/main/rs64_ro_probe.h rs64_dir_writable() probes
<data root>/saves once at boot; unwritable -> one [s7964-ro] line, plus one modal dialog when saving is on (NO_SAVE_WRITE unset;
ROGUESQ_RO_DIALOG=0 = line only). 80 write sites enumerated: diag fopen sites are all null-checked (if (FILE* f = ...), or a
static FILE* tested before use); F6 controls save reports SAVE FAILED; save path reports via message_box (stderr) -> covered.
UNIT: compiles the header and probes a writable dir, a chmod a-w dir, and a missing saves/ under a writable parent.
MUTANT: a probe that always returns true must fail the UNIT."""
import os, re, subprocess, sys, tempfile
root = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip()
hdr = open(os.path.join(root, "src/main/rs64_ro_probe.h")).read()
main = open(os.path.join(root, "src/main/main.cpp")).read()
TEST = r'''#include "H"
#include <cstdio>
int main(int c, char** v) { std::string w; std::filesystem::path p; int ok = 0;
  bool a = rs64_dir_writable(v[1], &w, &p); bool b = rs64_dir_writable(v[2], &w, &p); std::string wb = w;
  bool m = rs64_dir_writable(std::string(v[1]) + "/saves_missing", &w, &p);
  std::printf("rw=%d ro=%d(%s) missing_under_rw=%d\n", a, b, wb.c_str(), m); return (a && !b && m) ? 0 : 1; }'''
def unit(h):
    with tempfile.TemporaryDirectory() as t:
        open(f"{t}/H", "w").write(h); open(f"{t}/t.cpp", "w").write(TEST.replace('"H"', f'"{t}/H"'))
        os.makedirs(f"{t}/rw"); os.makedirs(f"{t}/ro"); os.chmod(f"{t}/ro", 0o555)
        try:
            subprocess.check_call(["c++", "-std=c++17", "-o", f"{t}/t", f"{t}/t.cpp"])
            r = subprocess.run([f"{t}/t", f"{t}/rw", f"{t}/ro"], capture_output=True, text=True)
            left = os.listdir(f"{t}/rw")
        finally: os.chmod(f"{t}/ro", 0o755)
        return r.returncode == 0 and not left, r.stdout.strip()
ok, out = unit(hdr); print(f"UNIT {out} {'PASS' if ok else 'FAIL'}")
mut = re.sub(r"(inline bool rs64_dir_writable\([^)]*\) \{)", r"\1 return true;", hdr, count=1)
mok, mout = unit(mut); print(f"MUTANT always_true caught={int(not mok)} {'PASS' if not mok and mut != hdr else 'FAIL'}")
w = main.find('rs64_dir_writable(rs_cwd / "saves"'); g = main.find("for (const auto& game : supported_games)")
st = w > 0 and main.find("recomp::register_config_path(rs_cwd)") < w < g and "SDL_ShowSimpleMessageBox" in main[w:g] and "ROGUESQ_RO_DIALOG" in main[w:g]
print(f"STATIC probe_before_game_start={int(st)} {'PASS' if st else 'FAIL'}")
def summ(tag):
    f = os.path.join(root, f"scratch/s7964/{tag}_summary.txt"); return open(f).read() if os.path.exists(f) else ""
o, n = summ("old"), summ("new")
def arm(s, a):
    m = re.search(rf"^\S+ {a}: (.*)$", s, re.M); return m[1] if m else ""
boots = all("vi320=1" in arm(s, a) and "crash_lines=0" in arm(s, a) for s in (o, n) for a in ("rw", "chmod", "dmg"))
ctl = "dmg CONTROL touch refused PASS" in o and "dmg CONTROL touch refused PASS" in n
print(f"CONTROL dmg_touch_refused={int(ctl)} rw_creates_mods={int('created=[mod_config mods' in arm(n, 'rw'))} {'PASS' if ctl and 'created=[mod_config mods' in arm(n, 'rw') else 'FAIL'}")
print(f"BOOT ro_arms_boot_both_binaries={int(boots)} {'PASS' if boots else 'FAIL'}")
silent = "s7964-ro" not in o
rep = "NOT writable saving=0 dialog=skip-nosave" in arm(n, "chmod") and "NOT writable saving=0 dialog=skip-nosave" in arm(n, "dmg") and "writable:" in arm(n, "rw")
dlg = "dialog=show" in arm(n, "dmg_dialog") and "update_screen=0 " in arm(n, "dmg_dialog") and "dialog=off" in arm(n, "dmg_nodlg") and "vi320=1" in arm(n, "dmg_nodlg")
print(f"FIX old_report=0:{int(silent)} new_report={int(rep)} dialog_modal={int(dlg)} {'PASS' if silent and rep and dlg else 'FAIL'}")
print("VERDICT CLOSED (H-silent fixed)" if ok and not mok and st and ctl and boots and silent and rep and dlg else "VERDICT OPEN")
