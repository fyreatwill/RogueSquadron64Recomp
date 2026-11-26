#!/usr/bin/env python3
"""s7970 class SW (game process frozen for seconds-minutes, then resumed: system sleep, lid close, App Nap, a debugger stop).
Proxy: SIGSTOP / SIGCONT of the game (tools/s7970_sw_e2e.zsh; title + forced-route flight, stops 0/60/300 s, scored per arm
by tools/s7970_sw_score.py on the present ring + ROGUESQ_AI_TRACE + log). Measured before the fix: presents, game swaps and
quit are fine on resume (VI thread recomputes total_vis from the clock, no catch-up), but audio misbehaves: the drain-stall
watchdog sees a pull gap as long as the freeze and reopens the device as "drain-stall" (by chance), and when it does not, the
device drains the SDL queue at ~3x real time for ~3 s, so the game posts 3x audio (verdict=burst). Fix (src/main/main.cpp
s7970): a 50 ms heartbeat thread detects a > 1 s process freeze; the next audio post resets the drain-stall clock and
reopens the device ONCE with why=resume. ROGUESQ_S7970_SW=0 = old (mutant arm).
Checks: STATIC (fix present and env-gated), SELFTEST (scorer planted controls), E2E (new: 6/6 arms PASS, every stop arm
logs one [s7970-sw] resume line and one why=resume reopen, no drain-stall reopen), MUTANT (mut: no [s7970-sw] line, and at
least one stop arm is not moot = the defect reproduces with the fix off), CONTROL (scorer rejects a summary with one arm
planted FAIL)."""
import os, re, subprocess, sys
# zst-ok: reads only scratch/s7970/<tag>_<arm>.log, which s7970_sw_e2e.zsh keeps raw (it compresses only the .ring)
root = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip()
ok_all = True
def say(tag, body, ok):
    global ok_all
    ok_all &= ok; print(f"{tag} {body} {'PASS' if ok else 'FAIL'}")
mn = open(os.path.join(root, "src/main/main.cpp")).read()
st = {
    "env": 'getenv("ROGUESQ_S7970_SW")' in mn and "if (!s7970_sw_on()) return false;" in mn,
    "heartbeat": 'pthread_setname_np("s7970-heartbeat")' in mn and "if (gap > 1.0)" in mn,
    "reset": "last_pull = now; last_after = after;\n        g_s7970_resume_reopen = true;" in mn,
    "why_resume": 'else if (resumed && audio_device) why = "resume";' in mn,
}
say("STATIC", " ".join(f"{k}={int(v)}" for k, v in st.items()), all(st.values()))
r = subprocess.run([sys.executable, os.path.join(root, "tools/s7970_sw_score.py"), "--selftest"], capture_output=True, text=True)
say("SELFTEST", f"rc={r.returncode} cases={r.stdout.count('selftest want=')}", r.returncode == 0 and r.stdout.count("selftest want=") == 8)
S = os.path.join(root, "scratch/s7970")
ARMS = ["title_s0", "title_s60", "title_s300", "flight_s0", "flight_s60", "flight_s300"]
def rd(p):
    try: return open(p, encoding="latin-1").read()
    except OSError: return ""
def lines(tag, arm, pat): return len(re.findall(pat, rd(f"{S}/{tag}_{arm}.log")))
def score_new(s, logs=True):
    got = [a for a in ARMS if re.search(rf"^new {a} PASS$", s, re.M)]
    res = [a for a in ARMS if not a.endswith("_s0") and (not logs or (lines("new", a, r"\[s7970-sw\] resume after") >= 1 and
           lines("new", a, r"reopen n=\d+ why=resume") >= 1 and lines("new", a, r"why=drain-stall") == 0))]
    ok = len(got) == 6 and len(res) == 4 and "new VERDICT PASS" in s and "new new_crash_reports=0" in s
    return ok, f"arms={len(got)}/6 resume_wired={len(res)}/4"
s = rd(f"{S}/new_summary.txt")
ok, body = score_new(s); say("E2E", body, ok)
m = rd(f"{S}/mut_summary.txt")
mv = re.findall(r"^mut (\w+_s(?:60|300)): .* verdict=(\w+)", m, re.M)
nm = [a for a, v in mv if v != "moot"]; mwired = sum(lines("mut", a, r"\[s7970-sw\]") for a in ARMS)
say("MUTANT", f"stop_arms={len(mv)}/4 not_moot={','.join(nm) or '-'} s7970_lines={mwired}", len(mv) == 4 and len(nm) >= 1 and mwired == 0)
planted = re.sub(r"^new flight_s300 PASS$", "new flight_s300 FAIL", s, count=1, flags=re.M)
pok, _ = score_new(planted, logs=False)
say("CONTROL", f"planted_fail_rejected={int(not pok)} (needs a real summary: {int(bool(s))})", bool(s) and not pok)
print("VERDICT", "CLOSED" if ok_all else "OPEN"); sys.exit(0 if ok_all else 1)
