#!/usr/bin/env python3
"""s7675 G6c ghost score: per subtype, the camera distance (view-test depth) at each real object's first addNpcToVisibilityBucket
call ([s7675-fr] fr_d) and, for stand-ins whose real object never called (delay=never), the closest our held stand-in came
(held_dmin). Positive control = the ordinary subtypes (0x0D/0x14/...) whose first call is at their spawn distance.
Verdict per never-case: GATE (held_dmin > every first-call depth seen for that subtype: the player never came close enough,
the stand-in bridges a distance-gated draw) or GHOST (held_dmin <= the subtype's max first-call depth: the real object was in
draw range and still never drew). rc 1 = any GHOST. Usage: s7675_ghost_score.py log_x4.txt [...]"""
import re, sys, collections
rc = 0
if sys.argv[1:] == ["--selftest"]:  # s7676 positive control: a synthetic GHOST must give rc 1, a GATE rc 0
    import subprocess, tempfile, os
    base = "[s7675-fr] item 1 sub 0047 odd=1 delay=800 fr_d=51.10 spawn_d=70 held_dmin=51.10\n"
    out = {}
    for name, hd in (("ghost", "40.00"), ("gate", "62.25")):
        t = tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False)
        t.write(base + "[s7675-fr] item 2 sub 0047 odd=1 delay=never fr_d=-1 spawn_d=71 held_dmin=%s\n" % hd); t.close()
        out[name] = subprocess.run([sys.executable, __file__, t.name], capture_output=True).returncode; os.unlink(t.name)
    ok = out == {"ghost": 1, "gate": 0}
    print("selftest ghost rc=%d gate rc=%d -> %s" % (out["ghost"], out["gate"], "PASS" if ok else "FAIL")); sys.exit(0 if ok else 1)
for path in sys.argv[1:]:
    fr = collections.defaultdict(list); never = []
    for l in open(path, errors="replace"):
        if not l.startswith("[s7675-fr]"): continue
        f = l.split(); d = dict(re.findall(r"(\w+)=(\S+)", l)); sub = f[4]
        if d["delay"] == "never": never.append((f[2], sub, float(d["held_dmin"]), d["odd"]))
        elif float(d["fr_d"]) >= 0: fr[sub].append((int(d["delay"]), float(d["fr_d"])))
    print("==", path)
    for sub, v in sorted(fr.items()):
        ds = sorted(x[1] for x in v); dl = sorted(x[0] for x in v)
        print("sub %s first calls=%d depth min/med/max %.1f/%.1f/%.1f delay med/max %d/%d" % (sub, len(v), ds[0], ds[len(ds)//2], ds[-1], dl[len(dl)//2], dl[-1]))
    for item, sub, hd, odd in never:
        ref = [x[1] for x in fr.get(sub, [])]
        if hd < 0: verdict = "UNHELD(no depth)"
        elif not ref: verdict = "NOREF(no first call of this subtype)"
        else: verdict = "GATE" if hd > max(ref) else "GHOST"
        if verdict == "GHOST": rc = 1
        print("never item %s sub %s odd=%s held_dmin=%.1f sub_max_first=%s -> %s" % (item, sub, odd, hd, ("%.1f" % max(ref)) if ref else "-", verdict))
sys.exit(rc)
