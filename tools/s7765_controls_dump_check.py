#!/usr/bin/env python3
"""s7765: owner-queue row 2 (`ROGUESQ_CONTROLS_DUMP=1`, controls.json) checked at launch, 4 arms, one game at a time.

  def   CONTROLS_DUMP=1, no controls.json         -> "[controls] no ...", dump D0
  rt    ROGUESQ_CONTROLS=<D0 as a file>           -> loaded, dump == D0 (OWNER-OPT-INS: the dump is "a ready-made starting file")
  ovr   ROGUESQ_CONTROLS=<A -> key:Space only>    -> loaded, dump A == ["key:Space"], every other entry == D0 (positive control)
  bad   ROGUESQ_CONTROLS=<malformed JSON>         -> rejected, dump == D0 (negative control)
Independent line for D0: the expected table is parsed from the VERBATIM pre-table code rs64_bind_old_sdl in main.cpp (not
from rs64_bind_defaults, which produced D0). Temp files live in scratch/s7765; build/controls.json and build/saves untouched.
rc 0 all PASS, 1 a mismatch, 2 an arm produced no dump.
"""
import json, os, re, signal, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "scratch/s7765")
N64 = {"A_BUTTON": "A", "B_BUTTON": "B", "Z_TRIG": "Z", "START_BUTTON": "START", "U_JPAD": "DU", "D_JPAD": "DD",
       "L_JPAD": "DL", "R_JPAD": "DR", "L_TRIG": "L", "R_TRIG": "R", "U_CBUTTONS": "CU", "D_CBUTTONS": "CD",
       "L_CBUTTONS": "CL", "R_CBUTTONS": "CR"}
PADN = {"DPAD_UP": "dpup", "DPAD_DOWN": "dpdown", "DPAD_LEFT": "dpleft", "DPAD_RIGHT": "dpright"}
AXN = {"TRIGGERLEFT": "lefttrigger", "TRIGGERRIGHT": "righttrigger"}
KEYN = {"RETURN": "Return", "UP": "Up", "DOWN": "Down", "LEFT": "Left", "RIGHT": "Right", "SPACE": "Space"}


def expected_from_old_code():
    src = open(os.path.join(ROOT, "src/main/main.cpp")).read()
    i = src.index("static void rs64_bind_old_sdl(")
    body = src[i:src.index("\n}\n", i)]
    b = {v: set() for v in N64.values()}
    for m, p in re.findall(r"^\s*gamepad_button\(N64_(\w+),\s*SDL_CONTROLLER_BUTTON_(\w+)\)", body, re.M):
        b[N64[m]].add("pad:" + PADN.get(p, p.lower()))
    for ax, thr, m in re.findall(r"SDL_CONTROLLER_AXIS_(\w+)\)\s*>\s*(\d+)\)\s*\{\s*btn \|= N64_(\w+);", body):
        b[N64[m]].add("axis+:%s:%s" % (AXN.get(ax, ax.lower()), thr))
    for k, m in re.findall(r"key\(SDL_SCANCODE_(\w+)\)\)\s+btn \|= N64_(\w+);", body):
        b[N64[m]].add("key:" + KEYN.get(k, k))
    st = {}
    for d, k in (("right", "D"), ("left", "A"), ("up", "W"), ("down", "S")):
        assert re.search(r"key\(SDL_SCANCODE_%s\)" % k, body), k
        st[d] = {"key:" + k}
    return b, st


def norm(d):
    return ({k: set(v) for k, v in d["buttons"].items()}, {k: set(d["stick"][k]) for k in ("up", "down", "left", "right")},
            (d["stick"]["pad_x"], d["stick"]["pad_y"], d["stick"]["invert_y"]))


def launch(tag, extra, cap=40):
    env = dict(os.environ); env.update({"ROGUESQ_CONTROLS_DUMP": "1", "ROGUESQ_NO_SAVE_WRITE": "1"}); env.update(extra)
    log = os.path.join(OUT, tag + ".log")
    with open(log, "w") as f:
        p = subprocess.Popen(["./RogueSquadron64Recomp"], cwd=os.path.join(ROOT, "build"), env=env, stdout=f,
                             stderr=subprocess.STDOUT, start_new_session=True)
        t0 = time.time(); done = None
        while time.time() - t0 < cap and p.poll() is None:
            time.sleep(0.5)
            txt = open(log, errors="replace").read()
            if "[controls] active table:" in txt and "\n}\n" in txt.split("[controls] active table:", 1)[1]:
                done = done or time.time()
                if time.time() - done > 1.0: break
        alive = p.poll() is None
        try: os.killpg(p.pid, signal.SIGKILL)
        except ProcessLookupError: pass
        p.wait()
    txt = open(log, errors="replace").read()
    st = re.findall(r"^\[controls\] (no |loaded |\S+ (rejected))", txt, re.M)
    st = [(m[1] or m[0]) for m in st]
    dump = None
    if "[controls] active table:" in txt:
        rest = txt.split("[controls] active table:\n", 1)[1]
        dump = json.loads(rest[:rest.index("\n}\n") + 3])
    return {"status": st[0].strip() if st else None, "dump": dump, "alive": alive, "log": log}


def main():
    os.makedirs(OUT, exist_ok=True)
    assert not os.path.exists(os.path.join(ROOT, "build/controls.json")), "build/controls.json exists: def arm not a no-file arm"
    eb, es = expected_from_old_code()
    res, ok = {}, True
    res["def"] = launch("def", {"ROGUESQ_CONTROLS": ""})
    if not res["def"]["dump"]: print("def: no dump"); return 2
    D0 = res["def"]["dump"]
    rt = os.path.join(OUT, "rt.json"); open(rt, "w").write(json.dumps(D0, indent=2) + "\n")
    ov = os.path.join(OUT, "ovr.json"); open(ov, "w").write('{"version":1,"buttons":{"A":["key:Space"]}}\n')
    bd = os.path.join(OUT, "bad.json"); open(bd, "w").write('{"version":1,"buttons":{"A":["key:Space"],}\n')
    res["rt"] = launch("rt", {"ROGUESQ_CONTROLS": rt})
    res["ovr"] = launch("ovr", {"ROGUESQ_CONTROLS": ov})
    res["bad"] = launch("bad", {"ROGUESQ_CONTROLS": bd})
    nb, ns, nstick = norm(D0)
    checks = [("def status=no", res["def"]["status"] == "no"),
              ("def buttons == old code", nb == eb), ("def stick keys == old code", ns == es),
              ("def stick pad", nstick == ("leftx", "lefty", True))]
    for t in ("rt", "ovr", "bad"):
        if not res[t]["dump"]: print(t, ": no dump"); return 2
    checks += [("rt status=loaded", res["rt"]["status"] == "loaded"), ("rt dump == D0", res["rt"]["dump"] == D0)]
    ob, os_, ost = norm(res["ovr"]["dump"])
    exp_ob = dict(nb); exp_ob["A"] = {"key:Space"}
    checks += [("ovr status=loaded", res["ovr"]["status"] == "loaded"), ("ovr A == key:Space", ob["A"] == {"key:Space"}),
               ("ovr others == D0", ob == exp_ob and os_ == ns and ost == nstick), ("ovr differs from D0", res["ovr"]["dump"] != D0)]
    checks += [("bad status=rejected", res["bad"]["status"] == "rejected"), ("bad dump == D0", res["bad"]["dump"] == D0)]
    for t in res: print("arm %-3s status=%s alive_at_kill=%s log=%s" % (t, res[t]["status"], res[t]["alive"], os.path.relpath(res[t]["log"], ROOT)))
    for n, c in checks:
        print("%-28s %s" % (n, "PASS" if c else "FAIL")); ok &= c
    if nb != eb:
        for k in eb:
            if nb.get(k) != eb[k]: print("  diff", k, "dump", sorted(nb.get(k, [])), "old", sorted(eb[k]))
    print("expected-from-old-code bindings:", sum(len(v) for v in eb.values()), "button sources")
    print("VERDICT", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
