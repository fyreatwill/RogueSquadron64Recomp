#!/usr/bin/env python3
"""s7966 class DI (two game instances on one data root). Harnesses tools/s7966_di/harness.cpp (librecomp files.cpp save
finalize, 2 writer processes + a sampling reader) and tools/s7966_di/hdr_test.cpp (rs64_write_file_atomic 2 writers,
rs64_instance_lock); e2e tools/s7966_di_e2e.zsh (summary scratch/s7966/new_summary.txt).
Measured s7966: the shared <save>.temp let one instance truncate the inode the other was writing and publish it
(49 torn/short samples + 273 finalize failures = in-game "Failed to write" dialogs, 2x2000 saves) -> H-corrupt; and the
last writer wins regardless (H-clobber). Fix: per-pid temp names (files.cpp rs64_private_temp, rs64_atomic_write.h
rs64_private_tmp_path, F6 controls save) + an flock on <data root>/saves/.rs64_instance.lock; a second instance logs
[s7966-di], shows one dialog when saving is on (ROGUESQ_DI_DIALOG=0 = line only) and runs with ROGUESQ_NO_SAVE_WRITE=1.
Mutants: ROGUESQ_S7966_SHARED_TEMP=1 (old shared names), ROGUESQ_S7966_NO_LOCK=1; control ROGUESQ_S7429_OLD_FINALIZE=1."""
import os, re, subprocess, sys, tempfile, shutil
root = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip()
L = os.path.join(root, "lib/N64ModernRuntime/librecomp")
t = tempfile.mkdtemp(prefix="s7966g")
ok_all = True
def say(tag, body, ok):
    global ok_all
    ok_all &= ok; print(f"{tag} {body} {'PASS' if ok else 'FAIL'}")
def kv(s):
    return {k: v for k, v in re.findall(r"(\w+)=(\S+)", s)}
try:
    h, u = f"{t}/h", f"{t}/u"
    subprocess.check_call(["clang++", "-std=c++20", "-O1", f"-I{L}/include/librecomp", f'-DFILES_CPP="{L}/src/files.cpp"',
                           os.path.join(root, "tools/s7966_di/harness.cpp"), "-o", h])
    subprocess.check_call(["c++", "-std=c++20", "-O1", os.path.join(root, "tools/s7966_di/hdr_test.cpp"), "-o", u])
    def run(b, args, **env):
        d = f"{t}/d{len(os.listdir(t))}"
        e = {k: v for k, v in os.environ.items() if not k.startswith("ROGUESQ_S7966") and k != "ROGUESQ_S7429_OLD_FINALIZE"}
        e.update(env)
        r = subprocess.run([b, d] + args, capture_output=True, text=True, env=e); return r.stdout.strip()
    f1, f2 = run(h, ["1500"]), run(h, ["1500"])
    a, b = kv(f1), kv(f2)
    say("FIX", f"save torn={a['torn']}+{b['torn']} finalize_fail={a['finalize_fail']}+{b['finalize_fail']}",
        a["torn"] == b["torn"] == "0" and a["finalize_fail"] == b["finalize_fail"] == "0" and a["final"] != "BAD" != b["final"])
    m = kv(run(h, ["1500"], ROGUESQ_S7966_SHARED_TEMP="1"))
    say("MUTANT shared_temp", f"torn={m['torn']} finalize_fail={m['finalize_fail']} caught={int(int(m['torn']) + int(m['finalize_fail']) > 0)}",
        int(m["torn"]) + int(m["finalize_fail"]) > 0)
    c = kv(run(h, ["1500"], ROGUESQ_S7966_SHARED_TEMP="1", ROGUESQ_S7429_OLD_FINALIZE="1"))
    say("CONTROL old_copy_finalize", f"torn={c['torn']}", int(c["torn"]) > 0)
    hf = run(u, ["400"]); at = kv(hf.split("\n")[0]); lk = kv(hf.split("\n")[1])
    say("ATOMIC", f"bad={at['bad']} fails={at['fails']}", at["bad"] == "0" and at["fails"] == "0")
    hm = kv(run(u, ["400"], ROGUESQ_S7966_SHARED_TEMP="1").split("\n")[0])
    say("ATOMIC_MUTANT shared_temp", f"bad={hm['bad']} fails={hm['fails']}", int(hm["bad"]) + int(hm["fails"]) > 0)
    say("LOCK", f"first={lk['first']} second={lk['second']} after_holder_sigkill={lk['after_holder_sigkill']}",
        lk["first"] == "1" and lk["second"] == "0" and lk["other_holder"] == "0" and lk["after_holder_sigkill"] == "1")
    nl = kv(run(u, ["20"], ROGUESQ_S7966_NO_LOCK="1").split("\n")[1])
    say("LOCK_MUTANT no_lock", f"second={nl['second']} (must not read busy)", nl["second"] != "0")
finally:
    shutil.rmtree(t, ignore_errors=True)
main = open(os.path.join(root, "src/main/main.cpp")).read()
w = main.find('rs64_instance_lock(rs_cwd / "saves"'); g = main.find("for (const auto& game : supported_games)")
blk = main[w:g] if w > 0 else ""
st = (w > 0 and main.find("recomp::register_config_path(rs_cwd)") < w < g and 'setenv("ROGUESQ_NO_SAVE_WRITE"' in blk
      and "ROGUESQ_DI_DIALOG" in blk and ("rs64_private_tmp_path(path)" in main or "rs64_write_file_atomic(path, text" in main) and 'path + ".tmp"' not in main  # s7972: rs64_bind_save -> shared writer
      and "rs64_private_tmp_path(path)" in open(os.path.join(root, "src/main/rs64_atomic_write.h")).read()
      and open(os.path.join(L, "src/files.cpp")).read().count("rs64_private_temp(") >= 3)
say("STATIC", f"lock_before_game_start+nosave_flip+private_temps={int(st)}", st)
sf = os.path.join(root, "scratch/s7966/new_summary.txt"); s = open(sf).read() if os.path.exists(sf) else ""
arms = {a: bool(re.search(rf"^new {a} PASS", s, re.M)) for a in ("nosave", "save", "dialog", "mutant", "relock")}
say("E2E", " ".join(f"{a}={int(v)}" for a, v in arms.items()), all(arms.values()) and "VERDICT PASS" in s)
print("VERDICT", "CLOSED" if ok_all else "OPEN"); sys.exit(0 if ok_all else 1)
