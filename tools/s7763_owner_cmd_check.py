#!/usr/bin/env python3
"""s7763: launch every distinct command in docs/OWNER-REVIEW-QUEUE.md and check that the settings the game
ECHOES at startup match what the command claims (real env > preset, as rs64_settings.cpp documents).

Per command: expected dd / aspect / fps60 / fullscreen / standins are computed from the command text (env vars
override the preset's vars); observed values come from the game's own echo lines:
  [s7663] settings applied (re-exec): ...      -> which preset vars were applied
  [ddbundle] dd=<x>                            -> effective draw distance (absent = dd1)
  [g1d] ROGUESQ_ASPECT=<a> -> FB_WIDTH=        -> effective aspect (absent = 4:3 retail)
  [g1f] window WxH fullscreen=<0|1>            -> fullscreen
  [standins] on ... dd=                        -> stand-ins on
One game at a time (CLAUDE.md), SIGKILL after the echo set is complete or --cap seconds.
--control adds an arm with a deliberately different env (DRAW_DISTANCE=3 over --preset tv) that must echo 3:
the positive control that the checker can see an env override at all.
rc 0 = every command matches; rc 1 = a mismatch (the row lies); rc 2 = an arm never produced its echoes.
"""
import os, re, signal, subprocess, sys, time, argparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRESETS = {  # mirror of src/main/rs64_settings.cpp presets(); checked against the source below
    "retail": {}, "window": {"ROGUESQ_FPS60": "1", "ROGUESQ_DRAW_DISTANCE": "2"},
    "tv": {"ROGUESQ_FPS60": "1", "ROGUESQ_DRAW_DISTANCE": "4", "ROGUESQ_ASPECT": "16:9", "ROGUESQ_FULLSCREEN": "1"},
    "ultrawide": {"ROGUESQ_FPS60": "1", "ROGUESQ_DRAW_DISTANCE": "4", "ROGUESQ_ASPECT": "21:9", "ROGUESQ_FULLSCREEN": "1"},
}


def check_preset_mirror():
    src = open(os.path.join(ROOT, "src/main/rs64_settings.cpp")).read()
    for name, vs in PRESETS.items():
        m = re.search(r'\{"%s",\s*"[^"]*",\s*\{(.*?)\}\},' % name, src, re.S)
        got = dict(re.findall(r'\{"(ROGUESQ_\w+)",\s*"([^"]*)"\}', m.group(1))) if m else None
        if got != vs:
            sys.exit("preset mirror stale for %s: source %s vs checker %s" % (name, got, vs))


def commands():
    txt = open(os.path.join(ROOT, "docs/OWNER-REVIEW-QUEUE.md")).read()
    out = {}
    for line in txt.splitlines():
        m = re.match(r"\|\s*(\d+)\s*\|", line)
        if not m:
            continue
        cell = line.split("|")[3]
        for c in re.findall(r"`([^`]*RogueSquadron64Recomp[^`]*)`", cell):
            out.setdefault(c.strip(), []).append(int(m.group(1)))
        for c in re.findall(r"`(--preset \w+)`", cell):  # shorthand cells: "`--preset tv`, ..."
            out.setdefault("./RogueSquadron64Recomp " + c, []).append(int(m.group(1)))
    return out


def parse(cmd):
    toks = cmd.split()
    env, preset = {}, None
    for i, t in enumerate(toks):
        if re.match(r"ROGUESQ_\w+=", t):
            k, v = t.split("=", 1); env[k] = v
        if t == "--preset":
            preset = toks[i + 1]
    exp = dict(PRESETS.get(preset, {}))
    exp.update(env)  # real env beats preset
    dd = float(exp.get("ROGUESQ_DRAW_DISTANCE", "1"))
    if dd > 4 and exp.get("ROGUESQ_DD_UNSAFE") != "1":
        dd = 4.0  # documented clamp without DD_UNSAFE
    want = {"dd": dd, "aspect": exp.get("ROGUESQ_ASPECT", "4:3"), "fps60": exp.get("ROGUESQ_FPS60", "0"),
            "fullscreen": exp.get("ROGUESQ_FULLSCREEN", "0"),
            "standins": "1" if exp.get("ROGUESQ_STANDINS", "0") not in ("0", "") and dd > 1 else "0"}
    return env, preset, want


# Row-specific switches: echo that must appear iff the command sets the var (second witness besides the
# preset/dd/aspect echoes). Retina's [retina] line prints in every run; ON = swap chain at drawable (backing) size.
FEATURES = {
    "ROGUESQ_S7115_NEARLIFT": lambda t: "[g1e-fast] on=0 reason=ROGUESQ_S7115_NEARLIFT" in t,
    "ROGUESQ_RETINA": lambda t: (lambda d, s: bool(d and s and d.group(1) == s.group(1)))(
        re.search(r"\[g1f\] drawable (\d+)x", t), re.search(r"\[retina\] swapchain create (\d+)x", t)),
    "ROGUESQ_QOS_ALL": lambda t: "[s6989] QOS_ALL" in t,
    "ROGUESQ_RENDER_TO_RAM": lambda t: "renderToRAM forced OFF" in t,
    "ROGUESQ_S7524_V2P": lambda t: "[s7524] DMEM OSTask virtual" in t,
    "ROGUESQ_SP_LATE": lambda t: "[s7536] ROGUESQ_SP_LATE=1" in t,
}


def observe(log):
    from rs64_zopen import zopen, resolve  # s7804: --offline re-scores retained armNN.log, zstd'd since
    t = zopen(resolve(log) or log).read()
    o = {}
    m = re.search(r"\[ddbundle\] dd=([\d.]+)", t); o["dd"] = float(m.group(1)) if m else 1.0
    m = re.search(r"\[g1d\] ROGUESQ_ASPECT=(\S+) -> FB_WIDTH", t); o["aspect"] = m.group(1) if m else "4:3"
    m = re.search(r"\[g1f\] window \d+x\d+ fullscreen=(\d)", t); o["fullscreen"] = m.group(1) if m else None
    o["standins"] = "1" if re.search(r"\[standins\] on mode=", t) else "0"
    m = re.search(r"\[s7663\] settings applied \(re-exec\): (.*)", t)
    applied = m.group(1) if m else ""
    o["applied"] = applied
    o["fps60"] = None  # resolved by the caller from env + applied summary
    return o, t


def run(cmd, env_extra, preset, log, cap):
    env = dict(os.environ)
    env.update({"ROGUESQ_NO_SAVE_WRITE": "1"})  # owner save rule: never write the owner's save
    env.update(env_extra)
    argv = ["./RogueSquadron64Recomp"] + (["--preset", preset] if preset else [])
    with open(log, "w") as f:
        p = subprocess.Popen(argv, cwd=os.path.join(ROOT, "build"), env=env, stdout=f, stderr=subprocess.STDOUT,
                             start_new_session=True)
    t0 = time.time()
    while time.time() - t0 < cap and p.poll() is None:
        time.sleep(1)
        t = open(log, errors="replace").read()
        if "[g1f] window" in t and "[g1d-heapcap]" in t and time.time() - t0 > 8:
            time.sleep(4); break  # standins / ddbundle echo before the first heapcap line
    alive = p.poll() is None
    try:
        os.killpg(p.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    p.wait()
    return alive, time.time() - t0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cap", type=int, default=45)
    ap.add_argument("--control", action="store_true")
    ap.add_argument("--offline", action="store_true", help="re-score existing armNN.log, no launches")
    ap.add_argument("--out", default=os.path.join(ROOT, "scratch/s7763"))
    a = ap.parse_args()
    check_preset_mirror()
    os.makedirs(a.out, exist_ok=True)
    cmds = commands()
    if a.control:
        cmds["env ROGUESQ_DRAW_DISTANCE=3 ./RogueSquadron64Recomp --preset tv"] = ["CTL"]
    bad = noecho = 0
    for i, (cmd, rows) in enumerate(cmds.items()):
        env, preset, want = parse(cmd)
        log = os.path.join(a.out, "arm%02d.log" % i)
        alive, secs = (1, 0) if a.offline else run(cmd, env, preset, log, a.cap)
        o, t = observe(log)
        # fps60: env value if given, else the preset value must appear in the applied summary
        if "ROGUESQ_FPS60" in env:
            o["fps60"] = env["ROGUESQ_FPS60"]
        else:
            m = re.search(r"ROGUESQ_FPS60=(\S+)\(preset\)", o["applied"]); o["fps60"] = m.group(1) if m else "0"
        miss = [k for k in want if str(o.get(k)) != str(want[k])]
        for var, seen in FEATURES.items():  # set in this command <-> its echo fired
            if (var in env) != seen(t):
                miss.append(var)
        if o["fullscreen"] is None:
            noecho += 1
        if miss:
            bad += 1
        print("rows=%s %s alive=%d %.0fs | want %s | got %s | %s" % (
            ",".join(map(str, rows)), "MATCH" if not miss else "MISMATCH " + ",".join(miss), alive, secs,
            " ".join("%s=%s" % kv for kv in want.items()),
            " ".join("%s=%s" % (k, o[k]) for k in want), cmd))
    print("s7763 owner_cmd_check: commands=%d mismatch=%d noecho=%d" % (len(cmds), bad, noecho))
    sys.exit(1 if bad else 2 if noecho else 0)


if __name__ == "__main__":
    main()
