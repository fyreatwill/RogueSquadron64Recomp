#!/usr/bin/env python3
"""Score a regress.sh capture: per-phase content verdict + run-log counters.

Turns a burst plus a run log into one machine-readable verdict.json, so a
change can be judged against a stored baseline instead of by opening PNGs.

Two measurement rules are baked in, both learned the hard way:

1. Sampled diagnostics lie about totals. `[defer-drop #N]` prints only the
   first 32 events and then every 64th (src/rsp/dpc_bridge.cpp:1381), so
   COUNTING THE LINES measures the sampler, not the stream. The running index
   is in the message, so the total is max(N) -- that is what this reports.
   Session 18 lost a conclusion to exactly this trap with `[loadblock]`.

2. A phase with too few frames is not judged. A content fraction over two
   frames is noise; phases under MIN_FRAMES are reported as `insufficient`
   rather than passed or failed.

Usage:  regress_score.py <outdir> [--baseline verdict.json] [--label name]
Exit:   0 = PASS, 1 = FAIL (usable as a loop gate), 2 = harness error
"""
import sys
import os
import re
import json
import statistics
from datetime import datetime, timezone

# Pillow lives in a venv that is not on the default path. Re-exec into an
# interpreter that has it rather than making every caller remember.
try:
    import PIL  # noqa: F401
except ImportError:                                   # pragma: no cover
    _here = os.path.dirname(os.path.abspath(__file__))
    _root = os.path.dirname(_here)
    for _cand in (os.environ.get("REGRESS_PYTHON"),
                  os.path.join(_root, "scratch", "venv", "bin", "python3"),
                  os.path.join(_root, ".venv", "bin", "python3")):
        if _cand and os.path.exists(_cand) and _cand != sys.executable:
            os.execv(_cand, [_cand, os.path.abspath(__file__)] + sys.argv[1:])
    sys.exit("regress_score: no python with Pillow found "
             "(set REGRESS_PYTHON, or: python3 -m venv scratch/venv && "
             "scratch/venv/bin/pip install Pillow)")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from frames import stats                              # noqa: E402  (reuse, don't reimplement)

MIN_FRAMES = 3          # below this a phase is reported, not judged
CONTENT_DROP_FAIL = 0.25    # absolute content-fraction drop that fails a phase
DISTINCT_DROP_FAIL = 0.50   # relative median-distinct drop that fails a phase

FRAME_RE = re.compile(r"f_(\d+)_(\d+\.\d)_p(\d+)_w(\d+)\.png$")
PHASE_RE = re.compile(r"\[phase\] vi_width=(\d+) \(was (\d+)\) "
                      r"origin=0x([0-9A-Fa-f]+) at ([0-9.]+)s")
MISSING_RE = re.compile(r"\[missing-func\] (0x[0-9A-Fa-f]+)")
# Sampled counters: the running index inside the tag is the real total.
SAMPLED_RE = {
    "defer_drop": re.compile(r"\[defer-drop #(\d+)\]"),
    "defer_commit": re.compile(r"\[defer-commit #(\d+)\]"),
}
ABORT_PATTERNS = [
    (re.compile(r"Assertion failed", re.I), "assert"),
    (re.compile(r"libc\+\+abi", re.I), "abort"),
    (re.compile(r"terminating with uncaught", re.I), "abort"),
    (re.compile(r"Failed to allocate IOGPUDeviceShmem", re.I), "gpu_oom"),
    (re.compile(r"Failed to find function at", re.I), "missing_func_fatal"),
    (re.compile(r"UnhandledJumpTarget", re.I), "unhandled_jump"),
]


def read_log(path):
    """Parse run.log into counters. Returns (counters, phase_transitions)."""
    counters = {
        "missing_func_addrs": [], "defer_drop_total": 0,
        "defer_commit_total": 0, "aborts": {},
    }
    transitions = []
    seen_missing = set()
    if not os.path.exists(path):
        return counters, transitions
    with open(path, "r", errors="replace") as fh:
        for line in fh:
            m = PHASE_RE.search(line)
            if m:
                transitions.append({
                    "ord": len(transitions) + 1,
                    "width": int(m.group(1)),
                    "prev_width": int(m.group(2)),
                    "origin": "0x" + m.group(3).upper(),
                    "t": float(m.group(4)),
                })
            m = MISSING_RE.search(line)
            if m and m.group(1) not in seen_missing:
                seen_missing.add(m.group(1))
                counters["missing_func_addrs"].append(m.group(1))
            for key, rx in SAMPLED_RE.items():
                m = rx.search(line)
                if m:
                    counters[key + "_total"] = max(counters[key + "_total"],
                                                   int(m.group(1)))
            for rx, tag in ABORT_PATTERNS:
                if rx.search(line):
                    counters["aborts"][tag] = counters["aborts"].get(tag, 0) + 1
    counters["missing_func_distinct"] = len(counters["missing_func_addrs"])
    return counters, transitions


def check_input_landed(env_path, transitions):
    """FAIL when a key schedule ran but nothing in the game reacted.

    This is a FAIL, not a WARN (changed in session 25). A run whose keys did not
    land did not visit the screens it was asked to visit -- it silently followed
    the undriven route -- so every per-phase number in the verdict describes a
    different part of the game than the caller asked for. Scoring that PASS is
    the same class of mistake as `window_burst.sh` reporting a dead window as
    "60/60 frames with content": the harness reporting a run it did not perform
    as a clean one. Session 25 lost a band-attribution probe to exactly this and
    got a PASS for it.

    winctl posts events with CGEventPostToPid, which returns success and
    silently does nothing when the calling process lacks Accessibility
    permission -- so 'keys fired' in the runner log is NOT evidence the game
    saw them. The observable consequence of a landed key press is that the
    game leaves its current screen; if no VI transition follows the schedule,
    the run almost certainly took the undriven path.

    Returns a list of (level, message).
    """
    keys = ""
    if os.path.exists(env_path):
        for line in open(env_path):
            if line.startswith("keys:"):
                keys = line.split(":", 1)[1].strip()
    if not keys or keys == "<none>":
        return []

    # Latest fire time per width group: "<width>@<sec>[:<key>]".
    last_offset = {}
    for tok in keys.split():
        if "@" not in tok:
            continue
        w, rest = tok.split("@", 1)
        try:
            sec = float(rest.split(":", 1)[0])
            last_offset[int(w)] = max(last_offset.get(int(w), 0.0), sec)
        except ValueError:
            continue

    entry = {}
    for t in transitions:
        entry.setdefault(t["width"], t["t"])

    out = []
    for w, off in sorted(last_offset.items()):
        if w not in entry:
            continue
        fired_at = entry[w] + off
        # 10s, not longer: the undriven boot path has its own transition ~19s
        # after the title keys would fire (measured 54.4s keys -> 73.1s), and a
        # window wide enough to swallow that makes the check always pass. A
        # landed Start advances the screen within a few seconds (driven runs
        # reach the 512 hangar 0.3s after the last key).
        if not any(t["t"] > fired_at and t["t"] <= fired_at + 10.0
                   for t in transitions):
            out.append(("FAIL", f"keys for width {w} fired around "
                                f"{fired_at:.1f}s but no VI transition followed "
                                f"within 10s -- input did not reach the game "
                                f"(needs Accessibility permission), so this run "
                                f"took the UNDRIVEN route and its phases are not "
                                f"the ones requested"))
    return out


def read_outcome(path):
    out = {"status": "unknown", "elapsed": 0.0, "frames": 0}
    if os.path.exists(path):
        for tok in open(path).read().split():
            if "=" in tok:
                k, v = tok.split("=", 1)
                if k in ("elapsed",):
                    out[k] = float(v)
                elif k in ("frames",):
                    out[k] = int(v)
                else:
                    out[k] = v
    return out


def score_phases(outdir):
    """Group frames by the phase tagged into their filename and score each."""
    buckets = {}
    for name in sorted(os.listdir(outdir)):
        m = FRAME_RE.search(name)
        if not m:
            continue
        _, elapsed, ord_, width = m.groups()
        buckets.setdefault((int(ord_), int(width)), []).append(
            (float(elapsed), os.path.join(outdir, name)))

    phases = []
    for (ord_, width), frames in sorted(buckets.items()):
        content, distincts, domshares, errors = 0, [], [], 0
        for _, path in frames:
            try:
                s = stats(path)
            except Exception:                          # partial/unreadable capture
                errors += 1
                continue
            content += bool(s["content"])
            distincts.append(s["distinct"])
            domshares.append(s["domshare"])
        n = len(distincts)
        phases.append({
            "ord": ord_, "width": width,
            "t_first": frames[0][0], "t_last": frames[-1][0],
            "frames": n, "unreadable": errors,
            "content_frames": content,
            "content_fraction": round(content / n, 3) if n else 0.0,
            "median_distinct": int(statistics.median(distincts)) if distincts else 0,
            "median_domshare": round(statistics.median(domshares), 3) if domshares else 1.0,
            "judged": n >= MIN_FRAMES,
        })
    return phases


def compare(cur, base):
    """Diff against a baseline verdict. Returns a list of (level, message)."""
    issues = []
    bo, co = base.get("outcome", {}), cur["outcome"]
    if bo.get("status") == "completed" and co["status"] == "died":
        issues.append(("FAIL", f"process died at {co['elapsed']:.1f}s; "
                               f"baseline completed {bo.get('elapsed', 0):.1f}s"))
    elif co["status"] == "died" and bo.get("status") == "died":
        if co["elapsed"] < bo.get("elapsed", 0) * 0.75:
            issues.append(("WARN", f"died earlier than baseline "
                                   f"({co['elapsed']:.1f}s vs {bo['elapsed']:.1f}s)"))

    # Phase-reached checks come from the game's own [phase] log lines, not from
    # the frames, so they work in log-only mode where capture is unavailable.
    cur_widths = {t["width"] for t in cur["phase_transitions"] if t["width"]}
    for w in sorted({t["width"] for t in base.get("phase_transitions", [])
                     if t["width"]}):
        if w not in cur_widths:
            issues.append(("FAIL", f"VI width {w} phase never reached "
                                   f"(baseline reached it)"))
    btmap = {t["width"]: t["t"] for t in base.get("phase_transitions", [])}
    for t in cur["phase_transitions"]:
        bt = btmap.get(t["width"])
        if bt and bt > 5.0 and t["t"] > bt * 2.0:
            issues.append(("WARN", f"width {t['width']} reached at {t['t']:.1f}s "
                                   f"vs {bt:.1f}s in baseline"))

    if base.get("visual") == "ok" and cur["visual"] != "ok":
        issues.append(("INFO", "visual half not compared: window capture "
                               "unavailable in this run"))

    bmap = {(p["ord"], p["width"]): p for p in base.get("phases", [])}
    for p in cur["phases"]:
        b = bmap.get((p["ord"], p["width"]))
        if not b or not (p["judged"] and b.get("judged")):
            continue
        d = p["content_fraction"] - b["content_fraction"]
        if d < -CONTENT_DROP_FAIL:
            issues.append(("FAIL", f"p{p['ord']:02d} w{p['width']}: content "
                                   f"{b['content_fraction']:.2f} -> "
                                   f"{p['content_fraction']:.2f}"))
        elif d > CONTENT_DROP_FAIL:
            issues.append(("INFO", f"p{p['ord']:02d} w{p['width']}: content "
                                   f"improved {b['content_fraction']:.2f} -> "
                                   f"{p['content_fraction']:.2f}"))
        if b["median_distinct"] and \
                p["median_distinct"] < b["median_distinct"] * DISTINCT_DROP_FAIL:
            issues.append(("FAIL", f"p{p['ord']:02d} w{p['width']}: detail "
                                   f"{b['median_distinct']} -> "
                                   f"{p['median_distinct']} distinct colours"))

    bc, cc = base.get("counters", {}), cur["counters"]
    new_missing = set(cc["missing_func_addrs"]) - set(bc.get("missing_func_addrs", []))
    if new_missing:
        issues.append(("FAIL", "new unmapped overlay symbols: "
                               + " ".join(sorted(new_missing))))
    for tag, n in cc["aborts"].items():
        if n > bc.get("aborts", {}).get(tag, 0):
            issues.append(("FAIL", f"{tag} count {bc.get('aborts', {}).get(tag, 0)}"
                                   f" -> {n}"))
    if cc["defer_drop_total"] > max(1, bc.get("defer_drop_total", 0)) * 2:
        issues.append(("WARN", f"defer-drop {bc.get('defer_drop_total', 0)}"
                               f" -> {cc['defer_drop_total']}"))
    return issues


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit("usage: regress_score.py <outdir> [--baseline v.json] [--label n]")
    outdir = args[0]
    baseline_path = label = None
    for i, a in enumerate(args):
        if a == "--baseline" and i + 1 < len(args):
            baseline_path = args[i + 1]
        if a == "--label" and i + 1 < len(args):
            label = args[i + 1]
    if not os.path.isdir(outdir):
        sys.exit(f"regress_score: no such directory: {outdir}")

    counters, transitions = read_log(os.path.join(outdir, "run.log"))
    outcome = read_outcome(os.path.join(outdir, "outcome.txt"))
    phases = score_phases(outdir)
    # Zero frames is a valid mode, not an error: window capture needs Screen
    # Recording permission that a headless/agent shell does not have, while the
    # log half of the verdict works anywhere. Say which half is present rather
    # than failing, so an unattended loop still gets crash/phase/counter gating.
    visual = "ok" if phases else "unavailable"
    if not phases and not transitions:
        sys.exit("regress_score: no frames and no parsable run.log -- nothing to score")

    env = {}
    envfile = os.path.join(outdir, "env.txt")
    if os.path.exists(envfile):
        for line in open(envfile):
            if line.startswith("ROGUESQ_") and "=" in line:
                k, v = line.strip().split("=", 1)
                env[k] = v

    verdict = {
        "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "label": label or os.path.basename(os.path.abspath(outdir)),
        "outdir": os.path.abspath(outdir),
        "env": env,
        "outcome": outcome,
        "visual": visual,
        "counters": counters,
        "phase_transitions": transitions,
        "phases": phases,
    }

    # Run-quality checks run with or without a baseline: a run whose input never
    # landed is not comparable to anything, and saying so is the whole point.
    issues = check_input_landed(envfile, transitions)
    if baseline_path:
        if not os.path.exists(baseline_path):
            # Never lose a completed run's verdict to a bad baseline path.
            issues.append(("WARN", f"baseline not found, not compared: "
                                   f"{baseline_path}"))
            baseline_path = None
        else:
            issues += compare(verdict, json.load(open(baseline_path)))
    verdict["baseline"] = os.path.abspath(baseline_path) if baseline_path else None
    verdict["issues"] = [{"level": lv, "message": m} for lv, m in issues]
    verdict["verdict"] = "FAIL" if any(lv == "FAIL" for lv, _ in issues) else "PASS"

    with open(os.path.join(outdir, "verdict.json"), "w") as fh:
        json.dump(verdict, fh, indent=2)

    print(f"\n=== {verdict['label']} === {outcome['status']} at "
          f"{outcome['elapsed']:.1f}s, {outcome['frames']} frames")
    if env:
        print("env: " + " ".join(f"{k}={v}" for k, v in sorted(env.items())))
    if not phases:
        print("\nvisual: UNAVAILABLE (no frames captured) -- log-only verdict.\n"
              "  window capture needs Screen Recording permission; run from a\n"
              "  terminal that has it to get per-phase content scoring.")
    print(f"\n{'phase':>7} {'width':>6} {'t':>12} {'frames':>7} {'content':>9} "
          f"{'distinct':>9}  note")
    for p in phases:
        note = "" if p["judged"] else f"insufficient (<{MIN_FRAMES} frames)"
        if p["unreadable"]:
            note += f" {p['unreadable']} unreadable"
        print(f"{'p%02d' % p['ord']:>7} {p['width']:>6} "
              f"{'%.1f-%.1f' % (p['t_first'], p['t_last']):>12} "
              f"{p['frames']:>7} "
              f"{'%d/%d' % (p['content_frames'], p['frames']):>9} "
              f"{p['median_distinct']:>9}  {note}")

    print(f"\ntransitions: " + (", ".join(
        f"{t['t']:.1f}s->w{t['width']}" for t in transitions) or "none logged"))
    print(f"missing-func: {counters['missing_func_distinct']} distinct  "
          f"defer-drop: {counters['defer_drop_total']}  "
          f"defer-commit: {counters['defer_commit_total']}  "
          f"aborts: {counters['aborts'] or 'none'}")

    if issues or baseline_path:
        header = (f"vs baseline {os.path.basename(baseline_path)}:"
                  if baseline_path else "run-quality checks:")
        print(f"\n{header}")
        for lv, m in issues or [("INFO", "no differences above threshold")]:
            print(f"  {lv:5s} {m}")
    print(f"\nVERDICT: {verdict['verdict']}   -> {outdir}/verdict.json")
    return 1 if verdict["verdict"] == "FAIL" else 0


if __name__ == "__main__":
    sys.exit(main())
