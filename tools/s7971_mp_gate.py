#!/usr/bin/env python3
"""s7971 class MP (host memory pressure while the game flies). `memory_pressure -S` needs root, so the stimulus is real:
tools/s7971_mp_e2e.zsh runs a forced-route flight per arm and at 125 s starts tools/s7971_mem_hog.py (incompressible,
page-hot allocation held 60 s; control 0 GB, mid 0.8 x free, high free + 0.5 x inactive, cap 8 GB), scored per arm by
tools/s7971_mp_score.py on the present ring + ROGUESQ_AI_TRACE + log + a 2 s host sampler (vm_stat, memorystatus level,
game RSS / footprint).
Checks: STATIC (H-handler: no memory-pressure / low-memory handler in src/, RT64 or the runtime outside contrib/, so no
cache drop-and-rebuild path exists to misbehave), SELFTEST (scorer planted stall / hold / underrun / alloc-fail / crash cases),
E2E (3/3 arms PASS, verdict moot, quit < 15 s), STIMULUS (the high arm really pressed the host: system compressions or
swapouts during the press > 10x the control arm's, the hog allocated >= 1 GB, and the GAME's resident set fell >= 20 MB
during the press = its own pages were compressed), CONTROL (scorer rejects a summary
with one arm planted FAIL)."""
import os, re, subprocess, sys
# zst-ok: reads only scratch/s7971/<tag>_summary.txt (raw) and source files
root = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip()
ok_all = True
def say(tag, body, ok):
    global ok_all
    ok_all &= ok; print(f"{tag} {body} {'PASS' if ok else 'FAIL'}")
pat = re.compile(r"MEMORYPRESSURE|memorypressure|LOWMEMORY|didReceiveMemoryWarning|os_proc_available_memory")
hits = []
for base in ("src", "lib/rt64/src", "lib/N64ModernRuntime"):
    for dp, dn, fn in os.walk(os.path.join(root, base)):
        dn[:] = [d for d in dn if d != "contrib"]
        for f in fn:
            if f.endswith((".c", ".cpp", ".h", ".hpp", ".mm", ".m")):
                try: s = open(os.path.join(dp, f), encoding="latin-1").read()
                except OSError: continue
                if pat.search(s): hits.append(os.path.relpath(os.path.join(dp, f), root))
# positive control for the census: the vendored SDL header in contrib DOES name SDL_APP_LOWMEMORY
ctl = any(pat.search(open(os.path.join(dp, f), encoding="latin-1").read())
          for dp, _, fn in os.walk(os.path.join(root, "lib/rt64/src/contrib")) for f in fn if f == "SDL_events.h")
say("STATIC", f"handlers={len(hits)} {','.join(hits) or '-'} census_control={int(ctl)}", not hits and ctl)
r = subprocess.run([sys.executable, os.path.join(root, "tools/s7971_mp_score.py"), "--selftest"], capture_output=True, text=True)
say("SELFTEST", f"rc={r.returncode} cases={r.stdout.count('selftest want=')}", r.returncode == 0 and r.stdout.count("selftest want=") == 9)
S = os.path.join(root, "scratch/s7971"); ARMS = ["flight_control", "flight_mid", "flight_high"]
def rd(p):
    try: return open(p, encoding="latin-1").read()
    except OSError: return ""
def score_new(s):
    got = [a for a in ARMS if re.search(rf"^new {a} PASS$", s, re.M)]
    return len(got) == 3 and "new VERDICT PASS" in s and "new new_crash_reports=0" in s, f"arms={len(got)}/3"
s = rd(f"{S}/new_summary.txt")
ok, body = score_new(s); say("E2E", body, ok)
def fld(arm, k):
    m = re.search(rf"^new {arm}: .*?\b{k}=(-?[0-9.]+)", s, re.M); return float(m.group(1)) if m else None
cc, ch = (fld("flight_control", "comp_d") or 0) + (fld("flight_control", "swo_d") or 0), (fld("flight_high", "comp_d") or 0) + (fld("flight_high", "swo_d") or 0)
gb = fld("flight_high", "gb") or 0; dr = fld("flight_high", "rss_drop_mb") or 0
say("STIMULUS", f"control_comp+swo={int(cc)} high_comp+swo={int(ch)} high_gb={gb:.2f} game_rss_drop_mb={int(dr)}", gb >= 1 and ch > 10 * max(cc, 1) and dr >= 20)
planted = re.sub(r"^new flight_high PASS$", "new flight_high FAIL", s, count=1, flags=re.M)
pok, _ = score_new(planted)
say("CONTROL", f"planted_fail_rejected={int(not pok)} (needs a real summary: {int(bool(s))})", bool(s) and not pok)
print("VERDICT", "CLOSED" if ok_all else "OPEN"); sys.exit(0 if ok_all else 1)
