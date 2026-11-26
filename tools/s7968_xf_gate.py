#!/usr/bin/env python3
"""s7968 class XF (game folder on a non-APFS volume: exFAT / FAT32 USB stick). One 64 MB image per FS (APFS = control) runs
the save-path harnesses against the real librecomp files.cpp: s7429 kill-at-offset (SIGKILL inside the save sequence; the
ROGUESQ_S7429_OLD_FINALIZE=1 copy finalize must tear on every FS = positive control, the rename finalize must not:
H-rename refuted), s7966 two-writer + atomic writer + flock (flock is honoured by the fskit exFAT/msdos drivers: H-flock
refuted), s7967 write/read cycles (fsync path: H-fsync refuted). H-xattr CONFIRMED: FAT/exFAT store xattrs in "._<name>"
AppleDouble sidecars, and the mods/ scanner opened "._foo.nrm" as a mod ("invalid zip file"); mods.cpp now skips "._*"
(ROGUESQ_S7968_XF=0 = old scan). E2E tools/s7968_xf_e2e.zsh (summary scratch/s7968/new_summary.txt)."""
import os, re, subprocess, sys, tempfile, shutil
root = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip()
L = os.path.join(root, "lib/N64ModernRuntime/librecomp")
t = tempfile.mkdtemp(prefix="s7968g")
ok_all = True
def say(tag, body, ok):
    global ok_all
    ok_all &= ok; print(f"{tag} {body} {'PASS' if ok else 'FAIL'}")
def kv(s): return {k: v for k, v in re.findall(r"(\w+)=(\S+)", s)}
def sh(cmd, **env):
    e = {k: v for k, v in os.environ.items() if not k.startswith(("ROGUESQ_S7966", "ROGUESQ_S7429"))}; e.update(env)
    return subprocess.run(cmd, capture_output=True, text=True, env=e).stdout.strip()
mounts = []
try:
    inc = [f"-I{L}/include/librecomp", f'-DFILES_CPP="{L}/src/files.cpp"']
    b = {k: f"{t}/{k}" for k in ("q", "di", "hdr", "cs")}
    subprocess.check_call(["clang++", "-std=c++20", "-O1", *inc, "-DLOADER_FALLBACK=0", f"{root}/tools/s7429_save_quit/harness.cpp", "-o", b["q"]])
    subprocess.check_call(["clang++", "-std=c++20", "-O1", *inc, f"{root}/tools/s7966_di/harness.cpp", "-o", b["di"]])
    subprocess.check_call(["c++", "-std=c++20", "-O1", f"{root}/tools/s7966_di/hdr_test.cpp", "-o", b["hdr"]])
    subprocess.check_call(["clang++", "-std=c++20", "-O1", *inc, f"{root}/tools/s7967_cs/harness.cpp", "-o", b["cs"]])
    for fs in ("APFS", "ExFAT", "MS-DOS FAT32"):
        n = fs.split()[0]; img, m = f"{t}/{n}.dmg", f"{t}/m_{n}"
        subprocess.check_call(["hdiutil", "create", "-quiet", "-size", "64m", "-fs", fs, "-volname", "XG" + n[:4], img])
        subprocess.check_call(["hdiutil", "attach", "-quiet", "-nobrowse", "-mountpoint", m, img]); mounts.append(m)
        kind = subprocess.run(["mount"], capture_output=True, text=True).stdout
        mk = re.search(rf"on {re.escape(os.path.realpath(m))} \((\w+)", kind); kind = mk.group(1) if mk else "?"
        old = kv(sh([b["q"], f"{m}/qo", "500", "60000"], ROGUESQ_S7429_OLD_FINALIZE="1"))
        new = kv(sh([b["q"], f"{m}/qn", "500", "60000"]))
        say(f"KILL {n} fs={kind}", f"old_short={old.get('short')} new_bad={int(new.get('short', 1)) + int(new.get('mixed', 1)) + int(new.get('missing', 1))} new_B={new.get('B')}",
            int(old.get("short", 0)) > 0 and new.get("short") == new.get("mixed") == new.get("missing") == "0" and int(new.get("B", 0)) > 0)
        d = kv(sh([b["di"], f"{m}/di", "300"]))
        say(f"TWOWRITER {n}", f"torn={d.get('torn')} finalize_fail={d.get('finalize_fail')}", d.get("torn") == d.get("finalize_fail") == "0" and d.get("final") in ("A", "B"))
        h = sh([b["hdr"], f"{m}/hd", "100"]).split("\n"); at, lk = kv(h[0]), kv(h[1]) if len(h) > 1 else {}
        say(f"ATOMIC+LOCK {n}", f"bad={at.get('bad')} fails={at.get('fails')} first={lk.get('first')} second={lk.get('second')} after_kill={lk.get('after_holder_sigkill')}",
            at.get("bad") == at.get("fails") == "0" and lk.get("first") == "1" and lk.get("second") == "0" and lk.get("after_holder_sigkill") == "1")
        os.makedirs(f"{m}/cs", exist_ok=True); w = sh([b["cs"], "write", f"{m}/cs/s.bin", "512", "55", "100"]); r = sh([b["cs"], "read", f"{m}/cs/s.bin", "512", "55"])
        ad = sum(1 for x in os.listdir(f"{m}/cs") if x.startswith("._"))
        say(f"WRITEREAD {n}", f"{w.split(' final')[0]} payload={kv(r).get('payload')} appledouble={ad}", "fails=0" in w and kv(r).get("payload") == "ok" and (ad == 0) == (n == "APFS"))
finally:
    for m in mounts: subprocess.run(["hdiutil", "detach", "-quiet", "-force", m])
    shutil.rmtree(t, ignore_errors=True)
src = open(os.path.join(L, "src/mods.cpp")).read()
i, j = src.find('getenv("ROGUESQ_S7968_XF")'), src.find("bool is_mod = false;", src.find("scan_mod_folder("))
st = 0 < i < j and 'rfind("._", 0) == 0' in src[i:j] and "continue;" in src[i:j]
say("STATIC", f"mods_scan_skips_appledouble={int(st)}", st)
sf = os.path.join(root, "scratch/s7968/new_summary.txt"); s = open(sf).read() if os.path.exists(sf) else ""
need = [f"{fs} {a}" for fs in ("APFS", "ExFAT", "MS-DOS") for a in ("save", "second", "mods_fix", "mods_mutant", "relaunch")]
got = [x for x in need if re.search(rf"^new {x} PASS", s, re.M)]
adm = len(re.findall(r"^new (ExFAT|MS-DOS) mods_mutant PASS: .*appledouble_opened=[1-9]", s, re.M))
say("E2E", f"arms={len(got)}/{len(need)} fat_mutant_opened={adm}", len(got) == len(need) and adm == 2 and "VERDICT PASS" in s)
print("VERDICT", "CLOSED" if ok_all else "OPEN"); sys.exit(0 if ok_all else 1)
