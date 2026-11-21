#!/usr/bin/env python3
"""s7764: score the OWNER-REVIEW-QUEUE in-flight toggles from one 3-arm forced-level flight (tools/s7764_inflight_toggles.zsh).

Arms (L1, dd4, 21:9, FPS60, autopilot firing + stick left/right):
  def  every fix at its default
  off  RUMBLE=0 W_CLAMP=0 DD_FARMAX=0 HORIZON_SKYFILL=0 STICK_GATE=0 M5_B40_VALUE=1 (each row's "old"/opt-in switch)
  tog  W_CLAMP=tog HORIZON_SKYFILL=tog (same-run odd/even 24 MHz seconds) + RUMBLE_SCALE=0.5
Per toggle the default arm must show the fix's own counter firing (positive control), and the switch arm must differ the
way the row says. rc 0 = every toggle H-works, 1 = a toggle is H-broken, 2 = a positive control did not fire (no verdict).
usage: s7764_inflight_toggle_check.py <runs dir>
"""
import re, sys, os

D = sys.argv[1] if len(sys.argv) > 1 else "scratch/s7764/runs"


def log(arm):
    p = os.path.join(D, "log_%s.txt" % arm)
    return open(p, errors="replace").read() if os.path.exists(p) else ""


def rumble(t):
    s = re.findall(r"\[rumble\] sum on=(\d) scale=([\d.]+) motor_calls=(\d+) on_edges=(\d+) max_duty=([\d.]+) sdl_on=(\d+).*?vpad=(\d+) vpad_nz=(\d+)", t)
    hi = [int(x) for x in re.findall(r"\[rumble-vpad\] n=\d+ lo=\d+ hi=(\d+)", t)]
    if not s:
        return None
    last = s[-1]
    return dict(on=int(last[0]), scale=float(last[1]), motor=int(last[2]), edges=int(last[3]), sdl_on=int(last[5]),
                vpad_nz=int(last[7]), vpad_hi_max=max(hi) if hi else 0)


def wsheet(t):
    out = {0: 0, 1: 0}
    last = {}
    for sec, blk, *v in re.findall(r"\[wsheet\] sec=(\d+) blk=(\d) lt20=(\d+) 20_40=(\d+) 40_60=(\d+) 60_100=(\d+) 100_200=(\d+) ge200=(\d+) dropped=(\d+)", t):
        last[int(blk)] = sum(int(x) for x in v[:6])  # cumulative counters: keep the last line per block
    out.update(last)
    return out


def skyfill(t):
    rows = [(int(s), int(n), int(m)) for s, n, m in re.findall(r"\[s7136\] sec (\d+) skyfill (\d+) mode=(\d)", t)]
    odd = sum(n for s, n, m in rows if s & 1); even = sum(n for s, n, m in rows if not s & 1)
    return dict(lines=len(rows), odd=odd, even=even)


def farmax(t):
    m = re.search(r"\[s7310\] far max ([\d.e+]+)", t)
    caps = [float(x) for x in re.findall(r"\[pnormcap\] far [\d.e+-]+ x[\d.e+-]+ -> ([\d.e+-]+)", t)]
    return dict(max=float(m.group(1)) if m else None, cap_max=max(caps) if caps else None, ncap=len(caps))


def stick(t):
    on = re.search(r"\[stick-gate\] on=(\d)", t)
    smp = [(float(a), int(b)) for a, b in re.findall(r"\[stick-gate\] sample on=\d in=(-?[\d.]+),-?[\d.]+ out_counts=(-?\d+),-?\d+", t)]
    full = [abs(c) for x, c in smp if abs(x) > 0.99]
    return dict(on=int(on.group(1)) if on else None, n=len(smp), full_max=max(full) if full else None)


def b40(t):
    rows = re.findall(r"\[m5-b40-read\] arm=(\w+) b40=(\d).*? value=0x([0-9A-F]{2})", t)
    return dict(n=len(rows), arm=sorted(set(r[0] for r in rows)), values=sorted(set(r[2] for r in rows)))


L = {a: log(a) for a in ("def", "off", "tog")}
if not all(L.values()):
    print("missing arm log(s):", [a for a, v in L.items() if not v]); sys.exit(2)
res, ctl_fail, broken = [], [], []


def row(name, ctl, works, detail):
    res.append("%-16s control=%s verdict=%s  %s" % (name, "PASS" if ctl else "FAIL", "H-works" if (ctl and works) else ("H-broken" if ctl else "n/a"), detail))
    if not ctl: ctl_fail.append(name)
    elif not works: broken.append(name)


r = {a: rumble(L[a]) for a in L}
d, o, g = r["def"], r["off"], r["tog"]
row("RUMBLE=0", bool(d and d["on"] == 1 and d["vpad_nz"] > 0),
    bool(o and o["on"] == 0 and o["vpad_nz"] == 0), "def %s | off %s" % (d, o))
row("RUMBLE_SCALE=.5", bool(d and d["vpad_hi_max"] > 0), bool(g and g["scale"] == 0.5 and 0 < g["vpad_hi_max"] < d["vpad_hi_max"]),
    "vpad hi max def %s tog %s" % (d and d["vpad_hi_max"], g and g["vpad_hi_max"]))
w = {a: wsheet(L[a]) for a in L}
row("W_CLAMP=0", w["def"][0] + w["def"][1] > 0, w["off"][0] + w["off"][1] == 0 and w["tog"][1] > 0 and w["tog"][0] == 0,
    "mixed-sign tris clamped def %s off %s tog(blk0 off/blk1 on) %s" % (w["def"], w["off"], w["tog"]))
s = {a: skyfill(L[a]) for a in L}
row("HORIZON_SKYFILL=0", s["def"]["odd"] + s["def"]["even"] > 0,
    s["off"]["lines"] == 0 and s["tog"]["odd"] > 0 and s["tog"]["even"] == 0, "def %s off %s tog %s" % (s["def"], s["off"], s["tog"]))
f = {a: farmax(L[a]) for a in L}
row("DD_FARMAX=0", f["def"]["max"] == 32767 and f["def"]["cap_max"] is not None and f["def"]["cap_max"] <= 32767,
    f["off"]["max"] == 0 and f["off"]["cap_max"] is not None and f["off"]["cap_max"] > 32767, "def %s off %s" % (f["def"], f["off"]))
k = {a: stick(L[a]) for a in L}
row("STICK_GATE=0", k["def"]["on"] == 1 and k["def"]["full_max"] is not None and k["def"]["full_max"] <= 86,
    k["off"]["on"] == 0 and k["off"]["full_max"] == 127, "def %s off %s" % (k["def"], k["off"]))
# B40 has no in-flight effect: its store happens at boot (reapplyDisplayMode). Scored from the b40 pair (s7764_inflight_toggles.zsh step 2,
# ROGUESQ_LOG_M5_B40_ROUTE=1): the b40-write event must fire in both arms (control) and store 0x00 default vs 0x01 with =1.
def b40w(arm):
    p = os.path.join(os.path.dirname(D.rstrip("/")), "b40", "log_%s.txt" % arm)
    t = open(p, errors="replace").read() if os.path.exists(p) else ""
    return sorted(set(re.findall(r"\[m5-b40-route\] arm=\w+ .*?edge=b40-write .*?b40_stored=0x([0-9A-F]{2})", t)))
b0, b1 = b40w("b0"), b40w("b1")
row("M5_B40_VALUE=1", bool(b0) and bool(b1), b0 == ["00"] and b1 == ["01"], "b40-write stored default %s, =1 %s" % (b0, b1))
print("\n".join(res))
print("controls_fail=%s broken=%s" % (",".join(ctl_fail) or "none", ",".join(broken) or "none"))
sys.exit(2 if ctl_fail else 1 if broken else 0)
